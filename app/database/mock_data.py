"""
Mock data service for when Firebase is not available
"""

from datetime import datetime
from typing import List, Dict, Any
import uuid


class MockDataService:
    """Mock data service for testing when Firebase is not available"""
    
    @staticmethod
    def get_mock_patients() -> List[Dict[str, Any]]:
        """Get mock patient data"""
        return [
            {
                'id': str(uuid.uuid4()),
                'uhid': 'PAT001',
                'patient_id': 'HOSP_001_PAT_001',
                'first_name': 'John',
                'last_name': 'Doe',
                'date_of_birth': '1990-01-15',
                'age': 34,
                'gender': 'male',
                'phone_number': '+91 9876543210',
                'email': 'john.doe@example.com',
                'address': {
                    'street': '123 Main Street',
                    'city': 'Mumbai',
                    'state': 'Maharashtra',
                    'pincode': '400001',
                    'country': 'India'
                },
                'created_at': datetime.utcnow().isoformat(),
                'is_active': True
            },
            {
                'id': str(uuid.uuid4()),
                'uhid': 'PAT002',
                'patient_id': 'HOSP_001_PAT_002',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'date_of_birth': '1985-05-20',
                'age': 39,
                'gender': 'female',
                'phone_number': '+91 9876543211',
                'email': 'jane.smith@example.com',
                'address': {
                    'street': '456 Park Avenue',
                    'city': 'Delhi',
                    'state': 'Delhi',
                    'pincode': '110001',
                    'country': 'India'
                },
                'created_at': datetime.utcnow().isoformat(),
                'is_active': True
            }
        ]
    
    @staticmethod
    def get_mock_claims() -> List[Dict[str, Any]]:
        """Get mock claims data"""
        return [
            {
                'id': str(uuid.uuid4()),
                'claim_id': 'CLM001',
                'hospital_id': 'HOSP_001',
                'hospital_name': 'Test Hospital',
                'patient_name': 'John Doe',
                'mobile_number': '+91 9876543210',
                'uhid': 'PAT001',
                'claim_type': 'IP',
                'admission_type': 'Planned',
                'status': 'draft',
                'payer_type': 'TPA',
                'payer_name': 'Test TPA',
                'insurer_name': 'Test Insurance',
                'created_at': datetime.utcnow().isoformat(),
                'is_active': True
            },
            {
                'id': str(uuid.uuid4()),
                'claim_id': 'CLM002',
                'hospital_id': 'HOSP_001',
                'hospital_name': 'Test Hospital',
                'patient_name': 'Jane Smith',
                'mobile_number': '+91 9876543211',
                'uhid': 'PAT002',
                'claim_type': 'OP',
                'admission_type': 'Emergency',
                'status': 'submitted',
                'payer_type': 'Insurer',
                'payer_name': 'Test Insurance',
                'insurer_name': 'Test Insurance',
                'created_at': datetime.utcnow().isoformat(),
                'is_active': True
            }
        ]
    
    @staticmethod
    def get_mock_specialities() -> List[Dict[str, Any]]:
        """Get mock specialities data"""
        return [
            {'id': 'SPEC001', 'name': 'Cardiology', 'description': 'Heart and cardiovascular diseases'},
            {'id': 'SPEC002', 'name': 'Neurology', 'description': 'Brain and nervous system disorders'},
            {'id': 'SPEC003', 'name': 'Orthopedics', 'description': 'Bone and joint disorders'},
            {'id': 'SPEC004', 'name': 'Pediatrics', 'description': 'Medical care for children'},
            {'id': 'SPEC005', 'name': 'Gynecology', 'description': 'Women\'s reproductive health'}
        ]
    
    @staticmethod
    def get_mock_doctors() -> List[Dict[str, Any]]:
        """Get mock doctors data"""
        return [
            {
                'id': 'DOC001',
                'name': 'Dr. Rajesh Kumar',
                'contact': '+91 9876543201',
                'qualification': 'MD, DM Cardiology',
                'registration_number': 'MH12345',
                'speciality_id': 'SPEC001',
                'hospital_id': 'HOSP_001'
            },
            {
                'id': 'DOC002',
                'name': 'Dr. Priya Sharma',
                'contact': '+91 9876543202',
                'qualification': 'MD, DM Neurology',
                'registration_number': 'MH12346',
                'speciality_id': 'SPEC002',
                'hospital_id': 'HOSP_001'
            }
        ]
    
    @staticmethod
    def get_mock_payers() -> List[Dict[str, Any]]:
        """Get mock payers data"""
        return [
            {'id': 'PAYER001', 'name': 'Test TPA', 'payer_type': 'TPA', 'code': 'TPA001'},
            {'id': 'PAYER002', 'name': 'Test Insurance', 'payer_type': 'Insurer', 'code': 'INS001'},
            {'id': 'PAYER003', 'name': 'Test Corporate', 'payer_type': 'Corporate', 'code': 'CORP001'}
        ]
    
    @staticmethod
    def get_mock_corporates() -> List[Dict[str, Any]]:
        """Get mock corporates data"""
        return [
            {'id': 'CORP001', 'name': 'Tech Corp Ltd', 'code': 'TECH001'},
            {'id': 'CORP002', 'name': 'Finance Corp Ltd', 'code': 'FIN001'},
            {'id': 'CORP003', 'name': 'Healthcare Corp Ltd', 'code': 'HC001'}
        ]
