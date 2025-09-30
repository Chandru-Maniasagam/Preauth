"""
Patient routes for RCM SaaS Application
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date
import uuid
import requests
from typing import Dict, Any, List, Optional
import logging

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.api.v1.middleware.auth_middleware import require_auth, require_permission
from app.api.v1.middleware.validation_middleware import validate_json
from app.database.firebase_client import FirebaseClient
from app.database.models.patient import Patient
from app.utils.validators import validate_indian_phone_number, validate_email, validate_pincode
from app.utils.helpers import generate_patient_id, calculate_age

patients_bp = Blueprint('patients', __name__)

# Firebase client will be initialized when needed
firebase_client = None
db = None

def get_db():
    """Get Firestore database client"""
    global db, firebase_client
    if db is None:
        firebase_client = FirebaseClient()
        db = firebase_client.get_firestore_client()
    return db


@patients_bp.route('/', methods=['POST'])
# @require_auth
# @require_permission('patients:create')
@validate_json(['name', 'mobile', 'uhid', 'gender', 'dob', 'address', 'state', 'city', 'pincode'])
def create_patient():
    """Create a new patient with comprehensive validation"""
    try:
        hospital_id = request.headers.get('X-Hospital-ID', 'HOSP_001')  # Default hospital for testing
        user_id = request.headers.get('X-User-ID', 'test_user')
        user_name = request.headers.get('X-User-Name', 'Test User')
        data = request.get_json()
        
        # Validate mandatory fields
        validation_errors = validate_patient_data(data)
        if validation_errors:
            return jsonify({
                'error': 'Validation failed',
                'details': validation_errors
            }), 400
        
        # Check if UHID already exists
        if check_uhid_exists(data['uhid']):
            return jsonify({
                'error': 'UHID already exists',
                'message': f"Patient with UHID {data['uhid']} already exists"
            }), 409
        
        # Validate external API data
        state_city_validation = validate_state_city_pincode(data['pincode'], data['state'], data['city'])
        if not state_city_validation['valid']:
            return jsonify({
                'error': 'Address validation failed',
                'details': state_city_validation['message']
            }), 400
        
        # Validate optional fields if provided
        optional_validation = validate_optional_fields(data)
        if optional_validation['errors']:
            return jsonify({
                'error': 'Optional field validation failed',
                'details': optional_validation['errors']
            }), 400
        
        # Calculate age from DOB
        age = calculate_age(data['dob'])
        
        # Generate patient ID
        patient_id = generate_patient_id(hospital_id)
        
        # Create patient object
        patient_data = {
            'uhid': data['uhid'],
            'hospital_id': hospital_id,  # Optional hospital assignment
            'patient_id': patient_id,
            'first_name': data['name'].split(' ')[0] if ' ' in data['name'] else data['name'],
            'last_name': data['name'].split(' ')[1] if ' ' in data['name'] else '',
            'date_of_birth': data['dob'],
            'age': age,
            'gender': data['gender'],
            'phone_number': data['mobile'],
            'email': data.get('email', ''),
            'abha_id': data.get('abha_id', ''),
            'alternative_mobile': data.get('alternative_mobile', ''),
            'occupation': data.get('occupation', ''),
            'policy_number': data.get('policy_number', ''),
            'corporate_name': data.get('corporate_name', ''),
            'employee_id': data.get('employee_id', ''),
            'payer_type': data.get('payer_type', ''),
            'payer_name': data.get('payer_name', ''),
            'insurer_name': data.get('insurer_name', ''),
            'past_medical_history': data.get('past_medical_history', []),
            'duration_of_past_history': data.get('duration_of_past_history', {}),
            'smoker': data.get('smoker', 'NO'),
            'alcohol': data.get('alcohol', 'NO'),
            'past_claims': data.get('past_claims', []),
            'address': {
                'street': data['address'],
                'city': data['city'],
                'state': data['state'],
                'pincode': data['pincode'],
                'country': 'India'
            },
            'created_by': user_id,
            'updated_by': user_id,
            'created_by_name': user_name,
            'updated_by_name': user_name,
            'is_active': True
        }
        
        # Create patient in database
        patient = Patient(**patient_data)
        
        # Save to Firestore using UHID as document ID
        db = get_db()
        patient_ref = db.collection('patients').document(data['uhid'])
        patient_ref.set(patient.to_dict())
        
        # Log the creation
        log_patient_creation(patient.id, hospital_id, user_id, user_name)
        
        return jsonify({
            'message': 'Patient created successfully',
            'patient_id': patient.id,
            'uhid': patient.uhid,
            'patient_data': {
                'name': f"{patient.first_name} {patient.last_name}".strip(),
                'uhid': patient.uhid,
                'age': age,
                'gender': patient.gender,
                'mobile': patient.phone_number,
                'created_at': patient.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        logging.error(f"Error creating patient: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to create patient'
        }), 500


@patients_bp.route('/<uhid>', methods=['GET'])
# @require_auth
# @require_permission('patients:read')
def get_patient(uhid):
    """Get patient by UHID"""
    try:
        # Get patient from database using UHID as document ID
        db = get_db()
        patient_ref = db.collection('patients').document(uhid)
        patient_doc = patient_ref.get()
        
        if not patient_doc.exists:
            return jsonify({'error': 'Patient not found'}), 404
        
        patient_data = patient_doc.to_dict()
        
        return jsonify({
            'patient': patient_data
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting patient: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@patients_bp.route('/search/mobile/<mobile>', methods=['GET'])
# @require_auth
# @require_permission('patients:read')
def get_patient_by_mobile(mobile):
    """Get patient by mobile number (10 digits without country code)"""
    try:
        # Clean mobile number - remove country code and non-digits
        clean_mobile = ''.join(filter(str.isdigit, mobile))
        if len(clean_mobile) > 10:
            clean_mobile = clean_mobile[-10:]  # Take last 10 digits
        
        # Search for patients with this mobile number
        db = get_db()
        patients_ref = db.collection('patients')
        query = patients_ref.where('phone_number', '>=', f'+91 {clean_mobile}').where('phone_number', '<=', f'+91 {clean_mobile}\uf8ff')
        results = list(query.stream())
        
        # Also search for exact match
        if not results:
            query = patients_ref.where('phone_number', '==', f'+91 {clean_mobile}')
            results = list(query.stream())
        
        if not results:
            return jsonify({'error': 'Patient not found'}), 404
        
        patients = [doc.to_dict() for doc in results]
        
        return jsonify({
            'patients': patients
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting patient by mobile: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@patients_bp.route('/', methods=['GET'])
# @require_auth
# @require_permission('patients:read')
def get_patients():
    """Get all patients with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '')
        
        # Build query
        db = get_db()
        patients_ref = db.collection('patients')
        query = patients_ref.where('is_active', '==', True)
        
        # Apply search filter if provided
        if search:
            # Note: Firestore doesn't support full-text search, so we'll filter in memory
            # In production, consider using Algolia or Elasticsearch
            pass
        
        # Get total count
        total_docs = list(query.stream())
        total_count = len(total_docs)
        
        # Apply pagination
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        
        # Get paginated results
        paginated_docs = total_docs[start_index:end_index]
        
        patients = []
        for doc in paginated_docs:
            patient_data = doc.to_dict()
            if not search or search.lower() in patient_data.get('first_name', '').lower() or \
               search.lower() in patient_data.get('last_name', '').lower() or \
               search.lower() in patient_data.get('uhid', '').lower():
                patients.append(patient_data)
        
        return jsonify({
            'patients': patients,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page,
                'has_next': end_index < total_count,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting patients: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@patients_bp.route('/states', methods=['GET'])
# @require_auth
def get_indian_states():
    """Get list of Indian states from external API"""
    try:
        # Using a free Indian states API
        response = requests.get('https://api.countrystatecity.in/v1/countries/IN/states', 
                              headers={'X-CSCAPI-KEY': 'YOUR_API_KEY'}, timeout=10)
        
        if response.status_code == 200:
            states = response.json()
            return jsonify({
                'states': [{'code': state['iso2'], 'name': state['name']} for state in states]
            }), 200
        else:
            # Fallback to static list if API fails
            return jsonify({
                'states': get_static_indian_states()
            }), 200
            
    except Exception as e:
        logging.error(f"Error fetching states: {str(e)}")
        # Return static list as fallback
        return jsonify({
            'states': get_static_indian_states()
        }), 200


@patients_bp.route('/pincode/<pincode>', methods=['GET'])
# @require_auth
def get_pincode_details(pincode):
    """Get state and city details from pincode"""
    try:
        # Using a free pincode API
        response = requests.get(f'https://api.postalpincode.in/pincode/{pincode}', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and data[0]['Status'] == 'Success':
                post_office = data[0]['PostOffice'][0]
                return jsonify({
                    'pincode': pincode,
                    'state': post_office['State'],
                    'city': post_office['District'],
                    'area': post_office['Name']
                }), 200
            else:
                return jsonify({'error': 'Invalid pincode'}), 400
        else:
            return jsonify({'error': 'Pincode service unavailable'}), 503
            
    except Exception as e:
        logging.error(f"Error fetching pincode details: {str(e)}")
        return jsonify({'error': 'Pincode service error'}), 500


@patients_bp.route('/payers', methods=['GET'])
# @require_auth
def get_payers():
    """Get list of payers from database"""
    try:
        hospital_id = request.headers.get('X-Hospital-ID', 'HOSP_001')
        payer_type = request.args.get('type', '')
        
        # Query payers collection
        db = get_db()
        payers_ref = db.collection('payers')
        query = payers_ref.where('hospital_id', '==', hospital_id).where('is_active', '==', True)
        
        if payer_type:
            query = query.where('payer_type', '==', payer_type)
        
        payers = []
        for doc in query.stream():
            payer_data = doc.to_dict()
            payers.append({
                'id': doc.id,
                'name': payer_data.get('name', ''),
                'payer_type': payer_data.get('payer_type', ''),
                'code': payer_data.get('code', '')
            })
        
        return jsonify({'payers': payers}), 200
        
    except Exception as e:
        logging.error(f"Error fetching payers: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@patients_bp.route('/corporates', methods=['GET'])
# @require_auth
def get_corporates():
    """Get list of corporate clients from database"""
    try:
        hospital_id = request.headers.get('X-Hospital-ID', 'HOSP_001')
        
        # Query corporates collection
        db = get_db()
        corporates_ref = db.collection('corporates')
        query = corporates_ref.where('hospital_id', '==', hospital_id).where('is_active', '==', True)
        
        corporates = []
        for doc in query.stream():
            corporate_data = doc.to_dict()
            corporates.append({
                'id': doc.id,
                'name': corporate_data.get('name', ''),
                'code': corporate_data.get('code', '')
            })
        
        return jsonify({'corporates': corporates}), 200
        
    except Exception as e:
        logging.error(f"Error fetching corporates: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


def validate_patient_data(data: Dict[str, Any]) -> List[str]:
    """Validate mandatory patient data"""
    errors = []
    
    # Validate name
    if not data.get('name') or len(data['name'].strip()) < 2:
        errors.append('Name is required and must be at least 2 characters')
    
    # Validate mobile
    if not data.get('mobile'):
        errors.append('Mobile number is required')
    elif not validate_indian_phone_number(data['mobile']):
        errors.append('Invalid mobile number format')
    
    # Validate UHID
    if not data.get('uhid') or len(data['uhid'].strip()) < 3:
        errors.append('UHID is required and must be at least 3 characters')
    
    # Validate gender
    valid_genders = ['male', 'female', 'other', 'prefer_not_to_say']
    if not data.get('gender') or data['gender'].lower() not in valid_genders:
        errors.append('Gender is required and must be one of: ' + ', '.join(valid_genders))
    
    # Validate DOB
    if not data.get('dob'):
        errors.append('Date of birth is required')
    else:
        try:
            dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
            if dob > date.today():
                errors.append('Date of birth cannot be in the future')
        except ValueError:
            errors.append('Invalid date format. Use YYYY-MM-DD')
    
    # Validate address
    if not data.get('address') or len(data['address'].strip()) < 5:
        errors.append('Address is required and must be at least 5 characters')
    
    # Validate state
    if not data.get('state') or len(data['state'].strip()) < 2:
        errors.append('State is required')
    
    # Validate city
    if not data.get('city') or len(data['city'].strip()) < 2:
        errors.append('City is required')
    
    # Validate pincode
    if not data.get('pincode'):
        errors.append('Pincode is required')
    elif not validate_pincode(data['pincode']):
        errors.append('Invalid pincode format')
    
    return errors


def validate_optional_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate optional patient fields"""
    errors = []
    
    # Validate email if provided
    if data.get('email') and not validate_email(data['email']):
        errors.append('Invalid email format')
    
    # Validate alternative mobile if provided
    if data.get('alternative_mobile') and not validate_indian_phone_number(data['alternative_mobile']):
        errors.append('Invalid alternative mobile number format')
    
    # Validate ABHA ID if provided
    if data.get('abha_id') and len(data['abha_id'].strip()) < 10:
        errors.append('ABHA ID must be at least 10 characters')
    
    # Validate smoker and alcohol values
    if data.get('smoker') and data['smoker'].upper() not in ['YES', 'NO']:
        errors.append('Smoker must be YES or NO')
    
    if data.get('alcohol') and data['alcohol'].upper() not in ['YES', 'NO']:
        errors.append('Alcohol must be YES or NO')
    
    return {'errors': errors, 'valid': len(errors) == 0}


def validate_state_city_pincode(pincode: str, state: str, city: str) -> Dict[str, Any]:
    """Validate state and city against pincode"""
    try:
        # This would typically call an external API
        # For now, we'll do basic validation
        if len(pincode) != 6 or not pincode.isdigit():
            return {'valid': False, 'message': 'Invalid pincode format'}
        
        # In a real implementation, you would call the pincode API here
        return {'valid': True, 'message': 'Address validated successfully'}
        
    except Exception as e:
        return {'valid': False, 'message': f'Address validation error: {str(e)}'}


def check_uhid_exists(uhid: str) -> bool:
    """Check if UHID already exists"""
    try:
        db = get_db()
        patient_ref = db.collection('patients').document(uhid)
        patient_doc = patient_ref.get()
        return patient_doc.exists
    except Exception:
        return False


def log_patient_creation(patient_id: str, hospital_id: str, user_id: str, user_name: str):
    """Log patient creation for audit trail"""
    try:
        audit_log = {
            'id': str(uuid.uuid4()),
            'hospital_id': hospital_id,
            'user_id': user_id,
            'action': 'create_patient',
            'resource_type': 'patient',
            'resource_id': patient_id,
            'new_values': {'created_by': user_name},
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'timestamp': datetime.utcnow().isoformat(),
            'created_at': datetime.utcnow(),
            'is_active': True
        }
        
        db = get_db()
        db.collection('audit_logs').add(audit_log)
    except Exception as e:
        logging.error(f"Error logging patient creation: {str(e)}")


def get_static_indian_states() -> List[Dict[str, str]]:
    """Fallback static list of Indian states"""
    return [
        {'code': 'AP', 'name': 'Andhra Pradesh'},
        {'code': 'AR', 'name': 'Arunachal Pradesh'},
        {'code': 'AS', 'name': 'Assam'},
        {'code': 'BR', 'name': 'Bihar'},
        {'code': 'CT', 'name': 'Chhattisgarh'},
        {'code': 'GA', 'name': 'Goa'},
        {'code': 'GJ', 'name': 'Gujarat'},
        {'code': 'HR', 'name': 'Haryana'},
        {'code': 'HP', 'name': 'Himachal Pradesh'},
        {'code': 'JK', 'name': 'Jammu and Kashmir'},
        {'code': 'JH', 'name': 'Jharkhand'},
        {'code': 'KA', 'name': 'Karnataka'},
        {'code': 'KL', 'name': 'Kerala'},
        {'code': 'MP', 'name': 'Madhya Pradesh'},
        {'code': 'MH', 'name': 'Maharashtra'},
        {'code': 'MN', 'name': 'Manipur'},
        {'code': 'ML', 'name': 'Meghalaya'},
        {'code': 'MZ', 'name': 'Mizoram'},
        {'code': 'NL', 'name': 'Nagaland'},
        {'code': 'OR', 'name': 'Odisha'},
        {'code': 'PB', 'name': 'Punjab'},
        {'code': 'RJ', 'name': 'Rajasthan'},
        {'code': 'SK', 'name': 'Sikkim'},
        {'code': 'TN', 'name': 'Tamil Nadu'},
        {'code': 'TG', 'name': 'Telangana'},
        {'code': 'TR', 'name': 'Tripura'},
        {'code': 'UP', 'name': 'Uttar Pradesh'},
        {'code': 'UT', 'name': 'Uttarakhand'},
        {'code': 'WB', 'name': 'West Bengal'},
        {'code': 'AN', 'name': 'Andaman and Nicobar Islands'},
        {'code': 'CH', 'name': 'Chandigarh'},
        {'code': 'DN', 'name': 'Dadra and Nagar Haveli'},
        {'code': 'DD', 'name': 'Daman and Diu'},
        {'code': 'DL', 'name': 'Delhi'},
        {'code': 'LD', 'name': 'Lakshadweep'},
        {'code': 'PY', 'name': 'Puducherry'}
    ]
