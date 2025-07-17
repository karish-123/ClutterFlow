# backend/services/subject_service.py
import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from services.database import db_service
from models.schemas import SubjectCreate, SubjectUpdate, SubjectResponse, SubjectWithStats

logger = logging.getLogger(__name__)

class SubjectService:
    def __init__(self):
        self.supabase = db_service.supabase
    
    async def create_subject(self, subject_data: SubjectCreate) -> Optional[Dict[str, Any]]:
        """Create a new subject"""
        try:
            # Convert to dict and handle arrays
            data = subject_data.model_dump()
            
            result = self.supabase.table('user_subjects').insert(data).execute()
            
            if result.data:
                logger.info(f"✅ Created subject: {subject_data.subject_name}")
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to create subject: {e}")
            return None
    
    async def get_all_subjects(self, include_stats: bool = False) -> List[Dict[str, Any]]:
        """Get all active subjects"""
        try:
            # Always use simple query - stats calculation in Python
            result = self.supabase.table('user_subjects')\
                .select("*")\
                .eq('is_active', True)\
                .order('subject_name')\
                .execute()
            
            subjects = result.data if result.data else []
            
            # Add stats if requested
            if include_stats:
                for subject in subjects:
                    try:
                        # Get document count for this subject
                        doc_count = self.supabase.table('document_classifications')\
                            .select("id", count="exact")\
                            .eq('subject_id', subject['id'])\
                            .execute()
                        
                        # Get latest document by querying from document_classifications and joining documents
                        latest_doc = self.supabase.table('document_classifications')\
                            .select("documents(upload_date, filename)")\
                            .eq('subject_id', subject['id'])\
                            .order('created_at', desc=True)\
                            .limit(1)\
                            .execute()
                        
                        subject['document_count'] = doc_count.count if doc_count.count else 0
                        
                        # Extract upload_date from nested structure
                        if latest_doc.data and latest_doc.data[0].get('documents'):
                            subject['latest_document'] = latest_doc.data[0]['documents']['upload_date']
                        else:
                            subject['latest_document'] = None
                            
                    except Exception as stat_error:
                        logger.warning(f"⚠️ Failed to get stats for subject {subject['id']}: {stat_error}")
                        # Set default values if stats fail
                        subject['document_count'] = 0
                        subject['latest_document'] = None
            
            return subjects
            
        except Exception as e:
            logger.error(f"❌ Failed to get subjects: {e}")
            return []
    
    async def get_subject_by_id(self, subject_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a specific subject by ID"""
        try:
            result = self.supabase.table('user_subjects')\
                .select("*")\
                .eq('id', str(subject_id))\
                .single()\
                .execute()
            
            return result.data if result.data else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get subject {subject_id}: {e}")
            return None
    
    async def update_subject(self, subject_id: UUID, subject_data: SubjectUpdate) -> Optional[Dict[str, Any]]:
        """Update a subject"""
        try:
            # Only include non-None values
            update_data = {k: v for k, v in subject_data.model_dump().items() if v is not None}
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            result = self.supabase.table('user_subjects')\
                .update(update_data)\
                .eq('id', str(subject_id))\
                .execute()
            
            if result.data:
                logger.info(f"✅ Updated subject: {subject_id}")
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to update subject {subject_id}: {e}")
            return None
    
    async def delete_subject(self, subject_id: UUID, reassign_to: Optional[UUID] = None) -> bool:
        """Delete a subject and optionally reassign documents"""
        try:
            # If reassigning documents, update them first
            if reassign_to:
                await self.reassign_documents(subject_id, reassign_to)
            
            # Soft delete by setting is_active to false
            result = self.supabase.table('user_subjects')\
                .update({'is_active': False, 'updated_at': datetime.utcnow().isoformat()})\
                .eq('id', str(subject_id))\
                .execute()
            
            if result.data:
                logger.info(f"✅ Deleted subject: {subject_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to delete subject {subject_id}: {e}")
            return False
    
    async def get_subject_documents(self, subject_id: UUID, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all documents for a specific subject"""
        try:
            # Query from document_classifications and join documents
            result = self.supabase.table('document_classifications')\
                .select("documents(*)")\
                .eq('subject_id', str(subject_id))\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            # Extract documents from the nested structure
            documents = []
            if result.data:
                for item in result.data:
                    if item.get('documents'):
                        documents.append(item['documents'])
            
            return documents
            
        except Exception as e:
            logger.error(f"❌ Failed to get documents for subject {subject_id}: {e}")
            # Fallback: try alternative query method
            try:
                logger.info(f"🔄 Trying alternative query for subject {subject_id}")
                
                # Get document IDs from classifications first
                classifications = self.supabase.table('document_classifications')\
                    .select("document_id")\
                    .eq('subject_id', str(subject_id))\
                    .execute()
                
                if not classifications.data:
                    return []
                
                document_ids = [item['document_id'] for item in classifications.data]
                
                # Get documents by IDs
                documents = self.supabase.table('documents')\
                    .select("*")\
                    .in_('id', document_ids)\
                    .order('upload_date', desc=True)\
                    .execute()
                
                return documents.data if documents.data else []
                
            except Exception as fallback_error:
                logger.error(f"❌ Fallback query also failed: {fallback_error}")
                return []
    
    async def assign_document_to_subject(self, document_id: UUID, subject_id: UUID, 
                                       confidence: float = 1.0, auto_assigned: bool = False) -> bool:
        """Assign a document to a subject"""
        try:
            # Check if classification already exists
            existing = self.supabase.table('document_classifications')\
                .select("id")\
                .eq('document_id', str(document_id))\
                .execute()
            
            classification_data = {
                'document_id': str(document_id),
                'subject_id': str(subject_id),
                'subject_confidence': confidence,
                'auto_assigned': auto_assigned,
                'primary_topic': 'manual_assignment',
                'category': 'other',
                'model_used': 'manual'
            }
            
            if existing.data:
                # Update existing classification
                result = self.supabase.table('document_classifications')\
                    .update(classification_data)\
                    .eq('document_id', str(document_id))\
                    .execute()
            else:
                # Create new classification
                result = self.supabase.table('document_classifications')\
                    .insert(classification_data)\
                    .execute()
            
            if result.data:
                logger.info(f"✅ Assigned document {document_id} to subject {subject_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to assign document to subject: {e}")
            return False
    
    async def reassign_documents(self, from_subject_id: UUID, to_subject_id: UUID) -> int:
        """Reassign all documents from one subject to another"""
        try:
            result = self.supabase.table('document_classifications')\
                .update({'subject_id': str(to_subject_id)})\
                .eq('subject_id', str(from_subject_id))\
                .execute()
            
            count = len(result.data) if result.data else 0
            logger.info(f"✅ Reassigned {count} documents from {from_subject_id} to {to_subject_id}")
            return count
            
        except Exception as e:
            logger.error(f"❌ Failed to reassign documents: {e}")
            return 0
    
    async def get_unclassified_documents(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get documents that haven't been assigned to any subject"""
        try:
            # First approach: get all document IDs that have classifications
            classified_docs = self.supabase.table('document_classifications')\
                .select("document_id")\
                .execute()
            
            classified_ids = [item['document_id'] for item in classified_docs.data] if classified_docs.data else []
            
            # Get documents that are NOT in the classified list
            if classified_ids:
                result = self.supabase.table('documents')\
                    .select("*")\
                    .not_('id', 'in', f"({','.join(classified_ids)})")\
                    .order('upload_date', desc=True)\
                    .limit(limit)\
                    .execute()
            else:
                # If no classifications exist, all documents are unclassified
                result = self.supabase.table('documents')\
                    .select("*")\
                    .order('upload_date', desc=True)\
                    .limit(limit)\
                    .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Failed to get unclassified documents: {e}")
            # Fallback: return all documents
            try:
                result = self.supabase.table('documents')\
                    .select("*")\
                    .order('upload_date', desc=True)\
                    .limit(limit)\
                    .execute()
                return result.data if result.data else []
            except:
                return []
    
    async def suggest_subject_for_document(self, document_id: UUID) -> Optional[Dict[str, Any]]:
        """Use LLM to suggest a subject for an unclassified document"""
        try:
            from services.llm_service import llm_service
            
            # Get document text
            extracted_text = self.supabase.table('extracted_text')\
                .select("raw_text")\
                .eq('document_id', str(document_id))\
                .execute()
            
            if not extracted_text.data:
                return None
            
            text = extracted_text.data[0]['raw_text']
            
            # Get available subjects
            subjects = await self.get_all_subjects()
            
            if not subjects:
                return None
            
            # Format subjects for LLM
            subjects_info = []
            for subject in subjects:
                keywords = ", ".join(subject.get('keywords', []))
                subjects_info.append(f"- {subject['subject_name']}: {keywords}")
            
            subjects_text = "\n".join(subjects_info)
            
            # Ask LLM for classification
            prompt = f"""
            Classify this document into one of the available subjects:
            
            Available Subjects:
            {subjects_text}
            
            Document text (first 1500 chars):
            {text[:1500]}...
            
            Return JSON with the best match:
            {{
                "subject_name": "exact subject name from list above",
                "confidence": 0.85,
                "reasoning": "brief explanation",
                "keywords_found": ["keyword1", "keyword2"]
            }}
            
            If no good match (confidence < 0.3), return {{"subject_name": null, "confidence": 0.0}}
            """
            
            result = await llm_service._generate_response(prompt)
            
            # Parse the JSON response
            import json
            import re
            
            json_match = re.search(r'\{.*\}', result.content, re.DOTALL)
            if json_match:
                suggestion = json.loads(json_match.group())
                
                # Find the subject ID
                if suggestion.get('subject_name'):
                    for subject in subjects:
                        if subject['subject_name'] == suggestion['subject_name']:
                            suggestion['subject_id'] = subject['id']
                            break
                
                return suggestion
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to suggest subject for document {document_id}: {e}")
            return None

# Global subject service instance
subject_service = SubjectService()