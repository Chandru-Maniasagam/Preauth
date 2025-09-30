"""
Preauth State model for RCM SaaS Application
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_model import BaseModel


class PreauthState(BaseModel):
    """Preauth State model for tracking state changes"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.preauth_id = kwargs.get('preauth_id', '')
        self.hospital_id = kwargs.get('hospital_id', '')
        self.state = kwargs.get('state', '')
        self.previous_state = kwargs.get('previous_state', '')
        self.state_data = kwargs.get('state_data', {})
        self.remarks = kwargs.get('remarks', '')
        self.changed_by = kwargs.get('changed_by', '')
        self.changed_at = kwargs.get('changed_at', datetime.utcnow())
        self.duration_minutes = kwargs.get('duration_minutes', 0)
        self.is_automatic = kwargs.get('is_automatic', False)
        self.trigger_event = kwargs.get('trigger_event', '')
        self.next_actions = kwargs.get('next_actions', [])
        self.assigned_to = kwargs.get('assigned_to', '')
        self.estimated_completion = kwargs.get('estimated_completion')
        self.actual_completion = kwargs.get('actual_completion')
        self.notes = kwargs.get('notes', '')
        self.attachments = kwargs.get('attachments', [])
        self.notifications_sent = kwargs.get('notifications_sent', [])
        self.escalation_level = kwargs.get('escalation_level', 0)
        self.is_escalated = kwargs.get('is_escalated', False)
        self.escalation_reason = kwargs.get('escalation_reason', '')
        self.sla_breach = kwargs.get('sla_breach', False)
        self.sla_breach_reason = kwargs.get('sla_breach_reason', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert preauth state to dictionary"""
        return {
            'id': self.id,
            'preauth_id': self.preauth_id,
            'hospital_id': self.hospital_id,
            'state': self.state,
            'previous_state': self.previous_state,
            'state_data': self.state_data,
            'remarks': self.remarks,
            'changed_by': self.changed_by,
            'changed_at': self.changed_at,
            'duration_minutes': self.duration_minutes,
            'is_automatic': self.is_automatic,
            'trigger_event': self.trigger_event,
            'next_actions': self.next_actions,
            'assigned_to': self.assigned_to,
            'estimated_completion': self.estimated_completion,
            'actual_completion': self.actual_completion,
            'notes': self.notes,
            'attachments': self.attachments,
            'notifications_sent': self.notifications_sent,
            'escalation_level': self.escalation_level,
            'is_escalated': self.is_escalated,
            'escalation_reason': self.escalation_reason,
            'sla_breach': self.sla_breach,
            'sla_breach_reason': self.sla_breach_reason,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PreauthState':
        """Create preauth state from dictionary"""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate preauth state data"""
        errors = super().validate()
        
        if not self.preauth_id or len(self.preauth_id.strip()) == 0:
            errors.append("Preauth ID is required")
        
        if not self.hospital_id or len(self.hospital_id.strip()) == 0:
            errors.append("Hospital ID is required")
        
        if not self.state or len(self.state.strip()) == 0:
            errors.append("State is required")
        
        valid_states = [
            'draft', 'submitted', 'under_review', 'pending_documents',
            'pending_verification', 'pending_approval', 'approved',
            'rejected', 'expired', 'cancelled', 'completed'
        ]
        
        if self.state not in valid_states:
            errors.append(f"Invalid state. Must be one of: {', '.join(valid_states)}")
        
        if self.duration_minutes < 0:
            errors.append("Duration cannot be negative")
        
        if self.escalation_level < 0:
            errors.append("Escalation level cannot be negative")
        
        return errors
    
    def calculate_duration(self, previous_state_time: datetime):
        """Calculate duration in current state"""
        if previous_state_time:
            duration = self.changed_at - previous_state_time
            self.duration_minutes = int(duration.total_seconds() / 60)
    
    def add_next_action(self, action: str, due_date: datetime = None):
        """Add next action to be taken"""
        self.next_actions.append({
            'action': action,
            'due_date': due_date,
            'created_at': datetime.utcnow(),
            'completed': False
        })
        self.update_timestamp()
    
    def complete_action(self, action: str):
        """Mark an action as completed"""
        for next_action in self.next_actions:
            if next_action['action'] == action and not next_action['completed']:
                next_action['completed'] = True
                next_action['completed_at'] = datetime.utcnow()
                break
        self.update_timestamp()
    
    def escalate(self, reason: str, level: int = 1):
        """Escalate the preauth state"""
        self.is_escalated = True
        self.escalation_level = level
        self.escalation_reason = reason
        self.update_timestamp()
    
    def check_sla_breach(self, sla_hours: int):
        """Check if SLA has been breached"""
        if self.estimated_completion:
            if datetime.utcnow() > self.estimated_completion:
                self.sla_breach = True
                self.sla_breach_reason = f"SLA breached by {sla_hours} hours"
                return True
        return False
    
    def add_notification(self, notification_id: str, type: str):
        """Add notification sent for this state"""
        self.notifications_sent.append({
            'notification_id': notification_id,
            'type': type,
            'sent_at': datetime.utcnow()
        })
        self.update_timestamp()
    
    def add_attachment(self, attachment: Dict[str, Any]):
        """Add attachment to state"""
        self.attachments.append({
            'attachment_id': str(uuid.uuid4()),
            'name': attachment.get('name', ''),
            'type': attachment.get('type', ''),
            'url': attachment.get('url', ''),
            'uploaded_at': datetime.utcnow(),
            'uploaded_by': attachment.get('uploaded_by', '')
        })
        self.update_timestamp()
