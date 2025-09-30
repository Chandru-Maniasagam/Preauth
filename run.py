#!/usr/bin/env python3
"""
Application launcher script for RCM SaaS Application
Run this from the project root directory
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
