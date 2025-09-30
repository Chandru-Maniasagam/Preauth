"""
Authentication middleware for RCM SaaS Application
"""

from functools import wraps
from flask import request, jsonify, g
import jwt
from datetime import datetime
import logging

from app.config import AppConfig


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401
        
        if not token:
            return jsonify({'error': 'Authorization token is missing'}), 401
        
        try:
            # Decode the token
            data = jwt.decode(token, AppConfig.JWT_SECRET_KEY, algorithms=['HS256'])
            current_user_id = data['user_id']
            current_hospital_id = data['hospital_id']
            current_user_role = data['role']
            
            # Store user info in g for use in the route
            g.current_user_id = current_user_id
            g.current_hospital_id = current_hospital_id
            g.current_user_role = current_user_role
            
            # Add headers for backward compatibility
            request.headers.add('X-User-ID', current_user_id)
            request.headers.add('X-Hospital-ID', current_hospital_id)
            request.headers.add('X-User-Role', current_user_role)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_permission(permission):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user has the required permission
            if not hasattr(g, 'current_user_permissions'):
                # Get user permissions from database
                # This would typically be cached or fetched from the database
                g.current_user_permissions = get_user_permissions(g.current_user_id, g.current_hospital_id)
            
            if permission not in g.current_user_permissions:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_user_permissions(user_id, hospital_id):
    """Get user permissions from database"""
    # This is a placeholder - in a real implementation, you would:
    # 1. Query the database for user permissions
    # 2. Check role-based permissions
    # 3. Check resource-specific permissions
    
    # For now, return basic permissions based on role
    role_permissions = {
        'super_admin': [
            'hospitals:read', 'hospitals:update', 'hospitals:delete',
            'users:read', 'users:create', 'users:update', 'users:delete',
            'patients:read', 'patients:create', 'patients:update', 'patients:delete',
            'preauth:read', 'preauth:create', 'preauth:update', 'preauth:delete',
            'preauth:approve', 'preauth:reject', 'preauth:submit',
            'dashboard:read', 'reports:read', 'notifications:read'
        ],
        'admin': [
            'hospitals:read', 'hospitals:update',
            'users:read', 'users:create', 'users:update', 'users:delete',
            'patients:read', 'patients:create', 'patients:update', 'patients:delete',
            'preauth:read', 'preauth:create', 'preauth:update', 'preauth:delete',
            'preauth:approve', 'preauth:reject', 'preauth:submit',
            'dashboard:read', 'reports:read', 'notifications:read'
        ],
        'doctor': [
            'patients:read', 'patients:create', 'patients:update',
            'preauth:read', 'preauth:create', 'preauth:update',
            'dashboard:read', 'notifications:read'
        ],
        'nurse': [
            'patients:read', 'patients:update',
            'preauth:read', 'preauth:update',
            'notifications:read'
        ],
        'receptionist': [
            'patients:read', 'patients:create', 'patients:update',
            'preauth:read', 'preauth:create', 'preauth:update',
            'notifications:read'
        ],
        'billing_staff': [
            'patients:read',
            'preauth:read', 'preauth:update',
            'dashboard:read', 'reports:read', 'notifications:read'
        ],
        'insurance_coordinator': [
            'patients:read',
            'preauth:read', 'preauth:create', 'preauth:update', 'preauth:submit',
            'preauth:approve', 'preauth:reject',
            'dashboard:read', 'notifications:read'
        ],
        'user': [
            'patients:read',
            'preauth:read',
            'notifications:read'
        ]
    }
    
    # Get user role from g (set in require_auth)
    user_role = getattr(g, 'current_user_role', 'user')
    return role_permissions.get(user_role, role_permissions['user'])


def generate_token(user_id, hospital_id, role, permissions=None):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'hospital_id': hospital_id,
        'role': role,
        'permissions': permissions or [],
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow().timestamp() + AppConfig.JWT_ACCESS_TOKEN_EXPIRES
    }
    
    token = jwt.encode(payload, AppConfig.JWT_SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, AppConfig.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
