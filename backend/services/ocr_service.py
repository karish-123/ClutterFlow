import pytesseract
from PIL import Image
import pdf2image
import asyncio
import logging
from pathlib import Path
from typing import Tuple, Optional
import fitz  # PyMuPDF

from config import settings
from database import SessionLocal
from models.document import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Tesseract path if provided
if settings.tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

class OCRProcessor:
    """Handle OCR processing for different file types"""
    
    @staticmethod
    def extract_text_from_image(image_path: str) -> Tuple[str, float]:
        """Extract text from image using Tesseract OCR"""
        try:
            image = Image.open(image_path)
            
            # Get OCR data with confidence scores
            ocr_data = pytesseract.image_to_data(
                image, 
                lang=settings.ocr_language,
                output_type=pytesseract.Output.DICT
            )
            
            # Extract text and calculate average confidence
            text_parts = []
            confidences = []
            
            for i, word in enumerate(ocr_data['text']):
                if word.strip():  # Skip empty strings
                    text_parts.append(word)
                    confidences.append(ocr_data['conf'][i])
            
            extracted_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return extracted_text, avg_confidence / 100  # Convert to 0-1 scale
            
        except Exception as e:
            logger.error(f"Image OCR failed: {str(e)}")
            return "", 0.0
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> Tuple[str, float]:
        """Extract text from PDF - try direct extraction first, then OCR"""
        try:
            # First try direct text extraction
            doc = fitz.open(pdf_path)
            text_parts = []
            
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
            
            doc.close()
            
            if text_parts:
                # Direct extraction successful
                extracted_text = '\n'.join(text_parts)
                return extracted_text, 1.0  # High confidence for direct extraction
            
            # If no text found, use OCR
            return OCRProcessor._ocr_pdf_pages(pdf_path)
            
        except Exception as e:
            logger.error(f"PDF processing failed: {str(e)}")
            return "", 0.0
    
    @staticmethod
    def _ocr_pdf_pages(pdf_path: str) -> Tuple[str, float]:
        """OCR PDF pages when direct extraction fails"""
        try:
            # Convert PDF pages to images
            pages = pdf2image.convert_from_path(
                pdf_path,
                dpi=300,  # Higher DPI for better OCR
                fmt='PNG'
            )
            
            all_text = []
            all_confidences = []
            
            for i, page in enumerate(pages):
                logger.info(f"Processing PDF page {i+1}/{len(pages)}")
                
                # OCR each page
                ocr_data = pytesseract.image_to_data(
                    page,
                    lang=settings.ocr_language,
                    output_type=pytesseract.Output.DICT
                )
                
                # Extract text and confidence for this page
                page_text = []
                page_confidences = []
                
                for j, word in enumerate(ocr_data['text']):
                    if word.strip():
                        page_text.append(word)
                        page_confidences.append(ocr_data['conf'][j])
                
                if page_text:
                    all_text.append(' '.join(page_text))
                    all_confidences.extend(page_confidences)
            
            extracted_text = '\n'.join(all_text)
            avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
            
            return extracted_text, avg_confidence / 100
            
        except Exception as e:
            logger.error(f"PDF OCR failed: {str(e)}")
            return "", 0.0
    
    @staticmethod
    def process_document(file_path: str, file_type: str) -> Tuple[str, float]:
        """Main method to process any document type"""
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            logger.error(f"File not found: {file_path}")
            return "", 0.0
        
        # Determine processing method based on file type
        if file_type.startswith('image/') or file_path_obj.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            return OCRProcessor.extract_text_from_image(file_path)
        elif file_type == 'application/pdf' or file_path_obj.suffix.lower() == '.pdf':
            return OCRProcessor.extract_text_from_pdf(file_path)
        elif file_type.startswith('text/') or file_path_obj.suffix.lower() == '.txt':
            # For text files, just read directly
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content, 1.0
            except Exception as e:
                logger.error(f"Text file reading failed: {str(e)}")
                return "", 0.0
        else:
            logger.warning(f"Unsupported file type: {file_type}")
            return "", 0.0

async def process_document_async(document_id: int):
    """Async wrapper for document processing"""
    def process_sync():
        db = SessionLocal()
        try:
            # Get document from database
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                logger.error(f"Document {document_id} not found")
                return
            
            # Update status to processing
            document.status = "processing"
            db.commit()
            
            logger.info(f"Processing document {document_id}: {document.original_filename}")
            
            # Process with OCR
            extracted_text, confidence = OCRProcessor.process_document(
                document.file_path, 
                document.file_type
            )
            
            # Update document with results
            document.extracted_text = extracted_text
            document.ocr_confidence = confidence
            document.status = "completed" if extracted_text else "error"
            
            if not extracted_text:
                document.error_message = "No text could be extracted from the document"
            
            db.commit()
            logger.info(f"Document {document_id} processed successfully")
            
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            # Update document with error
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = "error"
                document.error_message = str(e)
                db.commit()
        finally:
            db.close()
    
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, process_sync)