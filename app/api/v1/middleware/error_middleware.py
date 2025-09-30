"""
Error handling middleware for RCM SaaS Application
"""

from flask import jsonify, request
import logging
import traceback
from datetime import datetime


def handle_errors(app):
    """Register error handlers with Flask app"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request could not be understood or was missing required parameters',
            'status_code': 400,
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required and has failed or has not been provided',
            'status_code': 401,
            'timestamp': datetime.utcnow().isoformat()
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'The server understood the request but refuses to authorize it',
            'status_code': 403,
            'timestamp': datetime.utcnow().isoformat()
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404,
            'timestamp': datetime.utcnow().isoformat()
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'Method Not Allowed',
            'message': 'The method specified in the request is not allowed for the resource',
            'status_code': 405,
            'timestamp': datetime.utcnow().isoformat()
        }), 405
    
    @app.errorhandler(409)
    def conflict(error):
        return jsonify({
            'error': 'Conflict',
            'message': 'The request could not be completed due to a conflict with the current state of the resource',
            'status_code': 409,
            'timestamp': datetime.utcnow().isoformat()
        }), 409
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'error': 'Unprocessable Entity',
            'message': 'The request was well-formed but was unable to be followed due to semantic errors',
            'status_code': 422,
            'timestamp': datetime.utcnow().isoformat()
        }), 422
    
    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({
            'error': 'Too Many Requests',
            'message': 'Rate limit exceeded. Please try again later',
            'status_code': 429,
            'timestamp': datetime.utcnow().isoformat()
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        logging.error(f"Internal Server Error: {str(error)}")
        logging.error(traceback.format_exc())
        
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please try again later',
            'status_code': 500,
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        return jsonify({
            'error': 'Service Unavailable',
            'message': 'The server is currently unable to handle the request due to temporary overload or maintenance',
            'status_code': 503,
            'timestamp': datetime.utcnow().isoformat()
        }), 503
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logging.error(f"Unexpected error: {str(error)}")
        logging.error(traceback.format_exc())
        
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please try again later',
            'status_code': 500,
            'timestamp': datetime.utcnow().isoformat()
        }), 500


class APIException(Exception):
    """Custom API exception class"""
    
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        rv['status_code'] = self.status_code
        rv['timestamp'] = datetime.utcnow().isoformat()
        return rv


class ValidationError(APIException):
    """Validation error exception"""
    
    def __init__(self, message, field=None, payload=None):
        super().__init__(message, 400, payload)
        self.field = field


class AuthenticationError(APIException):
    """Authentication error exception"""
    
    def __init__(self, message="Authentication failed", payload=None):
        super().__init__(message, 401, payload)


class AuthorizationError(APIException):
    """Authorization error exception"""
    
    def __init__(self, message="Insufficient permissions", payload=None):
        super().__init__(message, 403, payload)


class NotFoundError(APIException):
    """Not found error exception"""
    
    def __init__(self, message="Resource not found", payload=None):
        super().__init__(message, 404, payload)


class ConflictError(APIException):
    """Conflict error exception"""
    
    def __init__(self, message="Resource conflict", payload=None):
        super().__init__(message, 409, payload)


class RateLimitError(APIException):
    """Rate limit error exception"""
    
    def __init__(self, message="Rate limit exceeded", payload=None):
        super().__init__(message, 429, payload)


def handle_api_exception(error):
    """Handle custom API exceptions"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def log_error(error, context=None):
    """Log error with context information"""
    error_info = {
        'error': str(error),
        'type': type(error).__name__,
        'timestamp': datetime.utcnow().isoformat(),
        'request_url': request.url if request else None,
        'request_method': request.method if request else None,
        'user_agent': request.headers.get('User-Agent') if request else None,
        'context': context or {}
    }
    
    logging.error(f"API Error: {error_info}")
    
    if hasattr(error, '__traceback__'):
        logging.error(traceback.format_exc())
