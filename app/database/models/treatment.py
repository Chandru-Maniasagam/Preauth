"""
Treatment model for RCM SaaS Application
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_model import BaseModel


class Treatment(BaseModel):
    """Treatment model"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hospital_id = kwargs.get('hospital_id', '')
        self.name = kwargs.get('name', '')
        self.code = kwargs.get('code', '')
        self.category = kwargs.get('category', '')
        self.description = kwargs.get('description', '')
        self.cost = kwargs.get('cost', 0.0)
        self.duration_hours = kwargs.get('duration_hours', 0)
        self.requirements = kwargs.get('requirements', [])
        self.is_active = kwargs.get('is_active', True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert treatment to dictionary"""
        return {
            'id': self.id,
            'hospital_id': self.hospital_id,
            'name': self.name,
            'code': self.code,
            'category': self.category,
            'description': self.description,
            'cost': self.cost,
            'duration_hours': self.duration_hours,
            'requirements': self.requirements,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Treatment':
        """Create treatment from dictionary"""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate treatment data"""
        errors = super().validate()
        
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Name is required")
        
        if not self.code or len(self.code.strip()) == 0:
            errors.append("Code is required")
        
        return errors
