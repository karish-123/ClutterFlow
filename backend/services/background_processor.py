# backend/services/background_processor.py
import asyncio
import logging
from datetime import datetime
from typing import Optional, List
from uuid import UUID
import json

from services.llm_service import llm_service
from services.database import db_service
from models.schemas import (
    ProcessingQueueCreate, ProcessingQueueUpdate, TaskType, TaskStatus,
    DocumentSummaryCreate, DocumentClassificationCreate, SummaryType
)
from config.settings import settings

logger = logging.getLogger(__name__)

class BackgroundProcessor:
    def __init__(self):
        self.is_running = False
        self.max_concurrent_tasks = 3
        self.processing_tasks = set()
        
    async def add_task(self, document_id: UUID, task_type: TaskType, priority: int = 1, task_data: dict = None) -> bool:
        """Add a new task to the processing queue"""
        try:
            task_data = task_data or {}
            
            task = ProcessingQueueCreate(
                document_id=document_id,
                task_type=task_type,
                priority=priority,
                task_data=task_data
            )
            
            # Convert UUID to string for JSON serialization
            task_dict = task.model_dump()
            task_dict['document_id'] = str(task_dict['document_id'])
            
            # Use Supabase REST API to insert task
            result = db_service.supabase.table('processing_queue').insert(task_dict).execute()
            
            if result.data:
                logger.info(f"✅ Added {task_type} task for document {document_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to add task: {e}")
            return False
    
    async def get_pending_tasks(self, limit: int = 10) -> List[dict]:
        """Get pending tasks ordered by priority and creation time"""
        try:
            result = db_service.supabase.table('processing_queue')\
                .select("*")\
                .eq('status', 'pending')\
                .order('priority')\
                .order('created_at')\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Failed to get pending tasks: {e}")
            return []
    
    async def update_task_status(self, task_id: UUID, status: TaskStatus, 
                               error_message: str = None, 
                               started_at: datetime = None,
                               completed_at: datetime = None) -> bool:
        """Update task status in database"""
        try:
            update_data = {'status': status}
            
            if error_message:
                update_data['error_message'] = error_message
            if started_at:
                update_data['started_at'] = started_at.isoformat()
            if completed_at:
                update_data['completed_at'] = completed_at.isoformat()
            
            result = db_service.supabase.table('processing_queue')\
                .update(update_data)\
                .eq('id', str(task_id))\
                .execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"❌ Failed to update task status: {e}")
            return False
    
    async def process_summarization_task(self, task: dict) -> bool:
        """Process a summarization task"""
        try:
            document_id = UUID(task['document_id'])
            task_id = UUID(task['id'])
            
            logger.info(f"🔄 Processing summarization for document {document_id}")
            
            # Mark task as processing
            await self.update_task_status(task_id, TaskStatus.processing, started_at=datetime.utcnow())
            
            # Get extracted text
            extracted_text_result = db_service.supabase.table('extracted_text')\
                .select("raw_text")\
                .eq('document_id', str(document_id))\
                .execute()
            
            if not extracted_text_result.data:
                raise Exception("No extracted text found for document")
            
            raw_text = extracted_text_result.data[0]['raw_text']
            
            if not raw_text or len(raw_text.strip()) < 50:
                raise Exception("Insufficient text for summarization")
            
            # Get summary type from task data
            summary_type = task.get('task_data', {}).get('summary_type', 'brief')
            
            # Generate summary using LLM
            summary_result = await llm_service.summarize_text(raw_text, summary_type)
            
            # Save summary to database
            summary_data = DocumentSummaryCreate(
                document_id=document_id,
                summary_text=summary_result.content,
                summary_type=summary_type,
                model_used=summary_result.model_used,
                tokens_used=summary_result.tokens_used,
                processing_time=summary_result.processing_time
            )
            
            # Convert UUID to string for JSON serialization
            summary_dict = summary_data.model_dump()
            summary_dict['document_id'] = str(summary_dict['document_id'])
            
            db_result = db_service.supabase.table('document_summaries')\
                .insert(summary_dict)\
                .execute()
            
            if db_result.data:
                # Mark task as completed
                await self.update_task_status(task_id, TaskStatus.completed, completed_at=datetime.utcnow())
                logger.info(f"✅ Summarization completed for document {document_id}")
                return True
            else:
                raise Exception("Failed to save summary to database")
                
        except Exception as e:
            logger.error(f"❌ Summarization failed for document {document_id}: {e}")
            await self.update_task_status(task_id, TaskStatus.failed, error_message=str(e))
            return False
    
    async def process_classification_task(self, task: dict) -> bool:
        """Process a classification task"""
        try:
            document_id = UUID(task['document_id'])
            task_id = UUID(task['id'])
            
            logger.info(f"🔄 Processing classification for document {document_id}")
            
            # Mark task as processing
            await self.update_task_status(task_id, TaskStatus.processing, started_at=datetime.utcnow())
            
            # Get extracted text
            extracted_text_result = db_service.supabase.table('extracted_text')\
                .select("raw_text")\
                .eq('document_id', str(document_id))\
                .execute()
            
            if not extracted_text_result.data:
                raise Exception("No extracted text found for document")
            
            raw_text = extracted_text_result.data[0]['raw_text']
            
            if not raw_text or len(raw_text.strip()) < 20:
                raise Exception("Insufficient text for classification")
            
            # Generate classification using LLM
            classification_result = await llm_service.classify_topic(raw_text)
            
            # Extract classification data from LLM metadata
            metadata = classification_result.metadata
            
            # Save classification to database
            classification_data = DocumentClassificationCreate(
                document_id=document_id,
                primary_topic=metadata.get('primary_topic', 'unknown'),
                confidence=metadata.get('confidence', 0.5),
                category=metadata.get('category', 'other'),
                tags=metadata.get('tags', []),
                model_used=classification_result.model_used
            )
            
            # Convert UUID to string for JSON serialization
            classification_dict = classification_data.model_dump()
            classification_dict['document_id'] = str(classification_dict['document_id'])
            
            db_result = db_service.supabase.table('document_classifications')\
                .insert(classification_dict)\
                .execute()
            
            if db_result.data:
                # Mark task as completed
                await self.update_task_status(task_id, TaskStatus.completed, completed_at=datetime.utcnow())
                logger.info(f"✅ Classification completed for document {document_id}")
                return True
            else:
                raise Exception("Failed to save classification to database")
                
        except Exception as e:
            logger.error(f"❌ Classification failed for document {document_id}: {e}")
            await self.update_task_status(task_id, TaskStatus.failed, error_message=str(e))
            return False
    
    async def process_single_task(self, task: dict) -> bool:
        """Process a single task based on its type"""
        task_type = task['task_type']
        
        if task_type == 'summarize':
            return await self.process_summarization_task(task)
        elif task_type == 'classify':
            return await self.process_classification_task(task)
        else:
            logger.warning(f"⚠️ Unknown task type: {task_type}")
            return False
    
    async def process_pending_tasks(self):
        """Main processing loop - processes pending tasks"""
        if not settings.background_processing_enabled:
            logger.info("Background processing is disabled")
            return
        
        logger.info("🚀 Starting background task processing...")
        
        while self.is_running:
            try:
                # Get pending tasks
                pending_tasks = await self.get_pending_tasks(limit=self.max_concurrent_tasks)
                
                if not pending_tasks:
                    await asyncio.sleep(5)  # Wait 5 seconds before checking again
                    continue
                
                # Process tasks concurrently
                tasks_to_process = []
                for task in pending_tasks[:self.max_concurrent_tasks]:
                    if len(self.processing_tasks) < self.max_concurrent_tasks:
                        task_coroutine = self.process_single_task(task)
                        self.processing_tasks.add(task_coroutine)
                        tasks_to_process.append(task_coroutine)
                
                if tasks_to_process:
                    # Wait for tasks to complete
                    results = await asyncio.gather(*tasks_to_process, return_exceptions=True)
                    
                    # Remove completed tasks
                    for task_coroutine in tasks_to_process:
                        self.processing_tasks.discard(task_coroutine)
                
                await asyncio.sleep(2)  # Brief pause between batches
                
            except Exception as e:
                logger.error(f"❌ Error in processing loop: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def start(self):
        """Start the background processor"""
        if self.is_running:
            logger.warning("Background processor is already running")
            return
        
        # Check if LLM service is available
        if not await llm_service.health_check():
            logger.error("❌ LLM service not available. Background processing disabled.")
            return
        
        self.is_running = True
        logger.info("🚀 Background processor started")
        
        # Start processing loop
        await self.process_pending_tasks()
    
    async def stop(self):
        """Stop the background processor"""
        self.is_running = False
        
        # Wait for current tasks to complete
        if self.processing_tasks:
            logger.info("⏳ Waiting for current tasks to complete...")
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        
        logger.info("🛑 Background processor stopped")
    
    async def queue_document_processing(self, document_id: UUID) -> bool:
        """Queue all processing tasks for a document"""
        success = True
        
        # Add summarization task
        if settings.enable_summarization:
            task_added = await self.add_task(
                document_id, 
                TaskType.summarize, 
                priority=1,
                task_data={'summary_type': 'brief'}
            )
            success = success and task_added
        
        # Add classification task
        if settings.enable_classification:
            task_added = await self.add_task(
                document_id, 
                TaskType.classify, 
                priority=2
            )
            success = success and task_added
        
        return success

# Global background processor instance
background_processor = BackgroundProcessor()