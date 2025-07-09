from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import json

from database import get_db
from models.document import Document, DocumentResponse, DocumentListResponse

router = APIRouter()

@router.get("/notes", response_model=DocumentListResponse)
async def get_notes(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get paginated list of processed documents"""
    
    query = db.query(Document)
    
    # Filter by status
    if status:
        query = query.filter(Document.status == status)
    
    # Search in filename or extracted text
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Document.original_filename.ilike(search_term)) |
            (Document.extracted_text.ilike(search_term)) |
            (Document.summary.ilike(search_term))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    documents = query.offset(offset).limit(per_page).all()
    
    return DocumentListResponse(
        documents=[DocumentResponse.from_orm(doc) for doc in documents],
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/notes/{document_id}", response_model=DocumentResponse)
async def get_note(document_id: int, db: Session = Depends(get_db)):
    """Get specific document details"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse.from_orm(document)

@router.get("/notes/{document_id}/text")
async def get_note_text(document_id: int, db: Session = Depends(get_db)):
    """Get extracted text for a document"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": document.id,
        "filename": document.original_filename,
        "extracted_text": document.extracted_text or "",
        "ocr_confidence": document.ocr_confidence,
        "status": document.status
    }

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get processing statistics"""
    
    total_docs = db.query(Document).count()
    completed_docs = db.query(Document).filter(Document.status == "completed").count()
    processing_docs = db.query(Document).filter(Document.status == "processing").count()
    error_docs = db.query(Document).filter(Document.status == "error").count()
    
    # Calculate average confidence
    completed_with_confidence = db.query(Document).filter(
        Document.status == "completed",
        Document.ocr_confidence.isnot(None)
    ).all()
    
    avg_confidence = 0
    if completed_with_confidence:
        avg_confidence = sum(doc.ocr_confidence for doc in completed_with_confidence) / len(completed_with_confidence)
    
    return {
        "total_documents": total_docs,
        "completed": completed_docs,
        "processing": processing_docs,
        "errors": error_docs,
        "success_rate": completed_docs / total_docs if total_docs > 0 else 0,
        "average_ocr_confidence": round(avg_confidence, 2) if avg_confidence else 0
    }