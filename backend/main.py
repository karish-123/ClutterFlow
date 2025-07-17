# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
from pathlib import Path
import logging
from typing import Optional
from uuid import UUID
from typing import Optional, List  # Add List to your existing typing imports
# Imports
from services.text_extractor import TextExtractor, ExtractionResult
from services.database import db_service
from services.background_processor import background_processor
from services.subject_service import subject_service
from services.file_storage import file_storage
from models.schemas import (
    ExtractionResponse, DocumentCreate, ExtractedTextCreate,
    DocumentListResponse, DocumentDetailResponse, DocumentSummaryResponse,
    DocumentClassificationResponse, SummarizeRequest, ClassifyRequest, TaskStatus,
    SubjectCreate, SubjectUpdate, SubjectResponse, SubjectWithStats,
    TaskType  # Add this missing import
)
from config.settings import settings

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ClutterFlow API",
    version=settings.api_version,
    description="AI-powered document processing and organization system"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

text_extractor = TextExtractor()

SUPPORTED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg'}

# Background task to start processor
async def startup_background_processor():
    """Start background processor on app startup"""
    import asyncio
    
    async def run_processor():
        try:
            await background_processor.start()
        except Exception as e:
            logger.error(f"Background processor error: {e}")
    
    # Start processor in background
    asyncio.create_task(run_processor())

# Add startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🌊 Starting ClutterFlow API...")
    await startup_background_processor()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down ClutterFlow API...")
    await background_processor.stop()

@app.get("/")
async def health_check():
    return {
        "status": "running", 
        "message": "Digital Clutter Cleaner API is operational",
        "version": settings.api_version
    }

@app.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of documents to return")
):
    """List all processed documents"""
    documents, total = await db_service.list_documents(skip=skip, limit=limit)
    return DocumentListResponse(
        documents=documents,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )

