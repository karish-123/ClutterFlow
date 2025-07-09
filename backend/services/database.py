# backend/services/database.py
from supabase import create_client, Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
import logging
from uuid import UUID

from config.settings import settings
from models.database_models import Base, Document, ExtractedText
from models.schemas import DocumentCreate, ExtractedTextCreate, DocumentUpdate

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        # Supabase client
        self.supabase: Client = create_client(settings.supabase_url, settings.supabase_key)
        
        # SQLAlchemy setup
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    async def create_document(self, document_data: DocumentCreate) -> Optional[Document]:
        """Create a new document record"""
        session = self.get_session()
        try:
            db_document = Document(**document_data.model_dump())
            session.add(db_document)
            session.commit()
            session.refresh(db_document)
            logger.info(f"Created document: {db_document.id}")
            return db_document
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error creating document: {e}")
            return None
        finally:
            session.close()
    
    async def create_extracted_text(self, text_data: ExtractedTextCreate) -> Optional[ExtractedText]:
        """Create extracted text record"""
        session = self.get_session()
        try:
            db_text = ExtractedText(**text_data.model_dump())
            session.add(db_text)
            session.commit()
            session.refresh(db_text)
            logger.info(f"Created extracted text for document: {text_data.document_id}")
            return db_text
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error creating extracted text: {e}")
            return None
        finally:
            session.close()
    
    async def get_document(self, document_id: UUID) -> Optional[Document]:
        """Get document by ID"""
        session = self.get_session()
        try:
            document = session.query(Document).filter(Document.id == document_id).first()
            return document
        except SQLAlchemyError as e:
            logger.error(f"Error getting document: {e}")
            return None
        finally:
            session.close()
    
    async def get_document_with_text(self, document_id: UUID) -> Optional[tuple]:
        """Get document with its extracted text"""
        session = self.get_session()
        try:
            document = session.query(Document).filter(Document.id == document_id).first()
            if document:
                extracted_text = session.query(ExtractedText).filter(
                    ExtractedText.document_id == document_id
                ).first()
                return document, extracted_text
            return None, None
        except SQLAlchemyError as e:
            logger.error(f"Error getting document with text: {e}")
            return None, None
        finally:
            session.close()
    
    async def list_documents(self, skip: int = 0, limit: int = 100) -> tuple[List[Document], int]:
        """List documents with pagination"""
        session = self.get_session()
        try:
            documents = session.query(Document).offset(skip).limit(limit).all()
            total = session.query(Document).count()
            return documents, total
        except SQLAlchemyError as e:
            logger.error(f"Error listing documents: {e}")
            return [], 0
        finally:
            session.close()
    
    async def update_document_status(self, document_id: UUID, status: str) -> Optional[Document]:
        """Update document status"""
        session = self.get_session()
        try:
            document = session.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = status
                session.commit()
                session.refresh(document)
                logger.info(f"Updated document {document_id} status to {status}")
                return document
            return None
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error updating document status: {e}")
            return None
        finally:
            session.close()
    
    async def delete_document(self, document_id: UUID) -> bool:
        """Delete document and its extracted text"""
        session = self.get_session()
        try:
            document = session.query(Document).filter(Document.id == document_id).first()
            if document:
                session.delete(document)
                session.commit()
                logger.info(f"Deleted document: {document_id}")
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error deleting document: {e}")
            return False
        finally:
            session.close()

# Global database service instance
db_service = DatabaseService()