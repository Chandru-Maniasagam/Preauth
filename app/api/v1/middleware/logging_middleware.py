"""
Logging middleware for RCM SaaS Application
"""

from functools import wraps
from flask import request, g
import logging
import time
from datetime import datetime
import json


def log_requests(f):
    """Decorator to log API requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Start timing
        start_time = time.time()
        
        # Log request
        request_id = g.get('request_id', 'unknown')
        user_id = getattr(g, 'current_user_id', 'anonymous')
        hospital_id = getattr(g, 'current_hospital_id', 'unknown')
        
        request_log = {
            'request_id': request_id,
            'method': request.method,
            'url': request.url,
            'user_id': user_id,
            'hospital_id': hospital_id,
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr,
            'timestamp': datetime.utcnow().isoformat(),
            'content_type': request.content_type,
            'content_length': request.content_length
        }
        
        # Log request body for non-GET requests (excluding sensitive data)
        if request.method != 'GET' and request.is_json:
            body = request.get_json()
            # Remove sensitive fields
            if isinstance(body, dict):
                sensitive_fields = ['password', 'password_hash', 'token', 'secret', 'key']
                filtered_body = {k: v for k, v in body.items() if k not in sensitive_fields}
                request_log['request_body'] = filtered_body
        
        logging.info(f"API Request: {json.dumps(request_log)}")
        
        # Execute the function
        try:
            response = f(*args, **kwargs)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Log response
            response_log = {
                'request_id': request_id,
                'status_code': response[1] if isinstance(response, tuple) else 200,
                'response_time_ms': round(response_time * 1000, 2),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logging.info(f"API Response: {json.dumps(response_log)}")
            
            return response
            
        except Exception as e:
            # Calculate response time
            response_time = time.time() - start_time
            
            # Log error
            error_log = {
                'request_id': request_id,
                'error': str(e),
                'error_type': type(e).__name__,
                'response_time_ms': round(response_time * 1000, 2),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logging.error(f"API Error: {json.dumps(error_log)}")
            
            raise
    
    return decorated_function


def log_audit_event(action, resource_type, resource_id, old_values=None, new_values=None, metadata=None):
    """Log audit event"""
    user_id = getattr(g, 'current_user_id', 'system')
    hospital_id = getattr(g, 'current_hospital_id', 'unknown')
    request_id = g.get('request_id', 'unknown')
    
    audit_log = {
        'request_id': request_id,
        'user_id': user_id,
        'hospital_id': hospital_id,
        'action': action,
        'resource_type': resource_type,
        'resource_id': resource_id,
        'old_values': old_values or {},
        'new_values': new_values or {},
        'metadata': metadata or {},
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    logging.info(f"Audit Event: {json.dumps(audit_log)}")


def log_security_event(event_type, description, severity='medium', metadata=None):
    """Log security event"""
    user_id = getattr(g, 'current_user_id', 'anonymous')
    hospital_id = getattr(g, 'current_hospital_id', 'unknown')
    request_id = g.get('request_id', 'unknown')
    
    security_log = {
        'request_id': request_id,
        'user_id': user_id,
        'hospital_id': hospital_id,
        'event_type': event_type,
        'description': description,
        'severity': severity,
        'metadata': metadata or {},
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if severity == 'high' or severity == 'critical':
        logging.error(f"Security Event: {json.dumps(security_log)}")
    else:
        logging.warning(f"Security Event: {json.dumps(security_log)}")


def log_performance_metric(metric_name, value, unit='ms', metadata=None):
    """Log performance metric"""
    user_id = getattr(g, 'current_user_id', 'system')
    hospital_id = getattr(g, 'current_hospital_id', 'unknown')
    request_id = g.get('request_id', 'unknown')
    
    performance_log = {
        'request_id': request_id,
        'user_id': user_id,
        'hospital_id': hospital_id,
        'metric_name': metric_name,
        'value': value,
        'unit': unit,
        'metadata': metadata or {},
        'timestamp': datetime.utcnow().isoformat()
    }
    
    logging.info(f"Performance Metric: {json.dumps(performance_log)}")


def log_business_event(event_type, description, data=None):
    """Log business event"""
    user_id = getattr(g, 'current_user_id', 'system')
    hospital_id = getattr(g, 'current_hospital_id', 'unknown')
    request_id = g.get('request_id', 'unknown')
    
    business_log = {
        'request_id': request_id,
        'user_id': user_id,
        'hospital_id': hospital_id,
        'event_type': event_type,
        'description': description,
        'data': data or {},
        'timestamp': datetime.utcnow().isoformat()
    }
    
    logging.info(f"Business Event: {json.dumps(business_log)}")


def setup_logging(app):
    """Setup logging configuration for the application"""
    
    # Configure logging level
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    app.logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    log_file = app.config.get('LOG_FILE')
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
    
    # Add request ID to all log messages
    @app.before_request
    def add_request_id():
        import uuid
        g.request_id = str(uuid.uuid4())
    
    # Log all requests
    @app.before_request
    def log_request():
        if not request.path.startswith('/health'):
            log_audit_event(
                action='request',
                resource_type='api',
                resource_id=request.endpoint or 'unknown',
                metadata={
                    'method': request.method,
                    'url': request.url,
                    'endpoint': request.endpoint
                }
            )
