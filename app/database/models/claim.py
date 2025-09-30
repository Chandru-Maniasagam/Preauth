"""
Claim model for RCM SaaS Application
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
from .base_model import BaseModel


class Claim(BaseModel):
    """Claim model for preauth and claims management"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Basic Information
        self.claim_id = kwargs.get('claim_id', '')  # CSHLS-YYYYMMDD-001 format
        self.hospital_id = kwargs.get('hospital_id', '')
        self.hospital_name = kwargs.get('hospital_name', '')
        self.patient_name = kwargs.get('patient_name', '')
        self.mobile_number = kwargs.get('mobile_number', '')
        self.uhid = kwargs.get('uhid', '')
        self.claim_type = kwargs.get('claim_type', '')  # IP/OP/Day care
        self.admission_type = kwargs.get('admission_type', '')  # Planned/Emergency
        self.status = kwargs.get('status', 'draft')  # draft/submitted/approved/rejected
        self.email_id = kwargs.get('email_id', '')
        self.abha_id = kwargs.get('abha_id', '')
        self.admission_datetime = kwargs.get('admission_datetime', '')
        self.ip_number = kwargs.get('ip_number', '')
        
        # Patient Information Section
        self.gender = kwargs.get('gender', '')
        self.date_of_birth = kwargs.get('date_of_birth', '')
        self.age_years = kwargs.get('age_years', 0)
        self.age_months = kwargs.get('age_months', 0)
        self.age_days = kwargs.get('age_days', 0)
        self.customer_id = kwargs.get('customer_id', '')
        self.alternative_contact = kwargs.get('alternative_contact', '')
        self.policy_number = kwargs.get('policy_number', '')
        self.employee_id = kwargs.get('employee_id', '')
        self.additional_policy = kwargs.get('additional_policy', False)
        self.additional_policy_details = kwargs.get('additional_policy_details', {})
        self.family_physician = kwargs.get('family_physician', False)
        self.family_physician_details = kwargs.get('family_physician_details', {})
        
        # Address Information
        self.address = kwargs.get('address', '')
        self.city = kwargs.get('city', '')
        self.state = kwargs.get('state', '')
        self.pincode = kwargs.get('pincode', '')
        self.occupation = kwargs.get('occupation', '')
        
        # Treatment Information
        self.speciality_id = kwargs.get('speciality_id', '')
        self.speciality_name = kwargs.get('speciality_name', '')
        self.treating_doctor_id = kwargs.get('treating_doctor_id', '')
        self.treating_doctor_name = kwargs.get('treating_doctor_name', '')
        self.treating_doctor_contact = kwargs.get('treating_doctor_contact', '')
        self.nature_of_illness = kwargs.get('nature_of_illness', '')  # Disease/Injury
        self.injury_details = kwargs.get('injury_details', {})
        self.clinical_findings = kwargs.get('clinical_findings', '')
        self.duration_of_ailment = kwargs.get('duration_of_ailment', {})
        self.first_consultation_date = kwargs.get('first_consultation_date', '')
        self.past_history_ailment = kwargs.get('past_history_ailment', '')
        self.provisional_diagnosis = kwargs.get('provisional_diagnosis', '')
        self.icd10_code = kwargs.get('icd10_code', '')
        self.proposed_treatment = kwargs.get('proposed_treatment', '')
        self.treatment_plan = kwargs.get('treatment_plan', '')
        self.drug_administration = kwargs.get('drug_administration', '')
        self.injury_occurrence = kwargs.get('injury_occurrence', {})
        self.maternity_details = kwargs.get('maternity_details', {})
        self.past_medical_history = kwargs.get('past_medical_history', {})
        self.treating_doctor_qualification = kwargs.get('treating_doctor_qualification', '')
        self.treating_doctor_registration = kwargs.get('treating_doctor_registration', '')
        self.ward_type = kwargs.get('ward_type', '')
        self.daycare_type = kwargs.get('daycare_type', '')
        self.expected_length_stay = kwargs.get('expected_length_stay', 0)
        self.estimated_treatment_cost = kwargs.get('estimated_treatment_cost', 0.0)
        
        # Payer Information
        self.payer_type = kwargs.get('payer_type', '')
        self.payer_name = kwargs.get('payer_name', '')
        self.insurer_name = kwargs.get('insurer_name', '')
        
        # Hospital Information (from associated hospital document)
        self.hospital_name = kwargs.get('hospital_name', '')
        self.hospital_address = kwargs.get('hospital_address', '')
        self.hospital_contact = kwargs.get('hospital_contact', '')
        
        # Status and Workflow
        self.submitted_at = kwargs.get('submitted_at')
        self.submitted_by = kwargs.get('submitted_by', '')
        self.submitted_by_name = kwargs.get('submitted_by_name', '')
        self.approved_at = kwargs.get('approved_at')
        self.approved_by = kwargs.get('approved_by', '')
        self.approved_by_name = kwargs.get('approved_by_name', '')
        self.rejected_at = kwargs.get('rejected_at')
        self.rejected_by = kwargs.get('rejected_by', '')
        self.rejected_by_name = kwargs.get('rejected_by_name', '')
        self.rejection_reason = kwargs.get('rejection_reason', '')
        
        # Display and UI fields
        self.show_in_claims = kwargs.get('show_in_claims', False)
        
        # File uploads
        self.uploaded_files = kwargs.get('uploaded_files', {})
        
        # Audit fields
        self.created_by = kwargs.get('created_by', '')
        self.updated_by = kwargs.get('updated_by', '')
        self.created_by_name = kwargs.get('created_by_name', '')
        self.updated_by_name = kwargs.get('updated_by_name', '')
        self.is_active = kwargs.get('is_active', True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert claim to dictionary"""
        return {
            'id': self.id,
            'claim_id': self.claim_id,
            'hospital_id': self.hospital_id,
            'hospital_name': self.hospital_name,
            'patient_name': self.patient_name,
            'mobile_number': self.mobile_number,
            'uhid': self.uhid,
            'claim_type': self.claim_type,
            'admission_type': self.admission_type,
            'status': self.status,
            'email_id': self.email_id,
            'abha_id': self.abha_id,
            'admission_datetime': self.admission_datetime,
            'ip_number': self.ip_number,
            
            # Patient Information
            'gender': self.gender,
            'date_of_birth': self.date_of_birth,
            'age_years': self.age_years,
            'age_months': self.age_months,
            'age_days': self.age_days,
            'customer_id': self.customer_id,
            'alternative_contact': self.alternative_contact,
            'policy_number': self.policy_number,
            'employee_id': self.employee_id,
            'additional_policy': self.additional_policy,
            'additional_policy_details': self.additional_policy_details,
            'family_physician': self.family_physician,
            'family_physician_details': self.family_physician_details,
            
            # Address Information
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'occupation': self.occupation,
            
            # Treatment Information
            'speciality_id': self.speciality_id,
            'speciality_name': self.speciality_name,
            'treating_doctor_id': self.treating_doctor_id,
            'treating_doctor_name': self.treating_doctor_name,
            'treating_doctor_contact': self.treating_doctor_contact,
            'nature_of_illness': self.nature_of_illness,
            'injury_details': self.injury_details,
            'clinical_findings': self.clinical_findings,
            'duration_of_ailment': self.duration_of_ailment,
            'first_consultation_date': self.first_consultation_date,
            'past_history_ailment': self.past_history_ailment,
            'provisional_diagnosis': self.provisional_diagnosis,
            'icd10_code': self.icd10_code,
            'proposed_treatment': self.proposed_treatment,
            'treatment_plan': self.treatment_plan,
            'drug_administration': self.drug_administration,
            'injury_occurrence': self.injury_occurrence,
            'maternity_details': self.maternity_details,
            'past_medical_history': self.past_medical_history,
            'treating_doctor_qualification': self.treating_doctor_qualification,
            'treating_doctor_registration': self.treating_doctor_registration,
            'ward_type': self.ward_type,
            'daycare_type': self.daycare_type,
            'expected_length_stay': self.expected_length_stay,
            'estimated_treatment_cost': self.estimated_treatment_cost,
            
            # Payer Information
            'payer_type': self.payer_type,
            'payer_name': self.payer_name,
            'insurer_name': self.insurer_name,
            
            # Hospital Information
            'hospital_name': self.hospital_name,
            'hospital_address': self.hospital_address,
            'hospital_contact': self.hospital_contact,
            
            # Status and Workflow
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'submitted_by': self.submitted_by,
            'submitted_by_name': self.submitted_by_name,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approved_by': self.approved_by,
            'approved_by_name': self.approved_by_name,
            'rejected_at': self.rejected_at.isoformat() if self.rejected_at else None,
            'rejected_by': self.rejected_by,
            'rejected_by_name': self.rejected_by_name,
            'rejection_reason': self.rejection_reason,
            
            # Audit fields
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'created_by_name': self.created_by_name,
            'updated_by_name': self.updated_by_name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'show_in_claims': self.show_in_claims,
            'uploaded_files': self.uploaded_files
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Claim':
        """Create claim from dictionary"""
        # Convert datetime strings back to datetime objects if needed
        if 'admission_datetime' in data and isinstance(data['admission_datetime'], str):
            try:
                data['admission_datetime'] = datetime.fromisoformat(data['admission_datetime'].replace('Z', '+00:00'))
            except:
                pass
        
        if 'date_of_birth' in data and isinstance(data['date_of_birth'], str):
            try:
                data['date_of_birth'] = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except:
                pass
        
        if 'date_of_first_consultation' in data and isinstance(data['date_of_first_consultation'], str):
            try:
                data['date_of_first_consultation'] = datetime.fromisoformat(data['date_of_first_consultation'].replace('Z', '+00:00'))
            except:
                pass
        
        if 'date_of_injury' in data and isinstance(data['date_of_injury'], str):
            try:
                data['date_of_injury'] = datetime.fromisoformat(data['date_of_injury'].replace('Z', '+00:00'))
            except:
                pass
        
        return cls(**data)

    def validate(self) -> List[str]:
        """Validate claim data"""
        errors = []
        
        # Validate mandatory fields
        if not self.patient_name:
            errors.append('Patient name is required')
        if not self.mobile_number:
            errors.append('Mobile number is required')
        if not self.uhid:
            errors.append('UHID is required')
        if not self.claim_type:
            errors.append('Claim type is required')
        if not self.admission_type:
            errors.append('Admission type is required')
        
        # Validate claim type
        valid_claim_types = ['IP', 'OP', 'Day care']
        if self.claim_type and self.claim_type not in valid_claim_types:
            errors.append('Invalid claim type')
        
        # Validate admission type
        valid_admission_types = ['Planned', 'Emergency']
        if self.admission_type and self.admission_type not in valid_admission_types:
            errors.append('Invalid admission type')
        
        return errors
