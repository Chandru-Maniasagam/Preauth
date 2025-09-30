"""
Firebase Storage utility for RCM SaaS Application
"""

import os
import uuid
from typing import Dict, Any, List, Optional, BinaryIO
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import storage as firebase_storage
import logging

from app.config import FirebaseConfig, StorageConfig


class FirebaseStorageClient:
    """Firebase Storage client for file operations"""
    
    def __init__(self):
        self.bucket_name = StorageConfig.BUCKET_NAME
        try:
            # Get the bucket using Firebase Admin SDK
            self.bucket = firebase_storage.bucket()
            logging.info("Firebase Storage initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Firebase Storage: {str(e)}")
            self.bucket = None
    
    def upload_patient_document(self, 
                              hospital_id: str, 
                              patient_id: str, 
                              file_data: BinaryIO, 
                              filename: str, 
                              document_type: str,
                              user_id: str) -> Dict[str, Any]:
        """Upload document for a patient"""
        
        # Generate unique filename
        file_extension = os.path.splitext(filename)[1]
        unique_filename = f"{document_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
        
        # Create storage path
        storage_path = f"patients/{hospital_id}/{patient_id}/documents/{document_type}/{unique_filename}"
        
        # Upload file
        blob = self.bucket.blob(storage_path)
        blob.upload_from_file(file_data, content_type=self._get_content_type(file_extension))
        
        # Set metadata
        metadata = StorageConfig.get_storage_metadata(hospital_id, user_id, document_type)
        blob.metadata = metadata
        blob.patch()
        
        # Generate public URL (signed URL for security)
        url = self._generate_signed_url(blob)
        
        return {
            'document_id': str(uuid.uuid4()),
            'name': filename,
            'type': document_type,
            'url': url,
            'storage_path': storage_path,
            'size': blob.size,
            'content_type': blob.content_type,
            'uploaded_at': datetime.utcnow().isoformat(),
            'uploaded_by': user_id
        }
    
    def upload_claim_document(self, 
                            hospital_id: str, 
                            preauth_id: str, 
                            file_data: BinaryIO, 
                            filename: str, 
                            document_type: str,
                            user_id: str) -> Dict[str, Any]:
        """Upload document for a claim/preauth"""
        
        # Generate unique filename
        file_extension = os.path.splitext(filename)[1]
        unique_filename = f"{document_type}_{preauth_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
        
        # Create storage path
        storage_path = f"claims/{hospital_id}/{preauth_id}/documents/{unique_filename}"
        
        # Upload file
        blob = self.bucket.blob(storage_path)
        blob.upload_from_file(file_data, content_type=self._get_content_type(file_extension))
        
        # Set metadata
        metadata = StorageConfig.get_storage_metadata(hospital_id, user_id, document_type)
        blob.metadata = metadata
        blob.patch()
        
        # Generate public URL (signed URL for security)
        url = self._generate_signed_url(blob)
        
        return {
            'document_id': str(uuid.uuid4()),
            'name': filename,
            'type': document_type,
            'url': url,
            'storage_path': storage_path,
            'size': blob.size,
            'content_type': blob.content_type,
            'uploaded_at': datetime.utcnow().isoformat(),
            'uploaded_by': user_id
        }
    
    def upload_general_document(self, 
                              hospital_id: str, 
                              file_data: BinaryIO, 
                              filename: str, 
                              document_type: str,
                              user_id: str) -> Dict[str, Any]:
        """Upload general document"""
        
        # Generate unique filename
        file_extension = os.path.splitext(filename)[1]
        unique_filename = f"{document_type}_{hospital_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
        
        # Create storage path
        storage_path = f"documents/{hospital_id}/{document_type}/{unique_filename}"
        
        # Upload file
        blob = self.bucket.blob(storage_path)
        blob.upload_from_file(file_data, content_type=self._get_content_type(file_extension))
        
        # Set metadata
        metadata = StorageConfig.get_storage_metadata(hospital_id, user_id, document_type)
        blob.metadata = metadata
        blob.patch()
        
        # Generate public URL (signed URL for security)
        url = self._generate_signed_url(blob)
        
        return {
            'document_id': str(uuid.uuid4()),
            'name': filename,
            'type': document_type,
            'url': url,
            'storage_path': storage_path,
            'size': blob.size,
            'content_type': blob.content_type,
            'uploaded_at': datetime.utcnow().isoformat(),
            'uploaded_by': user_id
        }
    
    def delete_document(self, storage_path: str) -> bool:
        """Delete document from storage"""
        try:
            blob = self.bucket.blob(storage_path)
            blob.delete()
            return True
        except NotFound:
            logging.warning(f"Document not found: {storage_path}")
            return False
        except Exception as e:
            logging.error(f"Error deleting document {storage_path}: {str(e)}")
            return False
    
    def get_document_url(self, storage_path: str, expiration_hours: int = 24) -> str:
        """Get signed URL for document access"""
        try:
            blob = self.bucket.blob(storage_path)
            url = blob.generate_signed_url(
                expiration=datetime.utcnow() + timedelta(hours=expiration_hours),
                method='GET'
            )
            return url
        except Exception as e:
            logging.error(f"Error generating signed URL for {storage_path}: {str(e)}")
            return ""
    
    def list_patient_documents(self, hospital_id: str, patient_id: str) -> List[Dict[str, Any]]:
        """List all documents for a patient"""
        prefix = f"patients/{hospital_id}/{patient_id}/documents/"
        return self._list_documents_with_prefix(prefix)
    
    def list_claim_documents(self, hospital_id: str, preauth_id: str) -> List[Dict[str, Any]]:
        """List all documents for a claim"""
        prefix = f"claims/{hospital_id}/{preauth_id}/documents/"
        return self._list_documents_with_prefix(prefix)
    
    def list_hospital_documents(self, hospital_id: str, document_type: str = None) -> List[Dict[str, Any]]:
        """List all documents for a hospital"""
        if document_type:
            prefix = f"documents/{hospital_id}/{document_type}/"
        else:
            prefix = f"documents/{hospital_id}/"
        return self._list_documents_with_prefix(prefix)
    
    def create_thumbnail(self, storage_path: str) -> Optional[str]:
        """Create thumbnail for image documents"""
        try:
            # This would typically use a service like Cloud Functions
            # or a separate microservice for image processing
            # For now, we'll return the original path
            return storage_path
        except Exception as e:
            logging.error(f"Error creating thumbnail for {storage_path}: {str(e)}")
            return None
    
    def cleanup_temp_files(self, hospital_id: str, older_than_hours: int = 24) -> int:
        """Clean up temporary files older than specified hours"""
        try:
            prefix = f"temp/{hospital_id}/"
            cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
            
            blobs = self.bucket.list_blobs(prefix=prefix)
            deleted_count = 0
            
            for blob in blobs:
                if blob.time_created < cutoff_time:
                    blob.delete()
                    deleted_count += 1
            
            return deleted_count
        except Exception as e:
            logging.error(f"Error cleaning up temp files: {str(e)}")
            return 0
    
    def get_storage_usage(self, hospital_id: str) -> Dict[str, Any]:
        """Get storage usage statistics for a hospital"""
        try:
            total_size = 0
            file_count = 0
            
            # Count patients documents
            patients_prefix = f"patients/{hospital_id}/"
            for blob in self.bucket.list_blobs(prefix=patients_prefix):
                total_size += blob.size
                file_count += 1
            
            # Count claims documents
            claims_prefix = f"claims/{hospital_id}/"
            for blob in self.bucket.list_blobs(prefix=claims_prefix):
                total_size += blob.size
                file_count += 1
            
            # Count general documents
            docs_prefix = f"documents/{hospital_id}/"
            for blob in self.bucket.list_blobs(prefix=docs_prefix):
                total_size += blob.size
                file_count += 1
            
            return {
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'file_count': file_count,
                'hospital_id': hospital_id
            }
        except Exception as e:
            logging.error(f"Error getting storage usage: {str(e)}")
            return {
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'file_count': 0,
                'hospital_id': hospital_id
            }
    
    def _list_documents_with_prefix(self, prefix: str) -> List[Dict[str, Any]]:
        """List documents with given prefix"""
        try:
            documents = []
            blobs = self.bucket.list_blobs(prefix=prefix)
            
            for blob in blobs:
                if not blob.name.endswith('/'):  # Skip directories
                    documents.append({
                        'name': os.path.basename(blob.name),
                        'storage_path': blob.name,
                        'size': blob.size,
                        'content_type': blob.content_type,
                        'created_at': blob.time_created.isoformat(),
                        'updated_at': blob.updated.isoformat(),
                        'url': self._generate_signed_url(blob)
                    })
            
            return documents
        except Exception as e:
            logging.error(f"Error listing documents with prefix {prefix}: {str(e)}")
            return []
    
    def _get_content_type(self, file_extension: str) -> str:
        """Get content type based on file extension"""
        content_types = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel'
        }
        return content_types.get(file_extension.lower(), 'application/octet-stream')
    
    def _generate_signed_url(self, blob, expiration_hours: int = 24) -> str:
        """Generate signed URL for blob access"""
        try:
            return blob.generate_signed_url(
                expiration=datetime.utcnow() + timedelta(hours=expiration_hours),
                method='GET'
            )
        except Exception as e:
            logging.error(f"Error generating signed URL: {str(e)}")
            return ""
    
    def health_check(self) -> Dict[str, Any]:
        """Check storage connection health"""
        try:
            # Try to list a small number of blobs to test connection
            list(self.bucket.list_blobs(max_results=1))
            return {
                'status': 'healthy',
                'bucket': self.bucket_name,
                'connection': 'active'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'bucket': self.bucket_name,
                'error': str(e)
            }
