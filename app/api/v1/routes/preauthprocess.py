"""
Preauth Process routes for RCM SaaS Application
Handles preauth status transitions and workflow management
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
import logging
from typing import Dict, Any, List, Optional

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.api.v1.middleware.auth_middleware import require_auth, require_permission
from app.api.v1.middleware.validation_middleware import validate_json
from app.database.firebase_client import FirebaseClient
from app.database.models.preauth_request import PreauthRequest
from app.database.models.preauth_state import PreauthState

preauthprocess_bp = Blueprint('preauthprocess', __name__)

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

# Define valid status transitions based on roles
STATUS_TRANSITIONS = {
    'preauth_executive': {
        'Preauth Registered': ['Need More Info', 'Preauth Approved', 'Preauth Denial'],
        'Need More Info': ['Info Submitted'],
        'Discharge Submitted': ['Discharge NMI', 'Discharge Approved', 'Discharge Denial'],
        'Discharge NMI': ['Discharge NMI Submitted']
    },
    'processor': {
        'Preauth Registered': ['Need More Info', 'Preauth Approved', 'Preauth Denial'],
        'Discharge Submitted': ['Discharge NMI', 'Discharge Approved', 'Discharge Denial']
    }
}

# Valid roles
VALID_ROLES = ['preauth_executive', 'processor']

def validate_status_transition(current_status: str, new_status: str, user_role: str) -> bool:
    """Validate if status transition is allowed for the given role"""
    if user_role not in VALID_ROLES:
        return False
    
    role_transitions = STATUS_TRANSITIONS.get(user_role, {})
    allowed_transitions = role_transitions.get(current_status, [])
    
    return new_status in allowed_transitions

def create_preauth_state_record(preauth_id: str, hospital_id: str, previous_status: str, 
                              new_status: str, user_id: str, remarks: str = '', 
                              state_data: Dict[str, Any] = None) -> PreauthState:
    """Create a new preauth state record"""
    state_record = PreauthState(
        preauth_id=preauth_id,
        hospital_id=hospital_id,
        state=new_status,
        previous_state=previous_status,
        state_data=state_data or {},
        remarks=remarks,
        changed_by=user_id,
        changed_at=datetime.utcnow(),
        is_automatic=False,
        trigger_event='manual_status_change'
    )
    return state_record

@preauthprocess_bp.route('/submit', methods=['POST'])
# @require_auth
# @require_permission('preauth:submit')
@validate_json(['patient_id', 'preauth_id', 'insurance_provider', 'policy_number', 'treatment_type', 'diagnosis_code', 'estimated_cost'])
def submit_preauth():
    """Submit a new preauth request - starts with 'Preauth Registered' status"""
    try:
        hospital_id = request.headers.get('X-Hospital-ID', 'HOSP_001')
        user_id = request.headers.get('X-User-ID', 'test_user')
        user_name = request.headers.get('X-User-Name', 'Test User')
        data = request.get_json()
        
        # Create preauth request with initial status
        preauth_data = {
            'hospital_id': hospital_id,
            'patient_id': data['patient_id'],
            'preauth_id': data['preauth_id'],
            'insurance_provider': data['insurance_provider'],
            'policy_number': data['policy_number'],
            'treatment_type': data['treatment_type'],
            'diagnosis_code': data['diagnosis_code'],
            'estimated_cost': float(data['estimated_cost']),
            'requested_amount': float(data.get('requested_amount', data['estimated_cost'])),
            'status': 'Preauth Registered',  # Initial status
            'submission_date': datetime.utcnow(),
            'created_by': user_id,
            'updated_by': user_id
        }
        
        # Add optional fields if provided
        optional_fields = [
            'policy_holder_name', 'policy_holder_relation', 'procedure_codes',
            'treatment_date', 'admission_date', 'doctor_name', 'doctor_license',
            'hospital_name', 'room_type', 'room_rent', 'consultation_fee',
            'investigation_cost', 'medicine_cost', 'surgery_cost', 'other_costs',
            'remarks', 'priority', 'is_urgent', 'urgent_reason'
        ]
        
        for field in optional_fields:
            if field in data:
                preauth_data[field] = data[field]
        
        preauth_request = PreauthRequest(**preauth_data)
        
        # Validate the request
        validation_errors = preauth_request.validate()
        if validation_errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': validation_errors
            }), 400
        
        # Save to database
        db = get_db()
        preauth_dict = preauth_request.to_dict()
        preauth_dict['id'] = str(uuid.uuid4())
        
        # Save preauth request
        db.collection('preauth_requests').document(preauth_dict['id']).set(preauth_dict)
        
        # Create initial state record
        state_record = create_preauth_state_record(
            preauth_id=preauth_request.preauth_id,
            hospital_id=hospital_id,
            previous_status='',
            new_status='Preauth Registered',
            user_id=user_id,
            remarks='Preauth request submitted',
            state_data={'submission_data': preauth_data}
        )
        
        state_dict = state_record.to_dict()
        state_dict['id'] = str(uuid.uuid4())
        db.collection('preauth_states').document(state_dict['id']).set(state_dict)
        
        return jsonify({
            'success': True,
            'message': 'Preauth request submitted successfully',
            'data': {
                'preauth_id': preauth_request.preauth_id,
                'status': 'Preauth Registered',
                'submission_date': preauth_request.submission_date.isoformat()
            }
        }), 201
        
    except Exception as e:
        logging.error(f"Error submitting preauth: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to submit preauth request',
            'error': str(e)
        }), 500

@preauthprocess_bp.route('/update-status', methods=['PUT'])
# @require_auth
# @require_permission('preauth:update_status')
@validate_json(['preauth_id', 'new_status'])
def update_preauth_status():
    """Update preauth status based on user role and current status"""
    try:
        hospital_id = request.headers.get('X-Hospital-ID', 'HOSP_001')
        user_id = request.headers.get('X-User-ID', 'test_user')
        user_role = request.headers.get('X-User-Role', 'preauth_executive')  # Default role
        data = request.get_json()
        
        preauth_id = data['preauth_id']
        new_status = data['new_status']
        remarks = data.get('remarks', '')
        state_data = data.get('state_data', {})
        
        # Validate user role
        if user_role not in VALID_ROLES:
            return jsonify({
                'success': False,
                'message': 'Invalid user role',
                'valid_roles': VALID_ROLES
            }), 400
        
        # Get current preauth request
        db = get_db()
        preauth_query = db.collection('preauth_requests').where('preauth_id', '==', preauth_id).where('hospital_id', '==', hospital_id).limit(1)
        preauth_docs = preauth_query.get()
        
        if not preauth_docs:
            return jsonify({
                'success': False,
                'message': 'Preauth request not found'
            }), 404
        
        preauth_doc = preauth_docs[0]
        preauth_data = preauth_doc.to_dict()
        current_status = preauth_data.get('status', '')
        
        # Validate status transition
        if not validate_status_transition(current_status, new_status, user_role):
            allowed_transitions = STATUS_TRANSITIONS.get(user_role, {}).get(current_status, [])
            return jsonify({
                'success': False,
                'message': f'Invalid status transition from {current_status} to {new_status}',
                'current_status': current_status,
                'user_role': user_role,
                'allowed_transitions': allowed_transitions
            }), 400
        
        # Update preauth request status
        preauth_data['status'] = new_status
        preauth_data['updated_at'] = datetime.utcnow()
        preauth_data['updated_by'] = user_id
        
        # Add status-specific fields
        if new_status == 'Preauth Approved':
            preauth_data['approval_date'] = datetime.utcnow()
            preauth_data['approval_reference'] = state_data.get('approval_reference', '')
            preauth_data['approved_amount'] = float(state_data.get('approved_amount', preauth_data.get('requested_amount', 0)))
        elif new_status in ['Preauth Denial', 'Discharge Denial']:
            preauth_data['rejection_date'] = datetime.utcnow()
            preauth_data['rejection_reason'] = remarks
        
        # Save updated preauth request
        db.collection('preauth_requests').document(preauth_doc.id).set(preauth_data)
        
        # Create state transition record
        state_record = create_preauth_state_record(
            preauth_id=preauth_id,
            hospital_id=hospital_id,
            previous_status=current_status,
            new_status=new_status,
            user_id=user_id,
            remarks=remarks,
            state_data=state_data
        )
        
        state_dict = state_record.to_dict()
        state_dict['id'] = str(uuid.uuid4())
        db.collection('preauth_states').document(state_dict['id']).set(state_dict)
        
        return jsonify({
            'success': True,
            'message': f'Status updated from {current_status} to {new_status}',
            'data': {
                'preauth_id': preauth_id,
                'previous_status': current_status,
                'new_status': new_status,
                'updated_by': user_id,
                'updated_at': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error updating preauth status: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update preauth status',
            'error': str(e)
        }), 500

@preauthprocess_bp.route('/status-history/<preauth_id>', methods=['GET'])
# @require_auth
# @require_permission('preauth:view_history')
def get_status_history(preauth_id):
    """Get status history for a preauth request"""
    try:
        hospital_id = request.headers.get('X-Hospital-ID', 'HOSP_001')
        
        db = get_db()
        
        # Get status history
        states_query = db.collection('preauth_states').where('preauth_id', '==', preauth_id).where('hospital_id', '==', hospital_id).order_by('changed_at')
        states_docs = states_query.get()
        
        status_history = []
        for doc in states_docs:
            state_data = doc.to_dict()
            status_history.append({
                'state': state_data.get('state'),
                'previous_state': state_data.get('previous_state'),
                'changed_at': state_data.get('changed_at').isoformat() if state_data.get('changed_at') else None,
                'changed_by': state_data.get('changed_by'),
                'remarks': state_data.get('remarks'),
                'duration_minutes': state_data.get('duration_minutes', 0)
            })
        
        return jsonify({
            'success': True,
            'data': {
                'preauth_id': preauth_id,
                'status_history': status_history
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting status history: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get status history',
            'error': str(e)
        }), 500

@preauthprocess_bp.route('/current-status/<preauth_id>', methods=['GET'])
# @require_auth
# @require_permission('preauth:view_status')
def get_current_status(preauth_id):
    """Get current status and allowed transitions for a preauth request"""
    try:
        hospital_id = request.headers.get('X-Hospital-ID', 'HOSP_001')
        user_role = request.headers.get('X-User-Role', 'preauth_executive')
        
        db = get_db()
        
        # Get current preauth request
        preauth_query = db.collection('preauth_requests').where('preauth_id', '==', preauth_id).where('hospital_id', '==', hospital_id).limit(1)
        preauth_docs = preauth_query.get()
        
        if not preauth_docs:
            return jsonify({
                'success': False,
                'message': 'Preauth request not found'
            }), 404
        
        preauth_data = preauth_docs[0].to_dict()
        current_status = preauth_data.get('status', '')
        
        # Get allowed transitions for current user role
        allowed_transitions = STATUS_TRANSITIONS.get(user_role, {}).get(current_status, [])
        
        return jsonify({
            'success': True,
            'data': {
                'preauth_id': preauth_id,
                'current_status': current_status,
                'user_role': user_role,
                'allowed_transitions': allowed_transitions,
                'preauth_data': {
                    'patient_id': preauth_data.get('patient_id'),
                    'insurance_provider': preauth_data.get('insurance_provider'),
                    'policy_number': preauth_data.get('policy_number'),
                    'treatment_type': preauth_data.get('treatment_type'),
                    'estimated_cost': preauth_data.get('estimated_cost'),
                    'requested_amount': preauth_data.get('requested_amount'),
                    'submission_date': preauth_data.get('submission_date').isoformat() if preauth_data.get('submission_date') else None
                }
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting current status: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get current status',
            'error': str(e)
        }), 500

@preauthprocess_bp.route('/list', methods=['GET'])
# @require_auth
# @require_permission('preauth:list')
def list_preauth_requests():
    """List preauth requests with filtering options"""
    try:
        hospital_id = request.headers.get('X-Hospital-ID', 'HOSP_001')
        user_role = request.headers.get('X-User-Role', 'preauth_executive')
        
        # Get query parameters
        status_filter = request.args.get('status')
        patient_id = request.args.get('patient_id')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        db = get_db()
        
        # Build query
        query = db.collection('preauth_requests').where('hospital_id', '==', hospital_id)
        
        if status_filter:
            query = query.where('status', '==', status_filter)
        
        if patient_id:
            query = query.where('patient_id', '==', patient_id)
        
        # Execute query with pagination
        query = query.order_by('submission_date', direction='DESCENDING').limit(limit).offset(offset)
        docs = query.get()
        
        preauth_requests = []
        for doc in docs:
            data = doc.to_dict()
            current_status = data.get('status', '')
            allowed_transitions = STATUS_TRANSITIONS.get(user_role, {}).get(current_status, [])
            
            preauth_requests.append({
                'id': doc.id,
                'preauth_id': data.get('preauth_id'),
                'patient_id': data.get('patient_id'),
                'status': current_status,
                'insurance_provider': data.get('insurance_provider'),
                'treatment_type': data.get('treatment_type'),
                'estimated_cost': data.get('estimated_cost'),
                'requested_amount': data.get('requested_amount'),
                'submission_date': data.get('submission_date').isoformat() if data.get('submission_date') else None,
                'allowed_transitions': allowed_transitions
            })
        
        return jsonify({
            'success': True,
            'data': {
                'preauth_requests': preauth_requests,
                'total_count': len(preauth_requests),
                'limit': limit,
                'offset': offset
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error listing preauth requests: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to list preauth requests',
            'error': str(e)
        }), 500

@preauthprocess_bp.route('/submit-discharge', methods=['POST'])
# @require_auth
# @require_permission('preauth:submit_discharge')
@validate_json(['preauth_id', 'discharge_data'])
def submit_discharge():
    """Submit discharge information for a preauth request"""
    try:
        hospital_id = request.headers.get('X-Hospital-ID', 'HOSP_001')
        user_id = request.headers.get('X-User-ID', 'test_user')
        data = request.get_json()
        
        preauth_id = data['preauth_id']
        discharge_data = data['discharge_data']
        
        db = get_db()
        
        # Get current preauth request
        preauth_query = db.collection('preauth_requests').where('preauth_id', '==', preauth_id).where('hospital_id', '==', hospital_id).limit(1)
        preauth_docs = preauth_query.get()
        
        if not preauth_docs:
            return jsonify({
                'success': False,
                'message': 'Preauth request not found'
            }), 404
        
        preauth_doc = preauth_docs[0]
        preauth_data = preauth_doc.to_dict()
        current_status = preauth_data.get('status', '')
        
        # Check if discharge can be submitted
        if current_status not in ['Preauth Approved']:
            return jsonify({
                'success': False,
                'message': f'Cannot submit discharge for status: {current_status}. Preauth must be approved first.'
            }), 400
        
        # Update preauth with discharge data
        preauth_data['status'] = 'Discharge Submitted'
        preauth_data['discharge_date'] = discharge_data.get('discharge_date', datetime.utcnow())
        preauth_data['actual_cost'] = discharge_data.get('actual_cost', 0.0)
        preauth_data['discharge_summary'] = discharge_data.get('discharge_summary', '')
        preauth_data['final_diagnosis'] = discharge_data.get('final_diagnosis', '')
        preauth_data['updated_at'] = datetime.utcnow()
        preauth_data['updated_by'] = user_id
        
        # Save updated preauth request
        db.collection('preauth_requests').document(preauth_doc.id).set(preauth_data)
        
        # Create state transition record
        state_record = create_preauth_state_record(
            preauth_id=preauth_id,
            hospital_id=hospital_id,
            previous_status=current_status,
            new_status='Discharge Submitted',
            user_id=user_id,
            remarks='Discharge information submitted',
            state_data={'discharge_data': discharge_data}
        )
        
        state_dict = state_record.to_dict()
        state_dict['id'] = str(uuid.uuid4())
        db.collection('preauth_states').document(state_dict['id']).set(state_dict)
        
        return jsonify({
            'success': True,
            'message': 'Discharge information submitted successfully',
            'data': {
                'preauth_id': preauth_id,
                'status': 'Discharge Submitted',
                'discharge_date': preauth_data['discharge_date'].isoformat() if isinstance(preauth_data['discharge_date'], datetime) else preauth_data['discharge_date']
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error submitting discharge: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to submit discharge information',
            'error': str(e)
        }), 500
