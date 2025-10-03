"""
Claim routes for RCM SaaS Application
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date
import uuid
import requests
from typing import Dict, Any, List, Optional
import logging
import re

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.api.v1.middleware.auth_middleware import require_auth, require_permission
from app.api.v1.middleware.validation_middleware import validate_json
from app.database.firebase_client import FirebaseClient
from app.database.models.claim import Claim
from app.utils.validators import validate_indian_phone_number, validate_email, validate_pincode
from app.utils.helpers import generate_claim_id, calculate_age_detailed

claims_bp = Blueprint('claims', __name__)

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


@claims_bp.route('/', methods=['POST'])
# @require_auth
# @require_permission('claims:create')
@validate_json(['patient_name', 'mobile_number', 'uhid', 'claim_type', 'admission_type'])
def create_claim_draft():
    """Create a new claim draft with mandatory fields"""
    try:
        hospital_id = request.headers.get('X-Hospital-ID', 'HOSP_001')
        user_id = request.headers.get('X-User-ID', 'test_user')
        user_name = request.headers.get('X-User-Name', 'Test User')
        data = request.get_json()
        
        # Validate mandatory fields
        validation_errors = validate_claim_mandatory_fields(data)
        if validation_errors:
            return jsonify({
                'error': 'Validation failed',
                'details': validation_errors
            }), 400
        
        # Validate hospital_id is provided
        if not hospital_id:
            return jsonify({
                'error': 'Hospital ID is required',
                'message': 'X-Hospital-ID header must be provided with a valid hospital ID'
            }), 400
        
        # Check if hospital exists in hospitals collection
        hospital_info = get_hospital_info(hospital_id)
        if hospital_info.get('name') == 'Unknown Hospital':
            return jsonify({
                'error': 'Hospital not found',
                'message': f"Hospital with ID {hospital_id} not found in hospitals collection"
            }), 404
        
        # Check if UHID exists in patients collection
        if not check_patient_exists(data['uhid']):
            return jsonify({
                'error': 'Patient not found',
                'message': f"Patient with UHID {data['uhid']} not found"
            }), 404
        
        # Generate claim ID
        claim_id = generate_claim_id(hospital_id)
        
        # Create claim object
        claim_data = {
            'claim_id': claim_id,
            'hospital_id': hospital_id,
            'hospital_name': hospital_info.get('name', 'Unknown Hospital'),
            'patient_name': data['patient_name'],
            'mobile_number': data['mobile_number'],
            'uhid': data['uhid'],
            'claim_type': data['claim_type'],
            'admission_type': data['admission_type'],
            'status': 'draft',
            'payer_type': data.get('payer_type', ''),
            'payer_name': data.get('payer_name', ''),
            'insurer_name': data.get('insurer_name', ''),
            'email_id': data.get('email_id', ''),
            'abha_id': data.get('abha_id', ''),
            'admission_datetime': data.get('admission_datetime', ''),
            'ip_number': data.get('ip_number', ''),
            'created_by': user_id,
            'updated_by': user_id,
            'created_by_name': user_name,
            'updated_by_name': user_name,
            'is_active': True
        }
        
        # Create claim in database
        claim = Claim(**claim_data)
        
        # Save to Firestore using claim_id as document ID
        db = get_db()
        claim_ref = db.collection('claims').document(claim_id)
        claim_ref.set(claim.to_dict())
        
        # Log the creation
        log_claim_creation(claim_id, hospital_id, user_id, user_name)
        
        return jsonify({
            'message': 'Claim draft created successfully',
            'claim_id': claim_id,
            'claim_number': claim_id,
            'status': 'draft',
            'claim_data': {
                'patient_name': claim.patient_name,
                'uhid': claim.uhid,
                'claim_type': claim.claim_type,
                'admission_type': claim.admission_type,
                'created_at': claim.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        logging.error(f"Error creating claim draft: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to create claim draft'
        }), 500


@claims_bp.route('/specialities', methods=['GET'])
# @require_auth
# @require_permission('claims:read')
def get_specialities():
    """Get all available specialities"""
    try:
        db = get_db()
        specialities_ref = db.collection('specialities')
        specialities = list(specialities_ref.where('is_active', '==', True).stream())
        
        specialities_list = []
        for speciality_doc in specialities:
            speciality_data = speciality_doc.to_dict()
            specialities_list.append({
                'id': speciality_data.get('id'),
                'name': speciality_data.get('name'),
                'description': speciality_data.get('description')
            })
        
        return jsonify({
            'specialities': specialities_list
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching specialities: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@claims_bp.route('/doctors', methods=['GET'])
# @require_auth
# @require_permission('claims:read')
def get_doctors():
    """Get doctors filtered by hospital and speciality"""
    try:
        hospital_id = request.headers.get('X-Hospital-ID')
        speciality_id = request.args.get('speciality_id')
        
        if not hospital_id:
            return jsonify({'error': 'Hospital ID is required'}), 400
        
        db = get_db()
        doctors_ref = db.collection('doctors')
        
        # Filter by hospital
        query = doctors_ref.where('hospital_id', '==', hospital_id).where('is_active', '==', True)
        
        # Filter by speciality if provided
        if speciality_id:
            query = query.where('speciality_id', '==', speciality_id)
        
        doctors = list(query.stream())
        
        doctors_list = []
        for doctor_doc in doctors:
            doctor_data = doctor_doc.to_dict()
            doctors_list.append({
                'id': doctor_data.get('id'),
                'name': doctor_data.get('name'),
                'contact': doctor_data.get('contact'),
                'qualification': doctor_data.get('qualification'),
                'registration_number': doctor_data.get('registration_number'),
                'speciality_id': doctor_data.get('speciality_id')
            })
        
        return jsonify({
            'doctors': doctors_list
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching doctors: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@claims_bp.route('/<claim_id>', methods=['PUT'])
# @require_auth
# @require_permission('claims:update')
def update_claim_draft(claim_id):
    """Update claim draft with optional fields"""
    try:
        hospital_id = request.headers.get('X-Hospital-ID', 'HOSP_001')
        user_id = request.headers.get('X-User-ID', 'test_user')
        user_name = request.headers.get('X-User-Name', 'Test User')
        data = request.get_json()
        
        # Get existing claim
        db = get_db()
        claim_ref = db.collection('claims').document(claim_id)
        claim_doc = claim_ref.get()
        
        if not claim_doc.exists:
            return jsonify({'error': 'Claim not found'}), 404
        
        existing_claim = claim_doc.to_dict()
        
        # Validate optional fields
        validation_errors = validate_claim_optional_fields(data)
        if validation_errors:
            return jsonify({
                'error': 'Validation failed',
                'details': validation_errors
            }), 400
        
        # Update claim with new data
        update_data = {
            'updated_by': user_id,
            'updated_by_name': user_name,
            'updated_at': datetime.utcnow()
        }
        
        # Patient Information Section
        if 'gender' in data:
            update_data['gender'] = data['gender']
        if 'date_of_birth' in data:
            update_data['date_of_birth'] = data['date_of_birth']
            # Calculate age
            age_details = calculate_age_detailed(data['date_of_birth'])
            update_data['age_years'] = age_details['years']
            update_data['age_months'] = age_details['months']
            update_data['age_days'] = age_details['days']
        if 'customer_id' in data:
            update_data['customer_id'] = data['customer_id']
        if 'alternative_contact' in data:
            update_data['alternative_contact'] = data['alternative_contact']
        if 'policy_number' in data:
            update_data['policy_number'] = data['policy_number']
        if 'employee_id' in data:
            update_data['employee_id'] = data['employee_id']
        if 'additional_policy' in data:
            update_data['additional_policy'] = data['additional_policy']
            if data['additional_policy'] and 'additional_policy_details' in data:
                update_data['additional_policy_details'] = data['additional_policy_details']
        if 'family_physician' in data:
            update_data['family_physician'] = data['family_physician']
            if data['family_physician'] and 'family_physician_details' in data:
                update_data['family_physician_details'] = data['family_physician_details']
        
        # Address Information
        if 'address' in data:
            update_data['address'] = data['address']
        if 'city' in data:
            update_data['city'] = data['city']
        if 'state' in data:
            update_data['state'] = data['state']
        if 'pincode' in data:
            update_data['pincode'] = data['pincode']
        if 'occupation' in data:
            update_data['occupation'] = data['occupation']
        
        # Treatment Information
        if 'speciality_id' in data:
            update_data['speciality_id'] = data['speciality_id']
        if 'treating_doctor_id' in data:
            update_data['treating_doctor_id'] = data['treating_doctor_id']
        if 'treating_doctor_name' in data:
            update_data['treating_doctor_name'] = data['treating_doctor_name']
        if 'treating_doctor_contact' in data:
            update_data['treating_doctor_contact'] = data['treating_doctor_contact']
        if 'nature_of_illness' in data:
            update_data['nature_of_illness'] = data['nature_of_illness']
        if 'injury_details' in data:
            update_data['injury_details'] = data['injury_details']
        if 'clinical_findings' in data:
            update_data['clinical_findings'] = data['clinical_findings']
        if 'duration_of_ailment' in data:
            update_data['duration_of_ailment'] = data['duration_of_ailment']
        if 'first_consultation_date' in data:
            update_data['first_consultation_date'] = data['first_consultation_date']
        if 'past_history_ailment' in data:
            update_data['past_history_ailment'] = data['past_history_ailment']
        if 'provisional_diagnosis' in data:
            update_data['provisional_diagnosis'] = data['provisional_diagnosis']
        if 'icd10_code' in data:
            update_data['icd10_code'] = data['icd10_code']
        if 'proposed_treatment' in data:
            update_data['proposed_treatment'] = data['proposed_treatment']
        if 'treatment_plan' in data:
            update_data['treatment_plan'] = data['treatment_plan']
        if 'drug_administration' in data:
            update_data['drug_administration'] = data['drug_administration']
        if 'injury_occurrence' in data:
            update_data['injury_occurrence'] = data['injury_occurrence']
        if 'maternity_details' in data:
            update_data['maternity_details'] = data['maternity_details']
        if 'past_medical_history' in data:
            update_data['past_medical_history'] = data['past_medical_history']
        if 'treating_doctor_qualification' in data:
            update_data['treating_doctor_qualification'] = data['treating_doctor_qualification']
        if 'treating_doctor_registration' in data:
            update_data['treating_doctor_registration'] = data['treating_doctor_registration']
        if 'ward_type' in data:
            update_data['ward_type'] = data['ward_type']
        if 'daycare_type' in data:
            update_data['daycare_type'] = data['daycare_type']
        if 'expected_length_stay' in data:
            update_data['expected_length_stay'] = data['expected_length_stay']
        if 'estimated_treatment_cost' in data:
            update_data['estimated_treatment_cost'] = data['estimated_treatment_cost']
        
        # Payer Information
        if 'payer_type' in data:
            update_data['payer_type'] = data['payer_type']
        if 'payer_name' in data:
            update_data['payer_name'] = data['payer_name']
        if 'insurer_name' in data:
            update_data['insurer_name'] = data['insurer_name']
        
        # Update the claim
        claim_ref.update(update_data)
        
        # Log the update
        log_claim_update(claim_id, hospital_id, user_id, user_name, update_data)
        
        return jsonify({
            'message': 'Claim draft updated successfully',
            'claim_id': claim_id,
            'updated_fields': list(update_data.keys())
        }), 200
        
    except Exception as e:
        logging.error(f"Error updating claim draft: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to update claim draft'
        }), 500


@claims_bp.route('/doctor-details/<doctor_id>', methods=['GET'])
# @require_auth
# @require_permission('claims:read')
def get_doctor_details(doctor_id):
    """Get doctor details by ID for auto-population"""
    try:
        hospital_id = request.headers.get('X-Hospital-ID')
        
        if not hospital_id:
            return jsonify({'error': 'Hospital ID is required'}), 400
        
        db = get_db()
        doctor_ref = db.collection('doctors').document(doctor_id)
        doctor_doc = doctor_ref.get()
        
        if not doctor_doc.exists:
            return jsonify({'error': 'Doctor not found'}), 404
        
        doctor_data = doctor_doc.to_dict()
        
        # Verify doctor belongs to the hospital
        if doctor_data.get('hospital_id') != hospital_id:
            return jsonify({'error': 'Doctor not found in this hospital'}), 404
        
        # Get speciality details
        speciality_id = doctor_data.get('speciality_id')
        speciality_name = 'Unknown'
        if speciality_id:
            speciality_ref = db.collection('specialities').document(speciality_id)
            speciality_doc = speciality_ref.get()
            if speciality_doc.exists:
                speciality_data = speciality_doc.to_dict()
                speciality_name = speciality_data.get('name', 'Unknown')
        
        return jsonify({
            'doctor': {
                'id': doctor_data.get('id'),
                'name': doctor_data.get('name'),
                'contact': doctor_data.get('contact'),
                'qualification': doctor_data.get('qualification'),
                'registration_number': doctor_data.get('registration_number'),
                'speciality_id': speciality_id,
                'speciality_name': speciality_name
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching doctor details: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@claims_bp.route('/<claim_id>', methods=['GET'])
# @require_auth
# @require_permission('claims:read')
def get_claim(claim_id):
    """Get claim by ID"""
    try:
        # Get claim from database
        db = get_db()
        claim_ref = db.collection('claims').document(claim_id)
        claim_doc = claim_ref.get()
        
        if not claim_doc.exists:
            return jsonify({'error': 'Claim not found'}), 404
        
        claim_data = claim_doc.to_dict()
        
        return jsonify({
            'claim': claim_data
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting claim: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@claims_bp.route('/', methods=['GET'])
# @require_auth
# @require_permission('claims:read')
def get_claims():
    """Get all claims with pagination and filtering"""
    try:
        hospital_id = request.headers.get('X-Hospital-ID', 'HOSP_001')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status', '')
        claim_type = request.args.get('claim_type', '')
        search = request.args.get('search', '')
        
        # Build query
        db = get_db()
        claims_ref = db.collection('claims')
        query = claims_ref.where('hospital_id', '==', hospital_id).where('is_active', '==', True)
        
        if status:
            query = query.where('status', '==', status)
        if claim_type:
            query = query.where('claim_type', '==', claim_type)
        
        # Get total count
        total_docs = list(query.stream())
        total_count = len(total_docs)
        
        # Apply pagination
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        
        # Get paginated results
        paginated_docs = total_docs[start_index:end_index]
        
        claims = []
        for doc in paginated_docs:
            claim_data = doc.to_dict()
            if not search or search.lower() in claim_data.get('patient_name', '').lower() or \
               search.lower() in claim_data.get('uhid', '').lower() or \
               search.lower() in claim_data.get('claim_id', '').lower():
                claims.append(claim_data)
        
        return jsonify({
            'claims': claims,
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
        error_msg = str(e)
        logging.error(f"Error getting claims: {error_msg}")
        logging.error(f"Error type: {type(e).__name__}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        
        # Return detailed error in development, generic in production
        import os
        if os.environ.get('FLASK_ENV') == 'development':
            return jsonify({
                'error': 'Internal server error',
                'details': error_msg,
                'type': type(e).__name__
            }), 500
        else:
            return jsonify({'error': 'Internal server error'}), 500


@claims_bp.route('/submit/<claim_id>', methods=['POST'])
# @require_auth
# @require_permission('claims:submit')
def submit_claim(claim_id):
    """Submit claim for processing"""
    try:
        hospital_id = request.headers.get('X-Hospital-ID', 'HOSP_001')
        user_id = request.headers.get('X-User-ID', 'test_user')
        user_name = request.headers.get('X-User-Name', 'Test User')
        
        # Get existing claim
        db = get_db()
        claim_ref = db.collection('claims').document(claim_id)
        claim_doc = claim_ref.get()
        
        if not claim_doc.exists:
            return jsonify({'error': 'Claim not found'}), 404
        
        claim_data = claim_doc.to_dict()
        
        if claim_data.get('status') != 'draft':
            return jsonify({'error': 'Only draft claims can be submitted'}), 400
        
        # Validate required fields for submission
        validation_errors = validate_claim_for_submission(claim_data)
        if validation_errors:
            return jsonify({
                'error': 'Validation failed',
                'details': validation_errors
            }), 400
        
        # Update claim status
        update_data = {
            'status': 'submitted',
            'submitted_at': datetime.utcnow(),
            'submitted_by': user_id,
            'submitted_by_name': user_name,
            'updated_by': user_id,
            'updated_by_name': user_name,
            'updated_at': datetime.utcnow()
        }
        
        claim_ref.update(update_data)
        
        # Log the submission
        log_claim_submission(claim_id, hospital_id, user_id, user_name)
        
        return jsonify({
            'message': 'Claim submitted successfully',
            'claim_id': claim_id,
            'status': 'submitted',
            'submitted_at': update_data['submitted_at'].isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"Error submitting claim: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to submit claim'
        }), 500


@claims_bp.route('/debug', methods=['GET'])
def debug_firebase():
    """Debug endpoint to test Firebase connectivity and configuration"""
    try:
        import os
        debug_info = {
            'environment': os.environ.get('FLASK_ENV', 'unknown'),
            'firebase_project_id': os.environ.get('FIREBASE_PROJECT_ID', 'not_set'),
            'firebase_storage_bucket': os.environ.get('FIREBASE_STORAGE_BUCKET', 'not_set'),
            'has_service_account_key': bool(os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY')),
            'service_account_key_length': len(os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY', '')) if os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY') else 0
        }
        
        # Test Firebase connection
        try:
            db = get_db()
            debug_info['firebase_connection'] = 'success'
            
            # Test a simple query
            test_collection = db.collection('test_connection')
            test_doc = test_collection.document('debug_test')
            test_doc.set({'timestamp': datetime.utcnow(), 'test': True})
            test_doc.delete()
            debug_info['firestore_write_test'] = 'success'
            
        except Exception as firebase_error:
            debug_info['firebase_connection'] = 'failed'
            debug_info['firebase_error'] = str(firebase_error)
            debug_info['firebase_error_type'] = type(firebase_error).__name__
        
        # Test claims collection access
        try:
            db = get_db()
            claims_ref = db.collection('claims')
            # Just try to get a reference, don't actually query
            debug_info['claims_collection_access'] = 'success'
        except Exception as claims_error:
            debug_info['claims_collection_access'] = 'failed'
            debug_info['claims_error'] = str(claims_error)
            debug_info['claims_error_type'] = type(claims_error).__name__
        
        return jsonify({
            'status': 'debug_info',
            'debug': debug_info
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'debug_failed',
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc()
        }), 500


@claims_bp.route('/payers', methods=['GET'])
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


def validate_claim_mandatory_fields(data: Dict[str, Any]) -> List[str]:
    """Validate mandatory claim fields"""
    errors = []
    
    # Validate patient name
    if not data.get('patient_name') or len(data['patient_name'].strip()) < 2:
        errors.append('Patient name is required and must be at least 2 characters')
    
    # Validate mobile number
    if not data.get('mobile_number'):
        errors.append('Mobile number is required')
    elif not validate_indian_phone_number(data['mobile_number']):
        errors.append('Invalid mobile number format')
    
    # Validate UHID
    if not data.get('uhid') or len(data['uhid'].strip()) < 3:
        errors.append('UHID is required and must be at least 3 characters')
    
    # Validate claim type
    valid_claim_types = ['IP', 'OP', 'Day care']
    if not data.get('claim_type') or data['claim_type'] not in valid_claim_types:
        errors.append('Claim type is required and must be one of: ' + ', '.join(valid_claim_types))
    
    # Validate admission type
    valid_admission_types = ['Planned', 'Emergency']
    if not data.get('admission_type') or data['admission_type'] not in valid_admission_types:
        errors.append('Admission type is required and must be one of: ' + ', '.join(valid_admission_types))
    
    return errors


def validate_claim_optional_fields(data: Dict[str, Any]) -> List[str]:
    """Validate optional claim fields"""
    errors = []
    
    # Validate claim type if provided
    if data.get('claim_type'):
        valid_claim_types = ['IP', 'OP', 'Day care']
        if data['claim_type'] not in valid_claim_types:
            errors.append('Invalid claim type. Must be IP, OP, or Day care')
    
    # Validate admission type if provided
    if data.get('admission_type'):
        valid_admission_types = ['Planned', 'Emergency']
        if data['admission_type'] not in valid_admission_types:
            errors.append('Invalid admission type. Must be Planned or Emergency')
    
    # Validate email if provided
    if data.get('email_id') and not validate_email(data['email_id']):
        errors.append('Invalid email format')
    
    # Validate mobile numbers if provided
    if data.get('alternative_contact') and not validate_indian_phone_number(data['alternative_contact']):
        errors.append('Invalid alternative contact number format')
    
    if data.get('treating_doctor_contact') and not validate_indian_phone_number(data['treating_doctor_contact']):
        errors.append('Invalid treating doctor contact number format')
    
    # Validate pincode if provided
    if data.get('pincode') and not validate_pincode(data['pincode']):
        errors.append('Invalid pincode format')
    
    # Validate payer information
    if data.get('payer_type'):
        valid_payer_types = ['TPA', 'Insurer', 'Corporate', 'Social schemes', 'Others']
        if data['payer_type'] not in valid_payer_types:
            errors.append('Invalid payer type')
    
    # Validate ward type if provided
    if data.get('ward_type'):
        valid_ward_types = ['Single room', 'Twin sharing', 'ICU', '3 or more beds']
        if data['ward_type'] not in valid_ward_types:
            errors.append('Invalid ward type. Must be Single room, Twin sharing, ICU, or 3 or more beds')
    
    # Validate daycare procedure if provided
    if data.get('daycare_procedure'):
        valid_daycare_types = ['Dialysis', 'Chemotherapy', 'Radiotherapy', 'Other procedures']
        if data['daycare_procedure'] not in valid_daycare_types:
            errors.append('Invalid daycare procedure. Must be Dialysis, Chemotherapy, Radiotherapy, or Other procedures')
    
    # Validate nature of illness if provided
    if data.get('nature_of_illness'):
        valid_nature_types = ['Disease', 'Injury']
        if data['nature_of_illness'] not in valid_nature_types:
            errors.append('Invalid nature of illness. Must be Disease or Injury')
    
    # Validate cause of injury if provided
    if data.get('cause_of_injury'):
        valid_cause_types = ['Substance Abuse', 'Accident', 'Negligence']
        if data['cause_of_injury'] not in valid_cause_types:
            errors.append('Invalid cause of injury. Must be Substance Abuse, Accident, or Negligence')
    
    # Validate proposed line of treatment if provided
    if data.get('proposed_line_of_treatment'):
        valid_treatment_types = ['Medical Management', 'Surgical management', 'Intensive care', 'Investigation', 'Non-allopathic']
        if data['proposed_line_of_treatment'] not in valid_treatment_types:
            errors.append('Invalid proposed line of treatment. Must be Medical Management, Surgical management, Intensive care, Investigation, or Non-allopathic')
    
    # Validate route of drug administration if provided
    if data.get('route_of_drug_admin'):
        valid_route_types = ['IV', 'Oral', 'Others']
        if data['route_of_drug_admin'] not in valid_route_types:
            errors.append('Invalid route of drug administration. Must be IV, Oral, or Others')
    
    # Validate occupation if provided
    if data.get('occupation'):
        valid_occupations = ['Service', 'Self employed', 'Retired', 'Business owner']
        if data['occupation'] not in valid_occupations:
            errors.append('Invalid occupation. Must be Service, Self employed, Retired, or Business owner')
    
    # Validate RTA file and FIR number (conditional validation)
    if data.get('rta_file') is True and not data.get('fir_number'):
        errors.append('FIR number is required when RTA file is true')
    
    # Validate maternity details
    if data.get('maternity_details', {}).get('maternity') and 'gpla' not in data['maternity_details']:
        errors.append('G/P/L/A details required for maternity cases')
    
    # Validate family physician details (conditional validation)
    if data.get('family_physician') is True:
        if not data.get('family_physician_details', {}).get('doctor_name'):
            errors.append('Doctor name is required when family physician is true')
        if not data.get('family_physician_details', {}).get('contact_number'):
            errors.append('Contact number is required when family physician is true')
    
    # Validate additional policy details (conditional validation)
    if data.get('additional_policy') is True:
        if not data.get('additional_policy_details', {}).get('payer_type'):
            errors.append('Payer type is required when additional policy is true')
        if not data.get('additional_policy_details', {}).get('payer_name'):
            errors.append('Payer name is required when additional policy is true')
        if data.get('additional_policy_details', {}).get('payer_type') == 'TPA' and not data.get('additional_policy_details', {}).get('insurer_name'):
            errors.append('Insurer name is required when additional policy payer type is TPA')
    
    return errors


def validate_claim_for_submission(claim_data: Dict[str, Any]) -> List[str]:
    """Validate claim data for submission"""
    errors = []
    
    # Check if all required fields are present
    required_fields = ['gender', 'date_of_birth', 'address', 'city', 'state', 'pincode']
    for field in required_fields:
        if not claim_data.get(field):
            errors.append(f'{field.replace("_", " ").title()} is required for submission')
    
    # Validate payer information
    if not claim_data.get('payer_type'):
        errors.append('Payer type is required for submission')
    
    if not claim_data.get('payer_name'):
        errors.append('Payer name is required for submission')
    
    # Validate treatment information
    if not claim_data.get('treating_doctor_name'):
        errors.append('Treating doctor name is required for submission')
    
    if not claim_data.get('provisional_diagnosis'):
        errors.append('Provisional diagnosis is required for submission')
    
    return errors


def check_patient_exists(uhid: str) -> bool:
    """Check if patient exists in patients collection"""
    try:
        db = get_db()
        patient_ref = db.collection('patients').document(uhid)
        patient_doc = patient_ref.get()
        return patient_doc.exists
    except Exception:
        return False


def get_hospital_info(hospital_id: str) -> dict:
    """Get hospital information by ID"""
    try:
        db = get_db()
        hospital_ref = db.collection('hospitals').document(hospital_id)
        hospital_doc = hospital_ref.get()
        
        if hospital_doc.exists:
            hospital_data = hospital_doc.to_dict()
            # Check for hospital name in different possible fields
            hospital_name = (
                hospital_data.get('Hospital_name') or 
                hospital_data.get('hospital_name') or 
                hospital_data.get('name') or 
                'Unknown Hospital'
            )
            return {
                'id': hospital_id,
                'name': hospital_name,
                **hospital_data
            }
        else:
            return {'id': hospital_id, 'name': 'Unknown Hospital'}
    except Exception as e:
        logging.error(f"Error fetching hospital info: {str(e)}")
        return {'id': hospital_id, 'name': 'Unknown Hospital'}


def log_claim_creation(claim_id: str, hospital_id: str, user_id: str, user_name: str):
    """Log claim creation for audit trail"""
    try:
        audit_log = {
            'id': str(uuid.uuid4()),
            'hospital_id': hospital_id,
            'user_id': user_id,
            'action': 'create_claim',
            'resource_type': 'claim',
            'resource_id': claim_id,
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
        logging.error(f"Error logging claim creation: {str(e)}")


def log_claim_update(claim_id: str, hospital_id: str, user_id: str, user_name: str, update_data: Dict[str, Any]):
    """Log claim update for audit trail"""
    try:
        audit_log = {
            'id': str(uuid.uuid4()),
            'hospital_id': hospital_id,
            'user_id': user_id,
            'action': 'update_claim',
            'resource_type': 'claim',
            'resource_id': claim_id,
            'new_values': update_data,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'timestamp': datetime.utcnow().isoformat(),
            'created_at': datetime.utcnow(),
            'is_active': True
        }
        
        db = get_db()
        db.collection('audit_logs').add(audit_log)
    except Exception as e:
        logging.error(f"Error logging claim update: {str(e)}")


def log_claim_submission(claim_id: str, hospital_id: str, user_id: str, user_name: str):
    """Log claim submission for audit trail"""
    try:
        audit_log = {
            'id': str(uuid.uuid4()),
            'hospital_id': hospital_id,
            'user_id': user_id,
            'action': 'submit_claim',
            'resource_type': 'claim',
            'resource_id': claim_id,
            'new_values': {'submitted_by': user_name},
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'timestamp': datetime.utcnow().isoformat(),
            'created_at': datetime.utcnow(),
            'is_active': True
        }
        
        db = get_db()
        db.collection('audit_logs').add(audit_log)
    except Exception as e:
        logging.error(f"Error logging claim submission: {str(e)}")
