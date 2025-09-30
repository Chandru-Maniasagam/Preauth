"""
Firebase Storage configuration for RCM SaaS Application
"""

from typing import Dict, Any, List
from .firebase_config import FirebaseConfig


class StorageConfig:
    """Firebase Storage configuration settings"""
    
    # Storage Bucket Configuration
    BUCKET_NAME = "mv20-a1a09.firebasestorage.app"
    BUCKET_URL = f"gs://{BUCKET_NAME}"
    
    # Storage Paths Structure
    STORAGE_PATHS = {
        'patients': 'patients/{hospital_id}/{patient_id}/',
        'claims': 'claims/{hospital_id}/{preauth_id}/',
        'documents': 'documents/{hospital_id}/{document_type}/',
        'reports': 'reports/{hospital_id}/{report_type}/',
        'temp': 'temp/{hospital_id}/',
        'backups': 'backups/{hospital_id}/'
    }
    
    # Document Types
    DOCUMENT_TYPES = {
        'patient_documents': 'patient_documents',
        'claim_documents': 'claim_documents',
        'medical_reports': 'medical_reports',
        'insurance_documents': 'insurance_documents',
        'identity_documents': 'identity_documents',
        'prescriptions': 'prescriptions',
        'discharge_summaries': 'discharge_summaries',
        'lab_reports': 'lab_reports',
        'imaging_reports': 'imaging_reports'
    }
    
    # File Upload Configuration
    UPLOAD_CONFIG = {
        'max_file_size': 16 * 1024 * 1024,  # 16MB
        'allowed_extensions': ['.pdf', '.png', '.jpg', '.jpeg', '.doc', '.docx', '.xlsx', '.xls'],
        'allowed_mime_types': [
            'application/pdf',
            'image/png',
            'image/jpeg',
            'image/jpg',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel'
        ],
        'image_compression': True,
        'image_quality': 85,
        'thumbnail_generation': True,
        'thumbnail_size': (200, 200)
    }
    
    # Security Rules for Storage
    STORAGE_RULES = {
        'patients': {
            'read': 'auth != null && resource.metadata.hospital_id == auth.hospital_id',
            'write': 'auth != null && resource.metadata.hospital_id == auth.hospital_id'
        },
        'claims': {
            'read': 'auth != null && resource.metadata.hospital_id == auth.hospital_id',
            'write': 'auth != null && resource.metadata.hospital_id == auth.hospital_id'
        },
        'documents': {
            'read': 'auth != null && resource.metadata.hospital_id == auth.hospital_id',
            'write': 'auth != null && resource.metadata.hospital_id == auth.hospital_id'
        }
    }
    
    @classmethod
    def get_patient_documents_path(cls, hospital_id: str, patient_id: str) -> str:
        """Get storage path for patient documents"""
        return f"patients/{hospital_id}/{patient_id}/documents/"
    
    @classmethod
    def get_claim_documents_path(cls, hospital_id: str, preauth_id: str) -> str:
        """Get storage path for claim documents"""
        return f"claims/{hospital_id}/{preauth_id}/documents/"
    
    @classmethod
    def get_document_path(cls, hospital_id: str, document_type: str, filename: str) -> str:
        """Get storage path for specific document"""
        return f"documents/{hospital_id}/{document_type}/{filename}"
    
    @classmethod
    def get_temp_path(cls, hospital_id: str, filename: str) -> str:
        """Get temporary storage path"""
        return f"temp/{hospital_id}/{filename}"
    
    @classmethod
    def get_thumbnail_path(cls, original_path: str) -> str:
        """Get thumbnail path for an image"""
        path_parts = original_path.rsplit('.', 1)
        if len(path_parts) == 2:
            return f"{path_parts[0]}_thumb.{path_parts[1]}"
        return f"{original_path}_thumb"
    
    @classmethod
    def validate_file_extension(cls, filename: str) -> bool:
        """Validate file extension"""
        if not filename:
            return False
        
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        allowed_exts = [ext[1:] for ext in cls.UPLOAD_CONFIG['allowed_extensions']]
        return file_ext in allowed_exts
    
    @classmethod
    def validate_file_size(cls, file_size: int) -> bool:
        """Validate file size"""
        return 0 < file_size <= cls.UPLOAD_CONFIG['max_file_size']
    
    @classmethod
    def get_storage_metadata(cls, hospital_id: str, user_id: str, document_type: str = None) -> Dict[str, Any]:
        """Get metadata for uploaded files"""
        metadata = {
            'hospital_id': hospital_id,
            'uploaded_by': user_id,
            'uploaded_at': None,  # Will be set by Firebase
            'content_type': None,  # Will be set by Firebase
            'size': None  # Will be set by Firebase
        }
        
        if document_type:
            metadata['document_type'] = document_type
        
        return metadata
    
    @classmethod
    def get_storage_config(cls) -> Dict[str, Any]:
        """Get complete storage configuration"""
        return {
            'bucket_name': cls.BUCKET_NAME,
            'bucket_url': cls.BUCKET_URL,
            'storage_paths': cls.STORAGE_PATHS,
            'document_types': cls.DOCUMENT_TYPES,
            'upload_config': cls.UPLOAD_CONFIG,
            'storage_rules': cls.STORAGE_RULES
        }
