"""
Hospital model for RCM SaaS Application
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_model import BaseModel


class Hospital(BaseModel):
    """Hospital model"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get('name', '')
        self.registration_number = kwargs.get('registration_number', '')
        self.address = kwargs.get('address', {})
        self.contact_info = kwargs.get('contact_info', {})
        self.license_info = kwargs.get('license_info', {})
        self.settings = kwargs.get('settings', {})
        self.subscription_plan = kwargs.get('subscription_plan', 'basic')
        self.subscription_status = kwargs.get('subscription_status', 'active')
        self.subscription_expires_at = kwargs.get('subscription_expires_at')
        self.max_patients = kwargs.get('max_patients', 1000)
        self.max_users = kwargs.get('max_users', 10)
        self.features = kwargs.get('features', [])
        self.timezone = kwargs.get('timezone', 'Asia/Kolkata')
        self.currency = kwargs.get('currency', 'INR')
        self.language = kwargs.get('language', 'en')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert hospital to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'registration_number': self.registration_number,
            'address': self.address,
            'contact_info': self.contact_info,
            'license_info': self.license_info,
            'settings': self.settings,
            'subscription_plan': self.subscription_plan,
            'subscription_status': self.subscription_status,
            'subscription_expires_at': self.subscription_expires_at,
            'max_patients': self.max_patients,
            'max_users': self.max_users,
            'features': self.features,
            'timezone': self.timezone,
            'currency': self.currency,
            'language': self.language,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Hospital':
        """Create hospital from dictionary"""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate hospital data"""
        errors = super().validate()
        
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Hospital name is required")
        
        if not self.registration_number or len(self.registration_number.strip()) == 0:
            errors.append("Registration number is required")
        
        if not self.address or not isinstance(self.address, dict):
            errors.append("Address is required and must be a dictionary")
        
        if not self.contact_info or not isinstance(self.contact_info, dict):
            errors.append("Contact info is required and must be a dictionary")
        
        if self.subscription_plan not in ['basic', 'premium', 'enterprise']:
            errors.append("Invalid subscription plan")
        
        if self.subscription_status not in ['active', 'inactive', 'suspended', 'expired']:
            errors.append("Invalid subscription status")
        
        return errors
    
    def update_subscription(self, plan: str, status: str, expires_at: datetime = None):
        """Update hospital subscription"""
        self.subscription_plan = plan
        self.subscription_status = status
        if expires_at:
            self.subscription_expires_at = expires_at
        self.update_timestamp()
    
    def add_feature(self, feature: str):
        """Add a feature to the hospital"""
        if feature not in self.features:
            self.features.append(feature)
            self.update_timestamp()
    
    def remove_feature(self, feature: str):
        """Remove a feature from the hospital"""
        if feature in self.features:
            self.features.remove(feature)
            self.update_timestamp()
