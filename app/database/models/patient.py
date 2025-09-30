"""
Patient model for RCM SaaS Application
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
from .base_model import BaseModel


class Patient(BaseModel):
    """Patient model"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.uhid = kwargs.get('uhid', '')  # UHID as primary identifier
        self.hospital_id = kwargs.get('hospital_id', '')  # Optional hospital assignment
        self.patient_id = kwargs.get('patient_id', '')  # Hospital's internal patient ID
        self.first_name = kwargs.get('first_name', '')
        self.last_name = kwargs.get('last_name', '')
        self.date_of_birth = kwargs.get('date_of_birth')
        self.gender = kwargs.get('gender', '')
        self.phone_number = kwargs.get('phone_number', '')
        self.email = kwargs.get('email', '')
        self.address = kwargs.get('address', {})
        self.emergency_contact = kwargs.get('emergency_contact', {})
        self.insurance_info = kwargs.get('insurance_info', {})
        self.medical_history = kwargs.get('medical_history', [])
        self.allergies = kwargs.get('allergies', [])
        self.medications = kwargs.get('medications', [])
        self.blood_group = kwargs.get('blood_group', '')
        self.height = kwargs.get('height', 0.0)
        self.weight = kwargs.get('weight', 0.0)
        self.notes = kwargs.get('notes', '')
        self.photo_url = kwargs.get('photo_url', '')
        self.documents = kwargs.get('documents', [])
        self.last_visit = kwargs.get('last_visit')
        self.visit_count = kwargs.get('visit_count', 0)
        self.is_verified = kwargs.get('is_verified', False)
        self.verification_date = kwargs.get('verification_date')
        self.verification_method = kwargs.get('verification_method', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert patient to dictionary"""
        return {
            'id': self.id,
            'uhid': self.uhid,
            'hospital_id': self.hospital_id,
            'patient_id': self.patient_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth,
            'gender': self.gender,
            'phone_number': self.phone_number,
            'email': self.email,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'insurance_info': self.insurance_info,
            'medical_history': self.medical_history,
            'allergies': self.allergies,
            'medications': self.medications,
            'blood_group': self.blood_group,
            'height': self.height,
            'weight': self.weight,
            'notes': self.notes,
            'photo_url': self.photo_url,
            'documents': self.documents,
            'last_visit': self.last_visit,
            'visit_count': self.visit_count,
            'is_verified': self.is_verified,
            'verification_date': self.verification_date,
            'verification_method': self.verification_method,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Patient':
        """Create patient from dictionary"""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate patient data"""
        errors = super().validate()
        
        if not self.hospital_id or len(self.hospital_id.strip()) == 0:
            errors.append("Hospital ID is required")
        
        if not self.patient_id or len(self.patient_id.strip()) == 0:
            errors.append("Patient ID is required")
        
        if not self.first_name or len(self.first_name.strip()) == 0:
            errors.append("First name is required")
        
        if not self.last_name or len(self.last_name.strip()) == 0:
            errors.append("Last name is required")
        
        if not self.date_of_birth:
            errors.append("Date of birth is required")
        
        if self.gender not in ['male', 'female', 'other', 'prefer_not_to_say']:
            errors.append("Invalid gender")
        
        if not self.phone_number or len(self.phone_number.strip()) == 0:
            errors.append("Phone number is required")
        
        if self.blood_group and self.blood_group not in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
            errors.append("Invalid blood group")
        
        if self.height < 0:
            errors.append("Height cannot be negative")
        
        if self.weight < 0:
            errors.append("Weight cannot be negative")
        
        return errors
    
    @property
    def full_name(self) -> str:
        """Get patient's full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def age(self) -> Optional[int]:
        """Calculate patient's age"""
        if not self.date_of_birth:
            return None
        
        today = date.today()
        if isinstance(self.date_of_birth, str):
            dob = datetime.strptime(self.date_of_birth, '%Y-%m-%d').date()
        else:
            dob = self.date_of_birth
        
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    
    def add_medical_record(self, record: Dict[str, Any]):
        """Add a medical record to patient's history"""
        self.medical_history.append({
            'record_id': str(uuid.uuid4()),
            'date': datetime.utcnow(),
            'type': record.get('type', 'general'),
            'description': record.get('description', ''),
            'doctor': record.get('doctor', ''),
            'diagnosis': record.get('diagnosis', ''),
            'treatment': record.get('treatment', ''),
            'attachments': record.get('attachments', [])
        })
        self.update_timestamp()
    
    def add_allergy(self, allergy: str, severity: str = 'mild'):
        """Add an allergy to patient's record"""
        self.allergies.append({
            'allergy': allergy,
            'severity': severity,
            'added_date': datetime.utcnow()
        })
        self.update_timestamp()
    
    def add_medication(self, medication: Dict[str, Any]):
        """Add a medication to patient's record"""
        self.medications.append({
            'medication_id': str(uuid.uuid4()),
            'name': medication.get('name', ''),
            'dosage': medication.get('dosage', ''),
            'frequency': medication.get('frequency', ''),
            'start_date': medication.get('start_date', datetime.utcnow()),
            'end_date': medication.get('end_date'),
            'prescribed_by': medication.get('prescribed_by', ''),
            'is_active': medication.get('is_active', True)
        })
        self.update_timestamp()
    
    def update_visit_info(self):
        """Update visit information"""
        self.last_visit = datetime.utcnow()
        self.visit_count += 1
        self.update_timestamp()
    
    def verify_patient(self, method: str = 'manual'):
        """Verify patient information"""
        self.is_verified = True
        self.verification_date = datetime.utcnow()
        self.verification_method = method
        self.update_timestamp()
