"""
API v1 routes module for RCM SaaS Application
"""

from flask import Blueprint, jsonify
from .patients import patients_bp
from .claims import claims_bp

# Create main v1 blueprint
v1_bp = Blueprint('v1', __name__)

# Register route blueprints
v1_bp.register_blueprint(patients_bp, url_prefix='/patients')
v1_bp.register_blueprint(claims_bp, url_prefix='/claims')

# API Documentation endpoint
@v1_bp.route('/', methods=['GET', 'POST', 'OPTIONS'])
def api_documentation():
    """API v1 documentation endpoint"""
    from flask import request
    
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    # Handle POST requests - redirect to appropriate endpoint
    if request.method == 'POST':
        return jsonify({
            'error': 'Invalid endpoint',
            'message': 'POST requests to /api/v1/ are not supported. Please use specific endpoints like /api/v1/patients/ or /api/v1/claims/',
            'available_endpoints': {
                'patients': '/api/v1/patients/',
                'claims': '/api/v1/claims/'
            }
        }), 400
    
    # Handle GET requests - return documentation
    return jsonify({
        'message': 'RCM SaaS Application API v1',
        'version': '1.0.0',
        'status': 'active',
        'endpoints': {
            'patients': {
                'base_url': '/api/v1/patients',
                'methods': {
                    'POST /': 'Create a new patient',
                    'GET /': 'Get all patients (with pagination)',
                    'GET /<uhid>': 'Get patient by UHID',
                    'GET /search/mobile/<mobile>': 'Search patient by mobile number',
                    'GET /states': 'Get list of Indian states',
                    'GET /pincode/<pincode>': 'Get state and city from pincode',
                    'GET /payers': 'Get list of payers',
                    'GET /corporates': 'Get list of corporate clients'
                }
            },
            'claims': {
                'base_url': '/api/v1/claims',
                'methods': {
                    'POST /': 'Create a new claim draft',
                    'GET /': 'Get all claims (with pagination and filtering)',
                    'GET /<claim_id>': 'Get claim by ID',
                    'PUT /<claim_id>': 'Update claim draft',
                    'POST /submit/<claim_id>': 'Submit claim for processing',
                    'GET /specialities': 'Get all available specialities',
                    'GET /doctors': 'Get doctors by hospital and speciality',
                    'GET /doctor-details/<doctor_id>': 'Get doctor details by ID',
                    'GET /payers': 'Get list of payers'
                }
            },
            'health': {
                'base_url': '/health',
                'methods': {
                    'GET /': 'Health check endpoint'
                }
            }
        },
        'authentication': {
            'note': 'Authentication middleware is currently disabled for development',
            'headers': {
                'X-Hospital-ID': 'Required for most endpoints',
                'X-User-ID': 'User identifier for audit logging',
                'X-User-Name': 'User name for audit logging'
            }
        },
        'documentation': {
            'swagger': 'Coming soon',
            'postman_collection': 'Coming soon'
        }
    }), 200
