"""
Health check routes for debugging
"""

from flask import Blueprint, jsonify
from datetime import datetime
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('/simple', methods=['GET'])
def simple_health():
    """Simple health check without Firebase dependency"""
    try:
        return jsonify({
            'status': 'healthy',
            'message': 'Simple health check working',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': os.environ.get('FLASK_ENV', 'unknown')
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'type': type(e).__name__
        }), 500

@health_bp.route('/env', methods=['GET'])
def check_env():
    """Check environment variables"""
    try:
        env_vars = {
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'not_set'),
            'FIREBASE_PROJECT_ID': os.environ.get('FIREBASE_PROJECT_ID', 'not_set'),
            'FIREBASE_STORAGE_BUCKET': os.environ.get('FIREBASE_STORAGE_BUCKET', 'not_set'),
            'HAS_SERVICE_ACCOUNT_KEY': bool(os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY')),
            'SERVICE_ACCOUNT_KEY_LENGTH': len(os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY', '')) if os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY') else 0
        }
        
        return jsonify({
            'status': 'success',
            'environment_variables': env_vars
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'type': type(e).__name__
        }), 500