@app.get("/documents/{document_id}", response_model=DocumentDetailResponse)
async def get_document(document_id: UUID):
    """Get document details with extracted text"""
    document, extracted_text = await db_service.get_document_with_text(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentDetailResponse(
        document=document,
        extracted_text=extracted_text
    )

@app.delete("/documents/{document_id}")
async def delete_document(document_id: UUID):
    """Delete a document and its extracted text"""
    success = await db_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document deleted successfully"}

@app.get("/documents/{document_id}/summary")
async def get_document_summary(document_id: UUID):
    """Get the summary for a document"""
    try:
        result = db_service.supabase.table('document_summaries')\
            .select("*")\
            .eq('document_id', str(document_id))\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Summary not found")
        
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{document_id}/classification")
async def get_document_classification(document_id: UUID):
    """Get the classification for a document"""
    try:
        result = db_service.supabase.table('document_classifications')\
            .select("*")\
            .eq('document_id', str(document_id))\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Classification not found")
        
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/{document_id}/summarize")
async def trigger_summarization(document_id: UUID, request: SummarizeRequest = SummarizeRequest()):
    """Manually trigger summarization for a document"""
    try:
        # Check if document exists
        document = await db_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Add summarization task
        success = await background_processor.add_task(
            document_id,
            TaskType.summarize,
            priority=1,
            task_data={'summary_type': request.summary_type}
        )
        
        if success:
            return {"message": "Summarization task queued", "document_id": document_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to queue summarization task")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/{document_id}/classify")
async def trigger_classification(document_id: UUID, request: ClassifyRequest = ClassifyRequest()):
    """Manually trigger classification for a document"""
    try:
        # Check if document exists
        document = await db_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Add classification task
        success = await background_processor.add_task(
            document_id,
            TaskType.classify,
            priority=1,
            task_data={'categories': request.categories}
        )
        
        if success:
            return {"message": "Classification task queued", "document_id": document_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to queue classification task")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks")
async def get_processing_tasks(
    status: Optional[str] = Query(None, description="Filter by task status"),
    limit: int = Query(20, ge=1, le=100)
):
    """Get processing tasks"""
    try:
        query = db_service.supabase.table('processing_queue').select("*")
        
        if status:
            query = query.eq('status', status)
        
        result = query.order('created_at', desc=True).limit(limit).execute()
        
        return {
            "tasks": result.data if result.data else [],
            "total": len(result.data) if result.data else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/overview")
async def get_analytics_overview():
    """Get processing analytics and statistics"""
    try:
        # Get document counts
        doc_result = db_service.supabase.table('documents').select("status", count="exact").execute()
        total_documents = doc_result.count if doc_result.count else 0
        
        # Get processing task counts
        task_result = db_service.supabase.table('processing_queue').select("status", count="exact").execute()
        
        # Get topic distribution
        topic_result = db_service.supabase.table('document_classifications')\
            .select("category")\
            .execute()
        
        # Process topic distribution
        topic_counts = {}
        if topic_result.data:
            for item in topic_result.data:
                category = item.get('category', 'unknown')
                topic_counts[category] = topic_counts.get(category, 0) + 1
        
        return {
            "total_documents": total_documents,
            "processing_stats": {
                "total_tasks": task_result.count if task_result.count else 0,
            },
            "topic_distribution": [
                {"topic": topic, "count": count, "percentage": (count/total_documents)*100 if total_documents > 0 else 0}
                for topic, count in topic_counts.items()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def validate_file(file: UploadFile):
    ext = Path(file.filename).suffix.lower()
    return ext in SUPPORTED_EXTENSIONS

async def save_temp_file(file: UploadFile) -> str:
    content = await file.read()
    if len(content) > settings.max_file_size:
        raise HTTPException(status_code=413, detail="File too large")
    
    ext = Path(file.filename).suffix
    path = Path(settings.temp_dir)
    path.mkdir(exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_path = path / f"{file_id}{ext}"
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    return str(file_path)

def cleanup_file(path: str):
    try:
        os.remove(path)
        logger.info(f"Cleaned up temp file: {path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup file {path}: {e}")
        
async def save_temp_file_from_content(content: bytes, filename: str) -> str:
    """Save file content to temporary file for processing"""
    ext = Path(filename).suffix
    path = Path(settings.temp_dir)
    path.mkdir(exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_path = path / f"{file_id}{ext}"
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    return str(file_path)

@app.post("/extract", response_model=ExtractionResponse)
async def extract(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Extract text from uploaded document and save to database + storage"""
    if not validate_file(file):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    logger.info(f"Processing file: {file.filename}")
    
    try:
        # Read file content once
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > settings.max_file_size:
            raise HTTPException(status_code=413, detail="File too large")
        
        logger.info(f"📊 File size: {file_size} bytes")
        
        # Create document record first
        document_data = DocumentCreate(
            filename=file.filename,
            file_type=Path(file.filename).suffix.lower(),
            file_size=file_size
        )
        
        document = await db_service.create_document(document_data)
        if not document:
            raise HTTPException(status_code=500, detail="Failed to create document record")
        
        logger.info(f"📄 Created document: {document.id}")
        
        # Update status to processing
        await db_service.update_document_status(document.id, "processing")
        
        # Reset file pointer for storage
        await file.seek(0)
        
        # Save file to Supabase Storage
        storage_result = await file_storage.save_document(file, str(document.id))
        
        logger.info(f"💾 Storage result: {storage_result}")
        
        if not storage_result.get("success"):
            raise HTTPException(
                status_code=500, 
                detail=f"File storage failed: {storage_result.get('error', 'Unknown error')}"
            )
        
        # Update document with storage info
        await db_service.update_document(document.id, {
            "storage_url": storage_result["storage_url"],
            "storage_path": storage_result["storage_path"]
        })
        
        # Save file temporarily for text extraction
        temp_file_path = await save_temp_file_from_content(file_content, file.filename)
        
        try:
            # Extract text from temporary file
            result = text_extractor.extract_text(temp_file_path)
            
            # Save extracted text
            text_data = ExtractedTextCreate(
                document_id=document.id,
                raw_text=result.text,
                confidence=result.confidence,
                method_used=result.method_used,
                page_count=result.page_count,
                processing_time=result.processing_time,
                extraction_metadata=result.metadata
            )
            
            extracted_text = await db_service.create_extracted_text(text_data)
            
            # Update status to completed
            await db_service.update_document_status(document.id, "completed")
            
            # Queue background LLM processing
            logger.info(f"🔄 Queuing LLM processing for document {document.id}")
            await background_processor.queue_document_processing(document.id)
            
        finally:
            # Clean up temporary file
            cleanup_file(temp_file_path)
        
        logger.info(f"✅ Successfully processed {file.filename} with document ID: {document.id}")
        
        return ExtractionResponse(
            success=True,
            document=document,
            extracted_text=extracted_text
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing file {file.filename}: {str(e)}")
        
        # Update status to failed if document was created
        if 'document' in locals() and document:
            await db_service.update_document_status(document.id, "failed")
        
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")



# Subject Management Endpoints
@app.post("/subjects", response_model=SubjectResponse)
async def create_subject(subject: SubjectCreate):
    """Create a new subject"""
    try:
        result = await subject_service.create_subject(subject)
        if result:
            return result
        raise HTTPException(status_code=400, detail="Failed to create subject")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/subjects", response_model=List[SubjectWithStats])
async def get_subjects(include_stats: bool = Query(False, description="Include document counts and stats")):
    """Get all active subjects"""
    try:
        subjects = await subject_service.get_all_subjects(include_stats=include_stats)
        return subjects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/subjects/{subject_id}", response_model=SubjectResponse)
async def get_subject(subject_id: UUID):
    """Get a specific subject by ID"""
    try:
        subject = await subject_service.get_subject_by_id(subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        return subject
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/subjects/{subject_id}", response_model=SubjectResponse)
async def update_subject(subject_id: UUID, subject: SubjectUpdate):
    """Update a subject"""
    try:
        result = await subject_service.update_subject(subject_id, subject)
        if not result:
            raise HTTPException(status_code=404, detail="Subject not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/subjects/{subject_id}")
async def delete_subject(subject_id: UUID, reassign_to: Optional[UUID] = Query(None)):
    """Delete a subject and optionally reassign documents"""
    try:
        success = await subject_service.delete_subject(subject_id, reassign_to)
        if not success:
            raise HTTPException(status_code=404, detail="Subject not found")
        return {"message": "Subject deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/subjects/{subject_id}/documents")
async def get_subject_documents(subject_id: UUID, limit: int = Query(50, ge=1, le=100)):
    """Get all documents for a specific subject"""
    try:
        documents = await subject_service.get_subject_documents(subject_id, limit)
        return {
            "subject_id": subject_id,
            "documents": documents,
            "total": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/{document_id}/assign-subject")
async def assign_document_to_subject(
    document_id: UUID, 
    subject_id: UUID = Query(..., description="Subject ID to assign to"),
    confidence: float = Query(1.0, ge=0.0, le=1.0, description="Assignment confidence"),
    auto_assigned: bool = Query(False, description="Was this auto-assigned by AI?")
):
    """Manually assign a document to a subject"""
    try:
        success = await subject_service.assign_document_to_subject(
            document_id, subject_id, confidence, auto_assigned
        )
        if success:
            return {"message": "Document assigned to subject successfully"}
        raise HTTPException(status_code=500, detail="Failed to assign document")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/unclassified")
async def get_unclassified_documents(limit: int = Query(20, ge=1, le=100)):
    """Get documents that haven't been assigned to any subject"""
    try:
        documents = await subject_service.get_unclassified_documents(limit)
        return {
            "documents": documents,
            "total": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/{document_id}/suggest-subject")
async def suggest_subject_for_document(document_id: UUID):
    """Get AI suggestion for document subject assignment"""
    try:
        suggestion = await subject_service.suggest_subject_for_document(document_id)
        if suggestion:
            return suggestion
        return {"message": "No suitable subject found", "suggestion": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced analytics with subject information
@app.get("/analytics/subjects")
async def get_subject_analytics():
    """Get analytics about subject distribution and usage"""
    try:
        subjects = await subject_service.get_all_subjects(include_stats=True)
        
        # Calculate analytics
        total_documents = sum(s.get('document_count', 0) for s in subjects)
        active_subjects = len([s for s in subjects if s.get('document_count', 0) > 0])
        
        # Top subjects by document count
        top_subjects = sorted(subjects, key=lambda x: x.get('document_count', 0), reverse=True)[:5]
        
        return {
            "total_subjects": len(subjects),
            "active_subjects": active_subjects,
            "total_documents": total_documents,
            "top_subjects": top_subjects,
            "subject_distribution": [
                {
                    "subject_name": s.get('subject_name'),
                    "document_count": s.get('document_count', 0),
                    "percentage": (s.get('document_count', 0) / total_documents * 100) if total_documents > 0 else 0
                }
                for s in subjects if s.get('document_count', 0) > 0
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/documents/{document_id}/view")
async def view_document(document_id: UUID):
    """View document in browser"""
    try:
        # Get document info
        document = await db_service.get_document(document_id)
        if not document or not document.storage_path:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get signed URL for secure access
        signed_url = file_storage.get_signed_url(document.storage_path, expires_in=3600)
        
        if not signed_url:
            raise HTTPException(status_code=500, detail="Could not generate file access URL")
        
        # Return redirect to signed URL
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=signed_url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error viewing document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to access file")

@app.get("/documents/{document_id}/download")
async def download_document(document_id: UUID):
    """Download document file"""
    try:
        # Get document info
        document = await db_service.get_document(document_id)
        if not document or not document.storage_path:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get signed URL for download
        signed_url = file_storage.get_signed_url(document.storage_path, expires_in=300)  # 5 minutes
        
        if not signed_url:
            raise HTTPException(status_code=500, detail="Could not generate download URL")
        
        return {"download_url": signed_url, "filename": document.filename}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error downloading document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Download failed")

@app.get("/storage/stats")
async def get_storage_stats():
    """Get storage usage statistics"""
    try:
        stats = file_storage.get_storage_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get storage stats: {str(e)}")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
