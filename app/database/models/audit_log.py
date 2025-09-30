"""
Audit Log model for RCM SaaS Application
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_model import BaseModel


class AuditLog(BaseModel):
    """Audit Log model for tracking system activities"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hospital_id = kwargs.get('hospital_id', '')
        self.user_id = kwargs.get('user_id', '')
        self.action = kwargs.get('action', '')
        self.resource_type = kwargs.get('resource_type', '')
        self.resource_id = kwargs.get('resource_id', '')
        self.old_values = kwargs.get('old_values', {})
        self.new_values = kwargs.get('new_values', {})
        self.ip_address = kwargs.get('ip_address', '')
        self.user_agent = kwargs.get('user_agent', '')
        self.session_id = kwargs.get('session_id', '')
        self.request_id = kwargs.get('request_id', '')
        self.duration_ms = kwargs.get('duration_ms', 0)
        self.status = kwargs.get('status', 'success')
        self.error_message = kwargs.get('error_message', '')
        self.metadata = kwargs.get('metadata', {})
        self.severity = kwargs.get('severity', 'info')
        self.category = kwargs.get('category', 'general')
        self.tags = kwargs.get('tags', [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'hospital_id': self.hospital_id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'request_id': self.request_id,
            'duration_ms': self.duration_ms,
            'status': self.status,
            'error_message': self.error_message,
            'metadata': self.metadata,
            'severity': self.severity,
            'category': self.category,
            'tags': self.tags,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditLog':
        """Create audit log from dictionary"""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate audit log data"""
        errors = super().validate()
        
        if not self.action or len(self.action.strip()) == 0:
            errors.append("Action is required")
        
        if not self.resource_type or len(self.resource_type.strip()) == 0:
            errors.append("Resource type is required")
        
        if not self.resource_id or len(self.resource_id.strip()) == 0:
            errors.append("Resource ID is required")
        
        valid_severities = ['debug', 'info', 'warning', 'error', 'critical']
        if self.severity not in valid_severities:
            errors.append(f"Invalid severity. Must be one of: {', '.join(valid_severities)}")
        
        valid_statuses = ['success', 'failure', 'pending', 'cancelled']
        if self.status not in valid_statuses:
            errors.append(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        return errors
