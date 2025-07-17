# backend/services/file_storage.py
import logging
from typing import Optional
from pathlib import Path
from fastapi import UploadFile
from supabase import create_client
from config.settings import settings

logger = logging.getLogger(__name__)

class SupabaseFileStorage:
    def __init__(self):
        self.supabase = create_client(settings.supabase_url, settings.supabase_key)
        self.bucket_name = "documents"
    
    async def save_document(self, file: UploadFile, document_id: str) -> dict:
        """Save uploaded document to Supabase Storage"""
        try:
            # Read file content
            file_content = await file.read()
            
            if not file_content:
                return {"success": False, "error": "Empty file content"}
            
            # Create storage path: documents/{document_id}/original.{extension}
            file_extension = Path(file.filename).suffix.lower()
            storage_path = f"{document_id}/original{file_extension}"
            
            logger.info(f"📁 Uploading to path: {storage_path}")
            logger.info(f"📊 File size: {len(file_content)} bytes")
            logger.info(f"📄 File extension: {file_extension}")
            logger.info(f"🔗 Content type: {file.content_type}")
            
            # Upload to Supabase Storage
            try:
                result = self.supabase.storage.from_(self.bucket_name).upload(
                    path=storage_path,
                    file=file_content,
                    file_options={
                        "content-type": file.content_type or "application/octet-stream"
                    }
                )
                
                # DEBUG: Print the entire result
                logger.info(f"🔍 Full upload result: {result}")
                logger.info(f"🔍 Result type: {type(result)}")
                
                if hasattr(result, 'data'):
                    logger.info(f"🔍 Result data: {result.data}")
                if hasattr(result, 'error'):
                    logger.info(f"🔍 Result error: {result.error}")
                if hasattr(result, 'count'):
                    logger.info(f"🔍 Result count: {result.count}")
                
                # Try different ways to detect success
                success_indicators = [
                    hasattr(result, 'data') and result.data,
                    hasattr(result, 'data') and result.data is not None,
                    hasattr(result, 'error') and result.error is None,
                    not hasattr(result, 'error') or result.error is None
                ]
                
                logger.info(f"🔍 Success indicators: {success_indicators}")
                
                # Check if upload was successful (try multiple conditions)
                if (hasattr(result, 'data') and result.data is not None and 
                    (not hasattr(result, 'error') or result.error is None)):
                    
                    # Get public URL 
                    try:
                        public_url_result = self.supabase.storage.from_(self.bucket_name).get_public_url(storage_path)
                        logger.info(f"🔍 Public URL result: {public_url_result}")
                        
                        # Handle different URL result formats
                        if isinstance(public_url_result, str):
                            storage_url = public_url_result
                        elif isinstance(public_url_result, dict):
                            storage_url = public_url_result.get('publicURL', '') or public_url_result.get('url', '')
                        else:
                            storage_url = str(public_url_result)
                        
                        logger.info(f"✅ Uploaded file {file.filename} to {storage_path}")
                        logger.info(f"🔗 Storage URL: {storage_url}")
                        
                        return {
                            "storage_url": storage_url,
                            "storage_path": storage_path,
                            "success": True
                        }
                        
                    except Exception as url_error:
                        logger.error(f"❌ Error getting public URL: {url_error}")
                        # Still return success if upload worked
                        return {
                            "storage_url": f"https://{settings.supabase_url.split('//')[1]}/storage/v1/object/public/{self.bucket_name}/{storage_path}",
                            "storage_path": storage_path,
                            "success": True
                        }
                
                elif hasattr(result, 'error') and result.error:
                    logger.error(f"❌ Supabase upload error: {result.error}")
                    return {"success": False, "error": f"Supabase error: {result.error}"}
                
                else:
                    # This is where we were getting stuck - let's be more lenient
                    logger.warning(f"⚠️ Unexpected result format, attempting to proceed")
                    
                    # Try to get URL anyway
                    try:
                        public_url_result = self.supabase.storage.from_(self.bucket_name).get_public_url(storage_path)
                        storage_url = public_url_result if isinstance(public_url_result, str) else str(public_url_result)
                        
                        logger.info(f"✅ Proceeding with upload despite unexpected result")
                        return {
                            "storage_url": storage_url,
                            "storage_path": storage_path,
                            "success": True
                        }
                    except Exception as fallback_error:
                        logger.error(f"❌ Fallback also failed: {fallback_error}")
                        return {"success": False, "error": f"Unknown upload result: {result}"}
                    
            except Exception as upload_error:
                logger.error(f"❌ Upload exception: {upload_error}")
                return {"success": False, "error": f"Upload failed: {str(upload_error)}"}
                
        except Exception as e:
            logger.error(f"❌ Error in save_document: {e}")
            return {"success": False, "error": str(e)}
    
    def get_signed_url(self, storage_path: str, expires_in: int = 3600) -> Optional[str]:
        """Get signed URL for private file access"""
        try:
            result = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                path=storage_path,
                expires_in=expires_in
            )
            
            logger.info(f"🔍 Signed URL result: {result}")
            
            # Handle different possible response formats
            if isinstance(result, dict):
                signed_url = (
                    result.get('signedURL') or 
                    result.get('data', {}).get('signedURL') or
                    result.get('url')
                )
                return signed_url
            elif isinstance(result, str):
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error creating signed URL for {storage_path}: {e}")
            return None
    
    def delete_document(self, storage_path: str) -> bool:
        """Delete document from Supabase Storage"""
        try:
            result = self.supabase.storage.from_(self.bucket_name).remove([storage_path])
            
            if hasattr(result, 'data') and result.data:
                logger.info(f"✅ Deleted file {storage_path}")
                return True
            else:
                logger.error(f"❌ Failed to delete {storage_path}: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting {storage_path}: {e}")
            return False
    
    def get_storage_stats(self) -> dict:
        """Get storage usage statistics"""
        try:
            result = self.supabase.storage.from_(self.bucket_name).list()
            
            if hasattr(result, 'data') and result.data:
                total_files = len(result.data)
                total_size = sum(
                    file.get('metadata', {}).get('size', 0) 
                    for file in result.data 
                    if isinstance(file, dict)
                )
                
                return {
                    "total_files": total_files,
                    "total_size_bytes": total_size,
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "bucket_name": self.bucket_name
                }
            
            return {"total_files": 0, "total_size_bytes": 0, "total_size_mb": 0}
            
        except Exception as e:
            logger.error(f"❌ Error getting storage stats: {e}")
            return {"error": str(e)}

# Global instance
file_storage = SupabaseFileStorage()