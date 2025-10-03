#!/usr/bin/env python3
"""
WSGI entry point for Gunicorn
This file provides a simple way for Gunicorn to import the Flask app
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and create the Flask app
from app.main import create_app

# Create the WSGI application
application = create_app()

# Also expose as 'app' for compatibility
app = application

if __name__ == "__main__":
    application.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))


