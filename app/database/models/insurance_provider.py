"""
Insurance Provider model for RCM SaaS Application
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_model import BaseModel


class InsuranceProvider(BaseModel):
    """Insurance Provider model"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get('name', '')
        self.code = kwargs.get('code', '')
        self.type = kwargs.get('type', '')  # public, private, tpa
        self.contact_info = kwargs.get('contact_info', {})
        self.address = kwargs.get('address', {})
        self.website = kwargs.get('website', '')
        self.api_endpoint = kwargs.get('api_endpoint', '')
        self.api_credentials = kwargs.get('api_credentials', {})
        self.supported_features = kwargs.get('supported_features', [])
        self.preferences = kwargs.get('preferences', {})
        self.is_active = kwargs.get('is_active', True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert insurance provider to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'type': self.type,
            'contact_info': self.contact_info,
            'address': self.address,
            'website': self.website,
            'api_endpoint': self.api_endpoint,
            'api_credentials': self.api_credentials,
            'supported_features': self.supported_features,
            'preferences': self.preferences,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InsuranceProvider':
        """Create insurance provider from dictionary"""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate insurance provider data"""
        errors = super().validate()
        
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Name is required")
        
        if not self.code or len(self.code.strip()) == 0:
            errors.append("Code is required")
        
        return errors
