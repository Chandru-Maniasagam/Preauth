"""
Preauth Request model for RCM SaaS Application
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
from decimal import Decimal
from .base_model import BaseModel


class PreauthRequest(BaseModel):
    """Preauth Request model (stored in claims collection)"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hospital_id = kwargs.get('hospital_id', '')
        self.patient_id = kwargs.get('patient_id', '')
        self.preauth_id = kwargs.get('preauth_id', '')  # Hospital's internal preauth ID
        self.claim_type = kwargs.get('claim_type', 'preauth')  # preauth, claim, appeal
        self.insurance_provider = kwargs.get('insurance_provider', '')
        self.policy_number = kwargs.get('policy_number', '')
        self.policy_holder_name = kwargs.get('policy_holder_name', '')
        self.policy_holder_relation = kwargs.get('policy_holder_relation', '')
        self.treatment_type = kwargs.get('treatment_type', '')
        self.diagnosis_code = kwargs.get('diagnosis_code', '')
        self.procedure_codes = kwargs.get('procedure_codes', [])
        self.estimated_cost = kwargs.get('estimated_cost', 0.0)
        self.requested_amount = kwargs.get('requested_amount', 0.0)
        self.approved_amount = kwargs.get('approved_amount', 0.0)
        self.status = kwargs.get('status', 'pending')
        self.priority = kwargs.get('priority', 'normal')
        self.treatment_date = kwargs.get('treatment_date')
        self.admission_date = kwargs.get('admission_date')
        self.discharge_date = kwargs.get('discharge_date')
        self.doctor_name = kwargs.get('doctor_name', '')
        self.doctor_license = kwargs.get('doctor_license', '')
        self.hospital_name = kwargs.get('hospital_name', '')
        self.room_type = kwargs.get('room_type', '')
        self.room_rent = kwargs.get('room_rent', 0.0)
        self.consultation_fee = kwargs.get('consultation_fee', 0.0)
        self.investigation_cost = kwargs.get('investigation_cost', 0.0)
        self.medicine_cost = kwargs.get('medicine_cost', 0.0)
        self.surgery_cost = kwargs.get('surgery_cost', 0.0)
        self.other_costs = kwargs.get('other_costs', 0.0)
        self.remarks = kwargs.get('remarks', '')
        self.insurance_remarks = kwargs.get('insurance_remarks', '')
        self.documents = kwargs.get('documents', [])
        self.attachments = kwargs.get('attachments', [])
        self.submission_date = kwargs.get('submission_date', datetime.utcnow())
        self.approval_date = kwargs.get('approval_date')
        self.rejection_date = kwargs.get('rejection_date')
        self.rejection_reason = kwargs.get('rejection_reason', '')
        self.approval_reference = kwargs.get('approval_reference', '')
        self.validity_period = kwargs.get('validity_period', 30)  # days
        self.expiry_date = kwargs.get('expiry_date')
        self.follow_up_required = kwargs.get('follow_up_required', False)
        self.follow_up_date = kwargs.get('follow_up_date')
        self.assigned_to = kwargs.get('assigned_to', '')
        self.assigned_date = kwargs.get('assigned_date')
        self.completion_date = kwargs.get('completion_date')
        self.is_urgent = kwargs.get('is_urgent', False)
        self.urgent_reason = kwargs.get('urgent_reason', '')
        self.patient_contribution = kwargs.get('patient_contribution', 0.0)
        self.insurance_contribution = kwargs.get('insurance_contribution', 0.0)
        self.copay_amount = kwargs.get('copay_amount', 0.0)
        self.deductible_amount = kwargs.get('deductible_amount', 0.0)
        self.coverage_percentage = kwargs.get('coverage_percentage', 0.0)
        self.exclusions = kwargs.get('exclusions', [])
        self.pre_existing_conditions = kwargs.get('pre_existing_conditions', [])
        self.waiting_period_applicable = kwargs.get('waiting_period_applicable', False)
        self.waiting_period_days = kwargs.get('waiting_period_days', 0)
        self.claim_number = kwargs.get('claim_number', '')
        self.tpa_name = kwargs.get('tpa_name', '')
        self.tpa_contact = kwargs.get('tpa_contact', {})
        self.verification_status = kwargs.get('verification_status', 'pending')
        self.verification_date = kwargs.get('verification_date')
        self.verification_notes = kwargs.get('verification_notes', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert preauth request to dictionary"""
        return {
            'id': self.id,
            'hospital_id': self.hospital_id,
            'patient_id': self.patient_id,
            'preauth_id': self.preauth_id,
            'claim_type': self.claim_type,
            'insurance_provider': self.insurance_provider,
            'policy_number': self.policy_number,
            'policy_holder_name': self.policy_holder_name,
            'policy_holder_relation': self.policy_holder_relation,
            'treatment_type': self.treatment_type,
            'diagnosis_code': self.diagnosis_code,
            'procedure_codes': self.procedure_codes,
            'estimated_cost': self.estimated_cost,
            'requested_amount': self.requested_amount,
            'approved_amount': self.approved_amount,
            'status': self.status,
            'priority': self.priority,
            'treatment_date': self.treatment_date,
            'admission_date': self.admission_date,
            'discharge_date': self.discharge_date,
            'doctor_name': self.doctor_name,
            'doctor_license': self.doctor_license,
            'hospital_name': self.hospital_name,
            'room_type': self.room_type,
            'room_rent': self.room_rent,
            'consultation_fee': self.consultation_fee,
            'investigation_cost': self.investigation_cost,
            'medicine_cost': self.medicine_cost,
            'surgery_cost': self.surgery_cost,
            'other_costs': self.other_costs,
            'remarks': self.remarks,
            'insurance_remarks': self.insurance_remarks,
            'documents': self.documents,
            'attachments': self.attachments,
            'submission_date': self.submission_date,
            'approval_date': self.approval_date,
            'rejection_date': self.rejection_date,
            'rejection_reason': self.rejection_reason,
            'approval_reference': self.approval_reference,
            'validity_period': self.validity_period,
            'expiry_date': self.expiry_date,
            'follow_up_required': self.follow_up_required,
            'follow_up_date': self.follow_up_date,
            'assigned_to': self.assigned_to,
            'assigned_date': self.assigned_date,
            'completion_date': self.completion_date,
            'is_urgent': self.is_urgent,
            'urgent_reason': self.urgent_reason,
            'patient_contribution': self.patient_contribution,
            'insurance_contribution': self.insurance_contribution,
            'copay_amount': self.copay_amount,
            'deductible_amount': self.deductible_amount,
            'coverage_percentage': self.coverage_percentage,
            'exclusions': self.exclusions,
            'pre_existing_conditions': self.pre_existing_conditions,
            'waiting_period_applicable': self.waiting_period_applicable,
            'waiting_period_days': self.waiting_period_days,
            'claim_number': self.claim_number,
            'tpa_name': self.tpa_name,
            'tpa_contact': self.tpa_contact,
            'verification_status': self.verification_status,
            'verification_date': self.verification_date,
            'verification_notes': self.verification_notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PreauthRequest':
        """Create preauth request from dictionary"""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """Validate preauth request data"""
        errors = super().validate()
        
        if not self.hospital_id or len(self.hospital_id.strip()) == 0:
            errors.append("Hospital ID is required")
        
        if not self.patient_id or len(self.patient_id.strip()) == 0:
            errors.append("Patient ID is required")
        
        if not self.preauth_id or len(self.preauth_id.strip()) == 0:
            errors.append("Preauth ID is required")
        
        if not self.insurance_provider or len(self.insurance_provider.strip()) == 0:
            errors.append("Insurance provider is required")
        
        if not self.policy_number or len(self.policy_number.strip()) == 0:
            errors.append("Policy number is required")
        
        if not self.treatment_type or len(self.treatment_type.strip()) == 0:
            errors.append("Treatment type is required")
        
        if not self.diagnosis_code or len(self.diagnosis_code.strip()) == 0:
            errors.append("Diagnosis code is required")
        
        if self.estimated_cost <= 0:
            errors.append("Estimated cost must be greater than 0")
        
        if self.requested_amount <= 0:
            errors.append("Requested amount must be greater than 0")
        
        if self.status not in ['pending', 'submitted', 'under_review', 'approved', 'rejected', 'expired', 'cancelled']:
            errors.append("Invalid status")
        
        if self.priority not in ['low', 'normal', 'high', 'urgent']:
            errors.append("Invalid priority")
        
        if self.policy_holder_relation not in ['self', 'spouse', 'child', 'parent', 'sibling', 'other']:
            errors.append("Invalid policy holder relation")
        
        return errors
    
    def calculate_total_cost(self) -> float:
        """Calculate total estimated cost"""
        return (
            self.room_rent + 
            self.consultation_fee + 
            self.investigation_cost + 
            self.medicine_cost + 
            self.surgery_cost + 
            self.other_costs
        )
    
    def update_status(self, status: str, remarks: str = '', reference: str = ''):
        """Update preauth request status"""
        self.status = status
        self.updated_at = datetime.utcnow()
        
        if status == 'approved':
            self.approval_date = datetime.utcnow()
            self.approval_reference = reference
            self.insurance_remarks = remarks
        elif status == 'rejected':
            self.rejection_date = datetime.utcnow()
            self.rejection_reason = remarks
        elif status == 'completed':
            self.completion_date = datetime.utcnow()
    
    def assign_to_user(self, user_id: str):
        """Assign preauth request to a user"""
        self.assigned_to = user_id
        self.assigned_date = datetime.utcnow()
        self.update_timestamp()
    
    def set_urgent(self, reason: str):
        """Mark preauth request as urgent"""
        self.is_urgent = True
        self.urgent_reason = reason
        self.priority = 'urgent'
        self.update_timestamp()
    
    def add_document(self, document: Dict[str, Any]):
        """Add a document to the preauth request"""
        self.documents.append({
            'document_id': str(uuid.uuid4()),
            'name': document.get('name', ''),
            'type': document.get('type', ''),
            'url': document.get('url', ''),
            'uploaded_at': datetime.utcnow(),
            'uploaded_by': document.get('uploaded_by', ''),
            'size': document.get('size', 0),
            'is_required': document.get('is_required', False)
        })
        self.update_timestamp()
    
    def calculate_expiry_date(self):
        """Calculate expiry date based on validity period"""
        if self.submission_date and self.validity_period:
            from datetime import timedelta
            self.expiry_date = self.submission_date + timedelta(days=self.validity_period)
    
    def is_expired(self) -> bool:
        """Check if preauth request is expired"""
        if not self.expiry_date:
            return False
        return datetime.utcnow() > self.expiry_date
    
    def get_remaining_days(self) -> int:
        """Get remaining days until expiry"""
        if not self.expiry_date:
            return 0
        
        remaining = self.expiry_date - datetime.utcnow()
        return max(0, remaining.days)
