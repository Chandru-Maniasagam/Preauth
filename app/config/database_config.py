"""
Database configuration for RCM SaaS Application
"""

from typing import Dict, Any, List
from .firebase_config import FirebaseConfig


class DatabaseConfig:
    """Database configuration settings"""
    
    # Firestore Collections
    COLLECTIONS = {
        'hospitals': 'hospitals',
        'patients': 'patients',
        'claims': 'claims',  # Changed from preauth_requests to claims
        'preauth_states': 'preauth_states',
        'users': 'users',
        'audit_logs': 'audit_logs',
        'notifications': 'notifications',
        'reports': 'reports',
        'insurance_providers': 'insurance_providers',
        'treatments': 'treatments',
        'documents': 'documents'
    }
    
    # Collection Indexes
    INDEXES = {
        'patients': [
            {'fields': ['hospital_id', 'created_at']},
            {'fields': ['patient_id', 'hospital_id']},
            {'fields': ['phone_number', 'hospital_id']},
            {'fields': ['email', 'hospital_id']}
        ],
        'claims': [
            {'fields': ['hospital_id', 'status', 'created_at']},
            {'fields': ['patient_id', 'hospital_id']},
            {'fields': ['insurance_provider', 'status']},
            {'fields': ['created_at', 'status']},
            {'fields': ['preauth_id', 'hospital_id']},
            {'fields': ['claim_type', 'status']},
            {'fields': ['submission_date', 'status']},
            {'fields': ['approval_date', 'status']}
        ],
        'preauth_states': [
            {'fields': ['preauth_id', 'state', 'created_at']},
            {'fields': ['hospital_id', 'state', 'created_at']}
        ],
        'users': [
            {'fields': ['hospital_id', 'role', 'is_active']},
            {'fields': ['email', 'hospital_id']},
            {'fields': ['user_id', 'hospital_id']}
        ]
    }
    
    # Database Rules (for Firestore security)
    SECURITY_RULES = {
        'hospitals': {
            'read': 'auth != null && resource.data.hospital_id == auth.hospital_id',
            'write': 'auth != null && auth.role in ["admin", "super_admin"]'
        },
        'patients': {
            'read': 'auth != null && resource.data.hospital_id == auth.hospital_id',
            'write': 'auth != null && resource.data.hospital_id == auth.hospital_id'
        },
        'claims': {
            'read': 'auth != null && resource.data.hospital_id == auth.hospital_id',
            'write': 'auth != null && resource.data.hospital_id == auth.hospital_id'
        }
    }
    
    @classmethod
    def get_collection_name(cls, collection_key: str) -> str:
        """Get collection name by key"""
        return cls.COLLECTIONS.get(collection_key, collection_key)
    
    @classmethod
    def get_indexes_for_collection(cls, collection_name: str) -> List[Dict[str, Any]]:
        """Get indexes for a specific collection"""
        return cls.INDEXES.get(collection_name, [])
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Get complete database configuration"""
        return {
            'project_id': FirebaseConfig.PROJECT_ID,
            'collections': cls.COLLECTIONS,
            'indexes': cls.INDEXES,
            'security_rules': cls.SECURITY_RULES
        }
