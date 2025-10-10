"""
API v1 routes module for RCM SaaS Application
"""

from flask import Blueprint, jsonify
from .patients import patients_bp
from .claims import claims_bp
from .health import health_bp
from .preauthprocess import preauthprocess_bp

# Create main v1 blueprint
v1_bp = Blueprint('v1', __name__)

# Register route blueprints
v1_bp.register_blueprint(patients_bp, url_prefix='/patients')
v1_bp.register_blueprint(claims_bp, url_prefix='/claims')
v1_bp.register_blueprint(health_bp, url_prefix='/health')
v1_bp.register_blueprint(preauthprocess_bp, url_prefix='/preauth-process')

# API Documentation endpoint
@v1_bp.route('/', methods=['GET'])
def api_documentation():
    """API v1 documentation endpoint"""
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
            },
            'preauth-process': {
                'base_url': '/api/v1/preauth-process',
                'methods': {
                    'POST /submit': 'Submit a new preauth request (starts with Preauth Registered status)',
                    'PUT /update-status': 'Update preauth status based on user role',
                    'GET /status-history/<preauth_id>': 'Get status history for a preauth request',
                    'GET /current-status/<preauth_id>': 'Get current status and allowed transitions',
                    'GET /list': 'List preauth requests with filtering options',
                    'POST /submit-discharge': 'Submit discharge information for approved preauth'
                },
                'roles': {
                    'preauth_executive': 'Can transition: Preauth Registered -> Need More Info/Preauth Approved/Preauth Denial, Need More Info -> Info Submitted, Discharge Submitted -> Discharge NMI/Discharge Approved/Discharge Denial, Discharge NMI -> Discharge NMI Submitted',
                    'processor': 'Can transition: Preauth Registered -> Need More Info/Preauth Approved/Preauth Denial, Discharge Submitted -> Discharge NMI/Discharge Approved/Discharge Denial'
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
