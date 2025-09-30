#!/usr/bin/env python3
"""
Test script to verify deployment configuration
Run this locally to check if all dependencies are available
"""

import sys
import os

def test_imports():
    """Test all critical imports"""
    print("Testing critical imports...")
    
    try:
        # Test Flask and extensions
        from flask import Flask
        from flask_cors import CORS
        from flask_limiter import Limiter
        print("✅ Flask and extensions imported successfully")
        
        # Test Firebase
        import firebase_admin
        from firebase_admin import credentials, firestore
        print("✅ Firebase Admin SDK imported successfully")
        
        # Test phone number validation
        import phonenumbers
        from phonenumbers import NumberParseException
        print("✅ Phone numbers library imported successfully")
        
        # Test other dependencies
        import jsonschema
        import jwt
        import requests
        import cryptography
        print("✅ Other dependencies imported successfully")
        
        # Test application modules
        from app.main import create_app
        print("✅ Application modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_app_creation():
    """Test Flask app creation"""
    print("\nTesting Flask app creation...")
    
    try:
        from app.main import create_app
        app = create_app()
        
        if app:
            print("✅ Flask app created successfully")
            print(f"   - App name: {app.name}")
            print(f"   - Debug mode: {app.debug}")
            print(f"   - Secret key configured: {'Yes' if app.config.get('SECRET_KEY') else 'No'}")
            return True
        else:
            print("❌ Flask app creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Flask app creation error: {e}")
        return False

def test_firebase_config():
    """Test Firebase configuration"""
    print("\nTesting Firebase configuration...")
    
    try:
        from app.config.firebase_config import FirebaseConfig
        
        # Test service account credentials
        credentials = FirebaseConfig.get_service_account_credentials()
        if credentials:
            print("✅ Firebase service account credentials found")
            print(f"   - Project ID: {credentials.get('project_id', 'Unknown')}")
        else:
            print("⚠️  Firebase service account credentials not found (expected for local test)")
        
        print(f"   - Project ID: {FirebaseConfig.PROJECT_ID}")
        print(f"   - Storage Bucket: {FirebaseConfig.STORAGE_BUCKET}")
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase configuration error: {e}")
        return False

def test_environment_variables():
    """Test environment variable configuration"""
    print("\nTesting environment variables...")
    
    required_vars = [
        'FLASK_ENV',
        'SECRET_KEY',
        'JWT_SECRET_KEY',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_STORAGE_BUCKET',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   These should be set in Render deployment")
    else:
        print("✅ All required environment variables are set")
    
    return len(missing_vars) == 0

def main():
    """Run all tests"""
    print("🚀 RCM SaaS Application - Deployment Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_app_creation,
        test_firebase_config,
        test_environment_variables
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix issues before deployment.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
