"""
API v1 routes module for RCM SaaS Application
"""

from flask import Blueprint
from .patients import patients_bp
from .claims import claims_bp

# Create main v1 blueprint
v1_bp = Blueprint('v1', __name__)

# Register route blueprints
v1_bp.register_blueprint(patients_bp, url_prefix='/patients')
v1_bp.register_blueprint(claims_bp, url_prefix='/claims')
