"""
Notification model for RCM SaaS Application
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_model import BaseModel


class Notification(BaseModel):
    """Notification model"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hospital_id = kwargs.get('hospital_id', '')
        self.user_id = kwargs.get('user_id', '')
        self.title = kwargs.get('title', '')
        self.message = kwargs.get('message', '')
        self.type = kwargs.get('type', 'info')
        self.category = kwargs.get('category', 'general')
        self.priority = kwargs.get('priority', 'normal')
        self.is_read = kwargs.get('is_read', False)
        self.read_at = kwargs.get('read_at')
        self.related_resource_type = kwargs.get('related_resource_type', '')
        self.related_resource_id = kwargs.get('related_resource_id', '')
        self.action_url = kwargs.get('action_url', '')
        self.action_text = kwargs.get('action_text', '')
        self.expires_at = kwargs.get('expires_at')
        self.scheduled_at = kwargs.get('scheduled_at')
        self.sent_at = kwargs.get('sent_at')
        self.delivery_status = kwargs.get('delivery_status', 'pending')
        self.delivery_methods = kwargs.get('delivery_methods', ['in_app'])
        self.retry_count = kwargs.get('retry_count', 0)
        self.max_retries = kwargs.get('max_retries', 3)
        self.error_message = kwargs.get('error_message', '')
        self.metadata = kwargs.get('metadata', {})
        self.tags = kwargs.get('tags', [])
        self.group_id = kwargs.get('group_id', '')
        self.parent_notification_id = kwargs.get('parent_notification_id', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert notification to dictionary"""
        return {
            'id': self.id,
            'hospital_id': self.hospital_id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'category': self.category,
            'priority': self.priority,
            'is_read': self.is_read,
            'read_at': self.read_at,
            'related_resource_type': self.related_resource_type,
            'related_resource_id': self.related_resource_id,
            'action_url': self.action_url,
            'action_text': self.action_text,
            'expires_at': self.expires_at,
            'scheduled_at': self.scheduled_at,
            'sent_at': self.sent_at,
            'delivery_status': self.delivery_status,
            'delivery_methods': self.delivery_methods,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'error_message': self.error_message,
            'metadata': self.metadata,
            'tags': self.tags,
            'group_id': self.group_id,
            'parent_notification_id': self.parent_notification_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        """Create notification from dictionary"""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate notification data"""
        errors = super().validate()
        
        if not self.title or len(self.title.strip()) == 0:
            errors.append("Title is required")
        
        if not self.message or len(self.message.strip()) == 0:
            errors.append("Message is required")
        
        valid_types = ['info', 'success', 'warning', 'error', 'urgent']
        if self.type not in valid_types:
            errors.append(f"Invalid type. Must be one of: {', '.join(valid_types)}")
        
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        if self.priority not in valid_priorities:
            errors.append(f"Invalid priority. Must be one of: {', '.join(valid_priorities)}")
        
        valid_delivery_statuses = ['pending', 'sent', 'delivered', 'failed', 'cancelled']
        if self.delivery_status not in valid_delivery_statuses:
            errors.append(f"Invalid delivery status. Must be one of: {', '.join(valid_delivery_statuses)}")
        
        return errors
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
        self.update_timestamp()
    
    def mark_as_unread(self):
        """Mark notification as unread"""
        self.is_read = False
        self.read_at = None
        self.update_timestamp()
    
    def mark_as_sent(self):
        """Mark notification as sent"""
        self.delivery_status = 'sent'
        self.sent_at = datetime.utcnow()
        self.update_timestamp()
    
    def mark_as_delivered(self):
        """Mark notification as delivered"""
        self.delivery_status = 'delivered'
        self.update_timestamp()
    
    def mark_as_failed(self, error_message: str = ''):
        """Mark notification as failed"""
        self.delivery_status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.update_timestamp()
    
    def can_retry(self) -> bool:
        """Check if notification can be retried"""
        return (self.delivery_status == 'failed' and 
                self.retry_count < self.max_retries)
    
    def is_expired(self) -> bool:
        """Check if notification is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def is_scheduled(self) -> bool:
        """Check if notification is scheduled for future"""
        if not self.scheduled_at:
            return False
        return datetime.utcnow() < self.scheduled_at
    
    def add_tag(self, tag: str):
        """Add tag to notification"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.update_timestamp()
    
    def remove_tag(self, tag: str):
        """Remove tag from notification"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.update_timestamp()
