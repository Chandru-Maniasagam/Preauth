"""
Firebase configuration for RCM SaaS Application
"""

import os
import json
from typing import Dict, Any


class FirebaseConfig:
    """Firebase configuration settings"""
    
    # Project Configuration
    PROJECT_ID = "mv20-a1a09"
    PROJECT_NUMBER = "476791140012"
    WEB_API_KEY = "AIzaSyAaqgkXJXkntZBs7QQyss7Hy_HECyMXE2c"
    
    # Storage Configuration
    STORAGE_BUCKET = "gs://mv20-a1a09.firebasestorage.app"
    
    # Service Account Key Path
    SERVICE_ACCOUNT_KEY_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "ServiceAccountKey.json"
    )
    
    @classmethod
    def get_service_account_credentials(cls):
        """Get service account credentials from environment variable or file"""
        # First try to get from environment variable (for production deployment)
        service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY')
        if service_account_json:
            try:
                return json.loads(service_account_json)
            except json.JSONDecodeError:
                pass
        
        # Fallback to file path (for local development)
        if os.path.exists(cls.SERVICE_ACCOUNT_KEY_PATH):
            with open(cls.SERVICE_ACCOUNT_KEY_PATH, 'r') as f:
                return json.load(f)
        
        # If neither is available, return None
        return None
    
    # Database Configuration
    DATABASE_URL = f"https://{PROJECT_ID}-default-rtdb.firebaseio.com/"
    
    # Firestore Configuration
    FIRESTORE_DATABASE_ID = "(default)"
    
    @classmethod
    def get_firebase_config(cls) -> Dict[str, Any]:
        """Get Firebase configuration dictionary"""
        return {
            "projectId": cls.PROJECT_ID,
            "storageBucket": cls.STORAGE_BUCKET,
            "databaseURL": cls.DATABASE_URL,
            "serviceAccount": cls.SERVICE_ACCOUNT_KEY_PATH
        }
    
    @classmethod
    def get_firestore_config(cls) -> Dict[str, Any]:
        """Get Firestore configuration dictionary"""
        return {
            "project_id": cls.PROJECT_ID,
            "database_id": cls.FIRESTORE_DATABASE_ID,
            "credentials": cls.SERVICE_ACCOUNT_KEY_PATH
        }
