"""
Document model for RCM SaaS Application
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_model import BaseModel


class Document(BaseModel):
    """Document model"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hospital_id = kwargs.get('hospital_id', '')
        self.name = kwargs.get('name', '')
        self.type = kwargs.get('type', '')
        self.url = kwargs.get('url', '')
        self.size = kwargs.get('size', 0)
        self.mime_type = kwargs.get('mime_type', '')
        self.uploaded_by = kwargs.get('uploaded_by', '')
        self.related_resource_type = kwargs.get('related_resource_type', '')
        self.related_resource_id = kwargs.get('related_resource_id', '')
        self.is_encrypted = kwargs.get('is_encrypted', False)
        self.encryption_key = kwargs.get('encryption_key', '')
        self.access_level = kwargs.get('access_level', 'private')
        self.tags = kwargs.get('tags', [])
        self.metadata = kwargs.get('metadata', {})
        self.is_verified = kwargs.get('is_verified', False)
        self.verification_date = kwargs.get('verification_date')
        self.verification_notes = kwargs.get('verification_notes', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary"""
        return {
            'id': self.id,
            'hospital_id': self.hospital_id,
            'name': self.name,
            'type': self.type,
            'url': self.url,
            'size': self.size,
            'mime_type': self.mime_type,
            'uploaded_by': self.uploaded_by,
            'related_resource_type': self.related_resource_type,
            'related_resource_id': self.related_resource_id,
            'is_encrypted': self.is_encrypted,
            'encryption_key': self.encryption_key,
            'access_level': self.access_level,
            'tags': self.tags,
            'metadata': self.metadata,
            'is_verified': self.is_verified,
            'verification_date': self.verification_date,
            'verification_notes': self.verification_notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create document from dictionary"""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate document data"""
        errors = super().validate()
        
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Name is required")
        
        if not self.url or len(self.url.strip()) == 0:
            errors.append("URL is required")
        
        return errors
