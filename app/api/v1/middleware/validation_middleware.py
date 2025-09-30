"""
Validation middleware for RCM SaaS Application
"""

from functools import wraps
from flask import request, jsonify
import jsonschema
from jsonschema import validate, ValidationError
import logging


def validate_json(required_fields=None):
    """Decorator to validate JSON request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body is empty'}), 400
            
            # Check required fields
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in data or data[field] is None or data[field] == '':
                        missing_fields.append(field)
                
                if missing_fields:
                    return jsonify({
                        'error': 'Missing required fields',
                        'missing_fields': missing_fields
                    }), 400
            
            # Store validated data in request context
            request.validated_data = data
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_request(schema):
    """Decorator to validate request against JSON schema"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body is empty'}), 400
            
            try:
                validate(instance=data, schema=schema)
            except ValidationError as e:
                return jsonify({
                    'error': 'Validation failed',
                    'details': e.message,
                    'path': list(e.absolute_path) if e.absolute_path else []
                }), 400
            
            # Store validated data in request context
            request.validated_data = data
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Common validation schemas
PATIENT_SCHEMA = {
    "type": "object",
    "properties": {
        "first_name": {"type": "string", "minLength": 1},
        "last_name": {"type": "string", "minLength": 1},
        "date_of_birth": {"type": "string", "format": "date"},
        "gender": {"type": "string", "enum": ["male", "female", "other", "prefer_not_to_say"]},
        "phone_number": {"type": "string", "minLength": 10},
        "email": {"type": "string", "format": "email"},
        "address": {"type": "object"},
        "emergency_contact": {"type": "object"},
        "insurance_info": {"type": "object"},
        "blood_group": {"type": "string", "enum": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]},
        "height": {"type": "number", "minimum": 0},
        "weight": {"type": "number", "minimum": 0}
    },
    "required": ["first_name", "last_name", "date_of_birth", "gender", "phone_number"]
}

PREAUTH_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "patient_id": {"type": "string", "minLength": 1},
        "insurance_provider": {"type": "string", "minLength": 1},
        "policy_number": {"type": "string", "minLength": 1},
        "policy_holder_name": {"type": "string", "minLength": 1},
        "policy_holder_relation": {"type": "string", "enum": ["self", "spouse", "child", "parent", "sibling", "other"]},
        "treatment_type": {"type": "string", "minLength": 1},
        "diagnosis_code": {"type": "string", "minLength": 1},
        "procedure_codes": {"type": "array", "items": {"type": "string"}},
        "estimated_cost": {"type": "number", "minimum": 0},
        "requested_amount": {"type": "number", "minimum": 0},
        "treatment_date": {"type": "string", "format": "date"},
        "admission_date": {"type": "string", "format": "date"},
        "discharge_date": {"type": "string", "format": "date"},
        "doctor_name": {"type": "string"},
        "doctor_license": {"type": "string"},
        "room_type": {"type": "string"},
        "room_rent": {"type": "number", "minimum": 0},
        "consultation_fee": {"type": "number", "minimum": 0},
        "investigation_cost": {"type": "number", "minimum": 0},
        "medicine_cost": {"type": "number", "minimum": 0},
        "surgery_cost": {"type": "number", "minimum": 0},
        "other_costs": {"type": "number", "minimum": 0},
        "remarks": {"type": "string"},
        "priority": {"type": "string", "enum": ["low", "normal", "high", "urgent"]},
        "is_urgent": {"type": "boolean"},
        "urgent_reason": {"type": "string"}
    },
    "required": ["patient_id", "insurance_provider", "policy_number", "treatment_type", "diagnosis_code", "estimated_cost"]
}

USER_SCHEMA = {
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "first_name": {"type": "string", "minLength": 1},
        "last_name": {"type": "string", "minLength": 1},
        "phone_number": {"type": "string", "minLength": 10},
        "role": {"type": "string", "enum": ["super_admin", "admin", "doctor", "nurse", "receptionist", "billing_staff", "insurance_coordinator", "user"]},
        "department": {"type": "string"},
        "designation": {"type": "string"},
        "employee_id": {"type": "string"},
        "permissions": {"type": "array", "items": {"type": "string"}},
        "working_hours": {"type": "object"},
        "specializations": {"type": "array", "items": {"type": "string"}},
        "license_number": {"type": "string"},
        "license_expiry": {"type": "string", "format": "date"},
        "qualifications": {"type": "array", "items": {"type": "string"}},
        "experience_years": {"type": "number", "minimum": 0},
        "address": {"type": "object"},
        "emergency_contact": {"type": "object"}
    },
    "required": ["email", "first_name", "last_name", "role"]
}

NOTIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "minLength": 1},
        "message": {"type": "string", "minLength": 1},
        "type": {"type": "string", "enum": ["info", "success", "warning", "error", "urgent"]},
        "category": {"type": "string"},
        "priority": {"type": "string", "enum": ["low", "normal", "high", "urgent"]},
        "recipients": {"type": "array", "items": {"type": "string"}},
        "related_resource_type": {"type": "string"},
        "related_resource_id": {"type": "string"},
        "action_url": {"type": "string"},
        "action_text": {"type": "string"},
        "scheduled_at": {"type": "string", "format": "date-time"},
        "expires_at": {"type": "string", "format": "date-time"},
        "delivery_methods": {"type": "array", "items": {"type": "string"}},
        "metadata": {"type": "object"},
        "tags": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["title", "message", "type", "recipients"]
}


def validate_pagination_params(page, per_page, max_per_page=100):
    """Validate pagination parameters"""
    if page < 1:
        return False, "Page must be greater than 0"
    
    if per_page < 1 or per_page > max_per_page:
        return False, f"Per page must be between 1 and {max_per_page}"
    
    return True, None


def validate_date_range(date_from, date_to):
    """Validate date range parameters"""
    from datetime import datetime
    
    if date_from:
        try:
            datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        except ValueError:
            return False, "Invalid date_from format"
    
    if date_to:
        try:
            datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        except ValueError:
            return False, "Invalid date_to format"
    
    if date_from and date_to:
        if datetime.fromisoformat(date_from.replace('Z', '+00:00')) > datetime.fromisoformat(date_to.replace('Z', '+00:00')):
            return False, "date_from cannot be greater than date_to"
    
    return True, None


def sanitize_input(data):
    """Sanitize input data to prevent XSS and other attacks"""
    if isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    elif isinstance(data, str):
        # Basic XSS prevention - remove script tags and dangerous characters
        import re
        data = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', data, flags=re.IGNORECASE)
        data = re.sub(r'javascript:', '', data, flags=re.IGNORECASE)
        data = re.sub(r'on\w+\s*=', '', data, flags=re.IGNORECASE)
        return data.strip()
    else:
        return data
