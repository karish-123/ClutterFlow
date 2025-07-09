import os
import aiofiles
from pathlib import Path
from fastapi import UploadFile
from config import settings

async def save_uploaded_file(file: UploadFile, filename: str) -> Path:
    """Save uploaded file to disk"""
    
    # Create upload directory if it doesn't exist
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    
    # Full file path
    file_path = upload_path / filename
    
    # Save file asynchronously
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return file_path

def get_file_info(file_path: str) -> dict:
    """Get file information"""
    path = Path(file_path)
    
    if not path.exists():
        return {}
    
    stat = path.stat()
    
    return {
        "size": stat.st_size,
        "created": stat.st_ctime,
        "modified": stat.st_mtime,
        "extension": path.suffix.lower(),
        "name": path.name
    }

def cleanup_old_files(days_old: int = 30):
    """Clean up files older than specified days"""
    import time
    
    upload_path = Path(settings.upload_dir)
    if not upload_path.exists():
        return
    
    current_time = time.time()
    cutoff_time = current_time - (days_old * 24 * 60 * 60)
    
    for file_path in upload_path.iterdir():
        if file_path.is_file():
            file_time = file_path.stat().st_mtime
            if file_time < cutoff_time:
                try:
                    file_path.unlink()
                    print(f"Deleted old file: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")