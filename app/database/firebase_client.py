"""
Firebase client for RCM SaaS Application
"""

import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional, Dict, Any
import logging

from app.config import FirebaseConfig


class FirebaseClient:
    """Firebase client for database and storage operations"""
    
    def __init__(self):
        self.app: Optional[firebase_admin.App] = None
        self.db: Optional[firestore.Client] = None
        self.bucket: Optional[Any] = None
        self._initialize_firebase()
    
    def _initialize_firebase(self) -> None:
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase app is already initialized
            if not firebase_admin._apps:
                # Get service account credentials
                service_account_info = FirebaseConfig.get_service_account_credentials()
                
                if service_account_info:
                    cred = credentials.Certificate(service_account_info)
                    self.app = firebase_admin.initialize_app(cred, {
                        'storageBucket': FirebaseConfig.STORAGE_BUCKET
                    })
                else:
                    logging.warning("No Firebase service account credentials found")
                    return
            else:
                self.app = firebase_admin.get_app()
            
            # Initialize Firestore client
            self.db = firestore.client()
            
            # Initialize Storage client using Firebase Admin SDK
            from firebase_admin import storage as firebase_storage
            self.bucket = firebase_storage.bucket()
            
            logging.info("Firebase initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize Firebase: {str(e)}")
            # Don't raise the error during import, just log it
            pass
    
    def get_firestore_client(self) -> firestore.Client:
        """Get Firestore client"""
        if self.db is None:
            raise RuntimeError("Firebase not initialized")
        return self.db
    
    def is_initialized(self) -> bool:
        """Check if Firebase is properly initialized"""
        return self.db is not None and self.app is not None
    
    def get_storage_bucket(self) -> Any:
        """Get Storage bucket"""
        if self.bucket is None:
            raise RuntimeError("Firebase not initialized")
        return self.bucket
    
    def health_check(self) -> Dict[str, Any]:
        """Check Firebase connection health"""
        try:
            # Test Firestore connection
            test_collection = self.db.collection('health_check')
            test_doc = test_collection.document('test')
            test_doc.set({'timestamp': firestore.SERVER_TIMESTAMP})
            test_doc.delete()
            
            return {
                'status': 'healthy',
                'firestore': 'connected',
                'storage': 'connected' if self.bucket else 'not_connected'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
