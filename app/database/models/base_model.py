"""
Base model class for RCM SaaS Application
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


class BaseModel(ABC):
    """Base model class for all database models"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.created_by = kwargs.get('created_by')
        self.updated_by = kwargs.get('updated_by')
        self.is_active = kwargs.get('is_active', True)
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for Firestore"""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model from dictionary"""
        pass
    
    def validate(self) -> List[str]:
        """Validate model data"""
        errors = []
        
        if not self.id:
            errors.append("ID is required")
        
        if not self.created_at:
            errors.append("Created at timestamp is required")
        
        return errors
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
    
    def soft_delete(self):
        """Soft delete the model"""
        self.is_active = False
        self.update_timestamp()
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"
    
    def __repr__(self) -> str:
        return self.__str__()
