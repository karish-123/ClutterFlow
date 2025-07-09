# text_extractor.py

import os
import cv2
import numpy as np
import pytesseract
import fitz  
from PIL import Image
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import magic
from pdf2image import convert_from_path
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExtractionResult:
    text: str
    confidence: float
    method_used: str
    page_count: int
    file_type: str
    processing_time: float
    metadata: Dict

class TextExtractor:
    def __init__(self, tesseract_cmd: Optional[str] = None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        elif os.name == 'nt':
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        self.ocr_config = '--oem 3 --psm 6'

    def extract_text(self, file_path: str) -> ExtractionResult:
        start_time = time.time()
        try:
            file_type = self._detect_file_type(file_path)
            if file_type == 'pdf':
                result = self._extract_from_pdf(file_path)
            elif file_type == 'image':
                result = self._extract_from_image(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            result.processing_time = time.time() - start_time
            result.file_type = file_type
            return result
        except Exception as e:
            return ExtractionResult(
                text="",
                confidence=0.0,
                method_used="error",
                page_count=0,
                file_type="unknown",
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            )

    def _detect_file_type(self, file_path: str) -> str:
        try:
            mime_type = magic.from_file(file_path, mime=True)
            if 'pdf' in mime_type:
                return 'pdf'
            elif 'image' in mime_type:
                return 'image'
            else:
                return 'unknown'
        except:
            ext = Path(file_path).suffix.lower()
            return 'pdf' if ext == '.pdf' else 'image' if ext in ['.png', '.jpg', '.jpeg'] else 'unknown'

    def _extract_from_pdf(self, file_path: str) -> ExtractionResult:
        try:
            doc = fitz.open(file_path)
            text_content = ""
            for page in doc:
                text_content += page.get_text() + "\n"
            doc.close()

            if len(text_content.strip()) > 50:
                return ExtractionResult(
                    text=text_content.strip(),
                    confidence=0.95,
                    method_used="direct_pdf_extraction",
                    page_count=len(doc),
                    file_type="pdf",
                    processing_time=0,
                    metadata={}
                )
        except Exception:
            pass
        return self._ocr_pdf_pages(file_path)

    def _ocr_pdf_pages(self, file_path: str) -> ExtractionResult:
        pages = convert_from_path(file_path, dpi=300)
        all_text = ""
        total_conf = 0
        count = 0
        for page in pages:
            img = np.array(page)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ocr = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            text, conf = self._extract_text_with_confidence(ocr)
            all_text += text + "\n"
            total_conf += conf
            count += 1
        avg_conf = total_conf / count if count > 0 else 0
        return ExtractionResult(
            text=all_text.strip(),
            confidence=avg_conf,
            method_used="pdf_ocr",
            page_count=len(pages),
            file_type="pdf",
            processing_time=0,
            metadata={}
        )

    def _extract_from_image(self, file_path: str) -> ExtractionResult:
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError("Failed to load image.")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ocr = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        text, conf = self._extract_text_with_confidence(ocr)
        return ExtractionResult(
            text=text,
            confidence=conf,
            method_used="image_ocr",
            page_count=1,
            file_type="image",
            processing_time=0,
            metadata={}
        )

    def _extract_text_with_confidence(self, ocr_data: Dict) -> Tuple[str, float]:
        texts = []
        confs = []
        for i, conf in enumerate(ocr_data['conf']):
            if conf != '-1':
                c = int(conf)
                if c > 30:
                    txt = ocr_data['text'][i].strip()
                    if txt:
                        texts.append(txt)
                        confs.append(c)
        full_text = ' '.join(texts)
        avg_conf = sum(confs) / len(confs) if confs else 0
        return full_text, avg_conf / 100
