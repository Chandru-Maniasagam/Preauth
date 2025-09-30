"""
API module for RCM SaaS Application
"""

from flask import Blueprint

# Create main API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import all API versions
from .v1 import v1_bp

# Register API versions
api_bp.register_blueprint(v1_bp, url_prefix='/v1')
