#!/usr/bin/env python3
"""
Test WSGI entry point
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_wsgi():
    """Test WSGI import"""
    try:
        from wsgi import application, app
        print("✅ Successfully imported WSGI application")
        print(f"   Application type: {type(application)}")
        print(f"   App type: {type(app)}")
        print(f"   App name: {application.name}")
        return True
    except Exception as e:
        print(f"❌ Failed to import WSGI application: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Testing WSGI Entry Point")
    print("=" * 40)
    
    if test_wsgi():
        print("🎉 WSGI entry point is ready!")
        sys.exit(0)
    else:
        print("⚠️  WSGI entry point has issues.")
        sys.exit(1)
