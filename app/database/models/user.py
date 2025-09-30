"""
User model for RCM SaaS Application
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_model import BaseModel


class User(BaseModel):
    """User model"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hospital_id = kwargs.get('hospital_id', '')
        self.user_id = kwargs.get('user_id', '')  # Hospital's internal user ID
        self.email = kwargs.get('email', '')
        self.username = kwargs.get('username', '')
        self.first_name = kwargs.get('first_name', '')
        self.last_name = kwargs.get('last_name', '')
        self.phone_number = kwargs.get('phone_number', '')
        self.role = kwargs.get('role', 'user')
        self.permissions = kwargs.get('permissions', [])
        self.department = kwargs.get('department', '')
        self.designation = kwargs.get('designation', '')
        self.employee_id = kwargs.get('employee_id', '')
        self.is_active = kwargs.get('is_active', True)
        self.is_verified = kwargs.get('is_verified', False)
        self.last_login = kwargs.get('last_login')
        self.login_count = kwargs.get('login_count', 0)
        self.password_hash = kwargs.get('password_hash', '')
        self.password_reset_token = kwargs.get('password_reset_token', '')
        self.password_reset_expires = kwargs.get('password_reset_expires')
        self.email_verification_token = kwargs.get('email_verification_token', '')
        self.email_verification_expires = kwargs.get('email_verification_expires')
        self.two_factor_enabled = kwargs.get('two_factor_enabled', False)
        self.two_factor_secret = kwargs.get('two_factor_secret', '')
        self.preferences = kwargs.get('preferences', {})
        self.notification_settings = kwargs.get('notification_settings', {})
        self.working_hours = kwargs.get('working_hours', {})
        self.specializations = kwargs.get('specializations', [])
        self.license_number = kwargs.get('license_number', '')
        self.license_expiry = kwargs.get('license_expiry')
        self.qualifications = kwargs.get('qualifications', [])
        self.experience_years = kwargs.get('experience_years', 0)
        self.photo_url = kwargs.get('photo_url', '')
        self.address = kwargs.get('address', {})
        self.emergency_contact = kwargs.get('emergency_contact', {})
        self.salary_info = kwargs.get('salary_info', {})
        self.leave_balance = kwargs.get('leave_balance', {})
        self.performance_metrics = kwargs.get('performance_metrics', {})
        self.assigned_patients = kwargs.get('assigned_patients', [])
        self.assigned_preauths = kwargs.get('assigned_preauths', [])
        self.workload_capacity = kwargs.get('workload_capacity', 100)
        self.current_workload = kwargs.get('current_workload', 0)
        self.skills = kwargs.get('skills', [])
        self.certifications = kwargs.get('certifications', [])
        self.training_records = kwargs.get('training_records', [])
        self.notes = kwargs.get('notes', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'hospital_id': self.hospital_id,
            'user_id': self.user_id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'role': self.role,
            'permissions': self.permissions,
            'department': self.department,
            'designation': self.designation,
            'employee_id': self.employee_id,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login,
            'login_count': self.login_count,
            'password_hash': self.password_hash,
            'password_reset_token': self.password_reset_token,
            'password_reset_expires': self.password_reset_expires,
            'email_verification_token': self.email_verification_token,
            'email_verification_expires': self.email_verification_expires,
            'two_factor_enabled': self.two_factor_enabled,
            'two_factor_secret': self.two_factor_secret,
            'preferences': self.preferences,
            'notification_settings': self.notification_settings,
            'working_hours': self.working_hours,
            'specializations': self.specializations,
            'license_number': self.license_number,
            'license_expiry': self.license_expiry,
            'qualifications': self.qualifications,
            'experience_years': self.experience_years,
            'photo_url': self.photo_url,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'salary_info': self.salary_info,
            'leave_balance': self.leave_balance,
            'performance_metrics': self.performance_metrics,
            'assigned_patients': self.assigned_patients,
            'assigned_preauths': self.assigned_preauths,
            'workload_capacity': self.workload_capacity,
            'current_workload': self.current_workload,
            'skills': self.skills,
            'certifications': self.certifications,
            'training_records': self.training_records,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary"""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate user data"""
        errors = super().validate()
        
        if not self.hospital_id or len(self.hospital_id.strip()) == 0:
            errors.append("Hospital ID is required")
        
        if not self.email or len(self.email.strip()) == 0:
            errors.append("Email is required")
        
        if not self.first_name or len(self.first_name.strip()) == 0:
            errors.append("First name is required")
        
        if not self.last_name or len(self.last_name.strip()) == 0:
            errors.append("Last name is required")
        
        if not self.role or len(self.role.strip()) == 0:
            errors.append("Role is required")
        
        valid_roles = ['super_admin', 'admin', 'doctor', 'nurse', 'receptionist', 
                      'billing_staff', 'insurance_coordinator', 'user']
        
        if self.role not in valid_roles:
            errors.append(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        
        if self.workload_capacity < 0 or self.workload_capacity > 100:
            errors.append("Workload capacity must be between 0 and 100")
        
        if self.current_workload < 0:
            errors.append("Current workload cannot be negative")
        
        return errors
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def display_name(self) -> str:
        """Get user's display name"""
        if self.username:
            return self.username
        return self.full_name
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in self.permissions
    
    def add_permission(self, permission: str):
        """Add permission to user"""
        if permission not in self.permissions:
            self.permissions.append(permission)
            self.update_timestamp()
    
    def remove_permission(self, permission: str):
        """Remove permission from user"""
        if permission in self.permissions:
            self.permissions.remove(permission)
            self.update_timestamp()
    
    def update_login_info(self):
        """Update login information"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        self.update_timestamp()
    
    def reset_password(self, new_password_hash: str):
        """Reset user password"""
        self.password_hash = new_password_hash
        self.password_reset_token = ''
        self.password_reset_expires = None
        self.update_timestamp()
    
    def verify_email(self):
        """Verify user email"""
        self.is_verified = True
        self.email_verification_token = ''
        self.email_verification_expires = None
        self.update_timestamp()
    
    def enable_two_factor(self, secret: str):
        """Enable two-factor authentication"""
        self.two_factor_enabled = True
        self.two_factor_secret = secret
        self.update_timestamp()
    
    def disable_two_factor(self):
        """Disable two-factor authentication"""
        self.two_factor_enabled = False
        self.two_factor_secret = ''
        self.update_timestamp()
    
    def assign_patient(self, patient_id: str):
        """Assign patient to user"""
        if patient_id not in self.assigned_patients:
            self.assigned_patients.append(patient_id)
            self.current_workload = min(self.current_workload + 1, self.workload_capacity)
            self.update_timestamp()
    
    def unassign_patient(self, patient_id: str):
        """Unassign patient from user"""
        if patient_id in self.assigned_patients:
            self.assigned_patients.remove(patient_id)
            self.current_workload = max(self.current_workload - 1, 0)
            self.update_timestamp()
    
    def assign_preauth(self, preauth_id: str):
        """Assign preauth to user"""
        if preauth_id not in self.assigned_preauths:
            self.assigned_preauths.append(preauth_id)
            self.update_timestamp()
    
    def unassign_preauth(self, preauth_id: str):
        """Unassign preauth from user"""
        if preauth_id in self.assigned_preauths:
            self.assigned_preauths.remove(preauth_id)
            self.update_timestamp()
    
    def add_skill(self, skill: str, level: str = 'intermediate'):
        """Add skill to user"""
        self.skills.append({
            'skill': skill,
            'level': level,
            'added_date': datetime.utcnow()
        })
        self.update_timestamp()
    
    def add_certification(self, certification: Dict[str, Any]):
        """Add certification to user"""
        self.certifications.append({
            'certification_id': str(uuid.uuid4()),
            'name': certification.get('name', ''),
            'issuer': certification.get('issuer', ''),
            'issue_date': certification.get('issue_date', datetime.utcnow()),
            'expiry_date': certification.get('expiry_date'),
            'credential_id': certification.get('credential_id', ''),
            'verification_url': certification.get('verification_url', '')
        })
        self.update_timestamp()
    
    def update_performance_metric(self, metric: str, value: float):
        """Update performance metric"""
        self.performance_metrics[metric] = {
            'value': value,
            'updated_at': datetime.utcnow()
        }
        self.update_timestamp()
    
    def is_available(self) -> bool:
        """Check if user is available for new assignments"""
        return (self.is_active and 
                self.is_verified and 
                self.current_workload < self.workload_capacity)
