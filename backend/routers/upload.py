from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import uuid
from pathlib import Path
import magic

from database import get_db
from models.document import Document, DocumentCreate, DocumentResponse
from config import settings
from services.storage_service import save_uploaded_file
from services.ocr_service import process_document_async

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a file for processing"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_extension} not allowed. Allowed: {settings.allowed_extensions}"
        )
    
    # Check file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_file_size} bytes"
        )
    
    # Reset file pointer
    await file.seek(0)
    
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}{file_extension}"
        
        # Save file
        file_path = await save_uploaded_file(file, filename)
        
        # Detect MIME type
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(file_path)
        
        # Create database record
        db_document = Document(
            filename=filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            file_type=file_type,
            status="uploaded"
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Start async processing
        await process_document_async(db_document.id)
        
        return DocumentResponse.from_orm(db_document)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/upload/status/{document_id}")
async def get_upload_status(document_id: int, db: Session = Depends(get_db)):
    """Get upload and processing status"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": document.id,
        "filename": document.original_filename,
        "status": document.status,
        "created_at": document.created_at,
        "processed_at": document.processed_at,
        "error_message": document.error_message
    }

@router.delete("/upload/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document and its file"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Delete file from storage
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")