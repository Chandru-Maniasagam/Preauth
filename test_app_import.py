#!/usr/bin/env python3
"""
Test app import for Gunicorn compatibility
"""

import sys
import os

def test_app_import():
    """Test importing the app for Gunicorn"""
    print("Testing app import...")
    
    try:
        # Test importing from app.main
        from app.main import app
        print("✅ Successfully imported app from app.main")
        print(f"   App type: {type(app)}")
        print(f"   App name: {app.name}")
        return True
    except Exception as e:
        print(f"❌ Failed to import app from app.main: {e}")
        return False

def test_app_init():
    """Test importing from app module"""
    print("\nTesting app module import...")
    
    try:
        import app
        if hasattr(app, 'app') and app.app is not None:
            print("✅ Successfully imported app from app module")
            print(f"   App type: {type(app.app)}")
            print(f"   App name: {app.app.name}")
            return True
        else:
            print("❌ app module has no 'app' attribute or it's None")
            return False
    except Exception as e:
        print(f"❌ Failed to import app module: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Testing Gunicorn App Import")
    print("=" * 40)
    
    success1 = test_app_import()
    success2 = test_app_init()
    
    print("\n" + "=" * 40)
    if success1 and success2:
        print("🎉 All tests passed! App is ready for Gunicorn.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        sys.exit(1)
