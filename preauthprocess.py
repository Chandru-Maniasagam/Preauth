"""
Preauth Process Management System
Handles role-based preauth workflow with status transitions
"""

from flask import Blueprint, request, jsonify, render_template_string, flash, redirect, url_for
from app.database.firebase_client import FirebaseClient
from datetime import datetime
import logging

# Initialize Firebase client
firebase_client = FirebaseClient()

def get_db():
    """Get Firestore database client"""
    return firebase_client.get_firestore_client()

# Create blueprint
preauth_process_bp = Blueprint('preauth_process', __name__)

# Define valid statuses
VALID_STATUSES = [
    'Preauth Registered',
    'preauth_registered',  # Add lowercase version
    'Approved', 
    'Need More Info',
    'Info Submitted',
    'Preauth Denial',
    'Enhance',
    'Enhanced',
    'Enhancement Denial',
    'Discharge Submit',
    'Discharge NMI',
    'Discharge NMI Submitted',
    'Discharge Denial',
    'Discharge Approval'  # Add missing status
]

# Define role-based status transitions
STATUS_TRANSITIONS = {
    'Preauth Executive': {
        'Preauth Registered': ['Enhance', 'Discharge Submit'],
        'preauth_registered': ['Enhance', 'Discharge Submit'],  # Add lowercase version
        'Need More Info': ['Info Submitted'],
        'Enhance': ['Discharge Submit'],
        'Info Submitted': ['Enhance', 'Discharge Submit'],
        'Approved': ['Discharge Submit'],  # Add Approved status transitions
        'Enhanced': ['Discharge Submit']   # Add Enhanced status transitions
    },
    'Preauth Processor': {
        'Preauth Registered': ['Approved', 'Need More Info', 'Preauth Denial'],
        'preauth_registered': ['Approved', 'Need More Info', 'Preauth Denial'],  # Add lowercase version
        'Enhance': ['Enhanced', 'Enhancement Denial'],
        'Discharge Submit': ['Discharge NMI', 'Discharge Approval', 'Discharge Denial'],
        'Discharge NMI': ['Discharge NMI Submitted'],
        'Approved': [],  # Approved is a final status for processor
        'Enhanced': []   # Enhanced is a final status for processor
    }
}

def validate_status_transition(current_status: str, new_status: str, user_role: str) -> bool:
    """Validate if status transition is allowed for the given role"""
    if current_status not in VALID_STATUSES or new_status not in VALID_STATUSES:
        return False
    
    if user_role not in STATUS_TRANSITIONS:
        return False
    
    allowed_transitions = STATUS_TRANSITIONS[user_role].get(current_status, [])
    return new_status in allowed_transitions

def get_claim_by_id(claim_id: str):
    """Get claim by ID from database"""
    try:
        db = get_db()
        claim_ref = db.collection('claims').document(claim_id)
        claim_doc = claim_ref.get()
        
        if not claim_doc.exists:
            return None, "Claim not found"
        
        return claim_doc.to_dict(), None
    except Exception as e:
        logging.error(f"Error fetching claim {claim_id}: {str(e)}")
        return None, str(e)

def update_claim_status(claim_id: str, new_status: str, user_role: str, comments: str = ""):
    """Update claim status with validation"""
    try:
        db = get_db()
        claim_ref = db.collection('claims').document(claim_id)
        claim_doc = claim_ref.get()
        
        if not claim_doc.exists:
            return False, "Claim not found"
        
        claim_data = claim_doc.to_dict()
        current_status = claim_data.get('status', '')
        
        # Validate status transition
        if not validate_status_transition(current_status, new_status, user_role):
            return False, f"Invalid status transition from {current_status} to {new_status} for role {user_role}"
        
        # Update claim status
        update_data = {
            'status': new_status,
            'last_updated': datetime.now().isoformat(),
            'updated_by': user_role,
            'status_history': claim_data.get('status_history', []) + [{
                'from_status': current_status,
                'to_status': new_status,
                'updated_by': user_role,
                'updated_at': datetime.now().isoformat(),
                'comments': comments
            }]
        }
        
        claim_ref.update(update_data)
        
        # Log the status change
        log_status_change(claim_id, current_status, new_status, user_role, comments)
        
        return True, "Status updated successfully"
        
    except Exception as e:
        logging.error(f"Error updating claim status: {str(e)}")
        return False, str(e)

def log_status_change(claim_id: str, from_status: str, to_status: str, user_role: str, comments: str):
    """Log status change in audit logs"""
    try:
        db = get_db()
        audit_log = {
            'claim_id': claim_id,
            'action': 'status_change',
            'from_status': from_status,
            'to_status': to_status,
            'user_role': user_role,
            'comments': comments,
            'timestamp': datetime.now().isoformat()
        }
        db.collection('audit_logs').add(audit_log)
    except Exception as e:
        logging.error(f"Error logging status change: {str(e)}")

# Preauth Executive Routes
@preauth_process_bp.route('/executive/dashboard')
def executive_dashboard():
    """Preauth Executive Dashboard"""
    try:
        db = get_db()
        
        # Get claims for executive role
        claims_ref = db.collection('claims')
        executive_claims = []
        
        # Get claims that executive can work on
        executive_statuses = ['Preauth Registered', 'Need More Info', 'Enhance', 'Info Submitted']
        
        for status in executive_statuses:
            query = claims_ref.where('status', '==', status).where('is_active', '==', True)
            claims = list(query.stream())
            for claim in claims:
                claim_data = claim.to_dict()
                claim_data['id'] = claim.id
                executive_claims.append(claim_data)
        
        return render_template_string(EXECUTIVE_DASHBOARD_TEMPLATE, claims=executive_claims)
        
    except Exception as e:
        logging.error(f"Error loading executive dashboard: {str(e)}")
        return f"Error: {str(e)}", 500

@preauth_process_bp.route('/executive/claim/<claim_id>')
def executive_claim_view(claim_id: str):
    """Preauth Executive - View specific claim"""
    try:
        claim_data, error = get_claim_by_id(claim_id)
        if error:
            return f"Error: {error}", 404
        
        return render_template_string(EXECUTIVE_CLAIM_TEMPLATE, claim=claim_data)
        
    except Exception as e:
        logging.error(f"Error loading claim view: {str(e)}")
        return f"Error: {str(e)}", 500

@preauth_process_bp.route('/executive/update-status', methods=['POST'])
def executive_update_status():
    """Preauth Executive - Update claim status"""
    try:
        data = request.get_json()
        claim_id = data.get('claim_id')
        new_status = data.get('status')
        comments = data.get('comments', '')
        
        if not claim_id or not new_status:
            return jsonify({'error': 'Claim ID and status are required'}), 400
        
        success, message = update_claim_status(claim_id, new_status, 'Preauth Executive', comments)
        
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logging.error(f"Error updating status: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Preauth Processor Routes
@preauth_process_bp.route('/processor/dashboard')
def processor_dashboard():
    """Preauth Processor Dashboard"""
    try:
        db = get_db()
        
        # Get claims for processor role
        claims_ref = db.collection('claims')
        processor_claims = []
        
        # Get claims that processor can work on
        processor_statuses = ['Preauth Registered', 'Enhance', 'Discharge Submit', 'Discharge NMI']
        
        for status in processor_statuses:
            query = claims_ref.where('status', '==', status).where('is_active', '==', True)
            claims = list(query.stream())
            for claim in claims:
                claim_data = claim.to_dict()
                claim_data['id'] = claim.id
                processor_claims.append(claim_data)
        
        return render_template_string(PROCESSOR_DASHBOARD_TEMPLATE, claims=processor_claims)
        
    except Exception as e:
        logging.error(f"Error loading processor dashboard: {str(e)}")
        return f"Error: {str(e)}", 500

@preauth_process_bp.route('/processor/claim/<claim_id>')
def processor_claim_view(claim_id: str):
    """Preauth Processor - View specific claim"""
    try:
        claim_data, error = get_claim_by_id(claim_id)
        if error:
            return f"Error: {error}", 404
        
        return render_template_string(PROCESSOR_CLAIM_TEMPLATE, claim=claim_data)
        
    except Exception as e:
        logging.error(f"Error loading claim view: {str(e)}")
        return f"Error: {str(e)}", 500

@preauth_process_bp.route('/processor/update-status', methods=['POST'])
def processor_update_status():
    """Preauth Processor - Update claim status"""
    try:
        data = request.get_json()
        claim_id = data.get('claim_id')
        new_status = data.get('status')
        comments = data.get('comments', '')
        
        if not claim_id or not new_status:
            return jsonify({'error': 'Claim ID and status are required'}), 400
        
        success, message = update_claim_status(claim_id, new_status, 'Preauth Processor', comments)
        
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logging.error(f"Error updating status: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API Routes for Status Management
@preauth_process_bp.route('/api/status-transitions/<user_role>')
def get_status_transitions(user_role: str):
    """Get allowed status transitions for a role"""
    if user_role not in STATUS_TRANSITIONS:
        return jsonify({'error': 'Invalid role'}), 400
    
    return jsonify({
        'role': user_role,
        'transitions': STATUS_TRANSITIONS[user_role]
    }), 200

@preauth_process_bp.route('/api/claim-status/<claim_id>')
def get_claim_status(claim_id: str):
    """Get current claim status and allowed transitions"""
    try:
        claim_data, error = get_claim_by_id(claim_id)
        if error:
            return jsonify({'error': error}), 404
        
        current_status = claim_data.get('status', '')
        
        # Get allowed transitions for both roles
        executive_transitions = STATUS_TRANSITIONS['Preauth Executive'].get(current_status, [])
        processor_transitions = STATUS_TRANSITIONS['Preauth Processor'].get(current_status, [])
        
        return jsonify({
            'claim_id': claim_id,
            'current_status': current_status,
            'allowed_transitions': {
                'Preauth Executive': executive_transitions,
                'Preauth Processor': processor_transitions
            },
            'status_history': claim_data.get('status_history', [])
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting claim status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@preauth_process_bp.route('/api/update-status', methods=['POST'])
def api_update_status():
    """API endpoint to update claim status"""
    try:
        data = request.get_json()
        claim_id = data.get('claim_id')
        new_status = data.get('status')
        user_role = data.get('user_role')
        comments = data.get('comments', '')
        
        if not all([claim_id, new_status, user_role]):
            return jsonify({'error': 'Claim ID, status, and user role are required'}), 400
        
        success, message = update_claim_status(claim_id, new_status, user_role, comments)
        
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logging.error(f"Error updating status: {str(e)}")
        return jsonify({'error': str(e)}), 500

# HTML Templates
EXECUTIVE_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preauth Executive Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-8">Preauth Executive Dashboard</h1>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {% for claim in claims %}
            <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-lg font-semibold text-gray-800">{{ claim.patient_name }}</h3>
                <p class="text-sm text-gray-600">Claim ID: {{ claim.claim_id }}</p>
                <p class="text-sm text-gray-600">Status: <span class="font-medium text-blue-600">{{ claim.status }}</span></p>
                <p class="text-sm text-gray-600">Hospital: {{ claim.hospital_name }}</p>
                <p class="text-sm text-gray-600">Admission: {{ claim.admission_datetime }}</p>
                
                <div class="mt-4">
                    <a href="/preauth-process/executive/claim/{{ claim.claim_id }}" 
                       class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded text-sm">
                        View Details
                    </a>
                </div>
            </div>
            {% endfor %}
        </div>
        
        {% if not claims %}
        <div class="text-center py-8">
            <p class="text-gray-500">No claims available for processing</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

PROCESSOR_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preauth Processor Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-8">Preauth Processor Dashboard</h1>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {% for claim in claims %}
            <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-lg font-semibold text-gray-800">{{ claim.patient_name }}</h3>
                <p class="text-sm text-gray-600">Claim ID: {{ claim.claim_id }}</p>
                <p class="text-sm text-gray-600">Status: <span class="font-medium text-green-600">{{ claim.status }}</span></p>
                <p class="text-sm text-gray-600">Hospital: {{ claim.hospital_name }}</p>
                <p class="text-sm text-gray-600">Admission: {{ claim.admission_datetime }}</p>
                
                <div class="mt-4">
                    <a href="/preauth-process/processor/claim/{{ claim.claim_id }}" 
                       class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded text-sm">
                        Process Claim
                    </a>
                </div>
            </div>
            {% endfor %}
        </div>
        
        {% if not claims %}
        <div class="text-center py-8">
            <p class="text-gray-500">No claims available for processing</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

EXECUTIVE_CLAIM_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claim Details - Executive View</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-8">Claim Details - Executive View</h1>
        
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Claim Information</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700">Patient Name</label>
                    <p class="text-gray-900">{{ claim.patient_name }}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Claim ID</label>
                    <p class="text-gray-900">{{ claim.claim_id }}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Current Status</label>
                    <p class="text-gray-900 font-medium text-blue-600">{{ claim.status }}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Hospital</label>
                    <p class="text-gray-900">{{ claim.hospital_name }}</p>
                </div>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Update Status</h2>
            <form id="statusForm">
                <input type="hidden" id="claimId" value="{{ claim.claim_id }}">
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">New Status</label>
                    <select id="newStatus" class="form-select block w-full px-3 py-2 border border-gray-300 rounded-md">
                        <option value="">Select Status</option>
                        <option value="Enhance">Enhance</option>
                        <option value="Discharge Submit">Discharge Submit</option>
                        <option value="Info Submitted">Info Submitted</option>
                    </select>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Comments</label>
                    <textarea id="comments" class="form-textarea block w-full px-3 py-2 border border-gray-300 rounded-md" rows="3"></textarea>
                </div>
                <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                    Update Status
                </button>
            </form>
        </div>
    </div>
    
    <script>
        document.getElementById('statusForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const claimId = document.getElementById('claimId').value;
            const newStatus = document.getElementById('newStatus').value;
            const comments = document.getElementById('comments').value;
            
            if (!newStatus) {
                alert('Please select a status');
                return;
            }
            
            try {
                const response = await fetch('/preauth-process/executive/update-status', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        claim_id: claimId,
                        status: newStatus,
                        comments: comments
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Status updated successfully');
                    location.reload();
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Error updating status: ' + error.message);
            }
        });
    </script>
</body>
</html>
"""

PROCESSOR_CLAIM_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claim Details - Processor View</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-8">Claim Details - Processor View</h1>
        
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Claim Information</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700">Patient Name</label>
                    <p class="text-gray-900">{{ claim.patient_name }}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Claim ID</label>
                    <p class="text-gray-900">{{ claim.claim_id }}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Current Status</label>
                    <p class="text-gray-900 font-medium text-green-600">{{ claim.status }}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Hospital</label>
                    <p class="text-gray-900">{{ claim.hospital_name }}</p>
                </div>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Process Claim</h2>
            <form id="statusForm">
                <input type="hidden" id="claimId" value="{{ claim.claim_id }}">
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">New Status</label>
                    <select id="newStatus" class="form-select block w-full px-3 py-2 border border-gray-300 rounded-md">
                        <option value="">Select Status</option>
                        <option value="Approved">Approved</option>
                        <option value="Need More Info">Need More Info</option>
                        <option value="Preauth Denial">Preauth Denial</option>
                        <option value="Enhanced">Enhanced</option>
                        <option value="Enhancement Denial">Enhancement Denial</option>
                        <option value="Discharge NMI">Discharge NMI</option>
                        <option value="Discharge Approval">Discharge Approval</option>
                        <option value="Discharge Denial">Discharge Denial</option>
                        <option value="Discharge NMI Submitted">Discharge NMI Submitted</option>
                    </select>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Comments</label>
                    <textarea id="comments" class="form-textarea block w-full px-3 py-2 border border-gray-300 rounded-md" rows="3"></textarea>
                </div>
                <button type="submit" class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
                    Process Claim
                </button>
            </form>
        </div>
    </div>
    
    <script>
        document.getElementById('statusForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const claimId = document.getElementById('claimId').value;
            const newStatus = document.getElementById('newStatus').value;
            const comments = document.getElementById('comments').value;
            
            if (!newStatus) {
                alert('Please select a status');
                return;
            }
            
            try {
                const response = await fetch('/preauth-process/processor/update-status', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        claim_id: claimId,
                        status: newStatus,
                        comments: comments
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Status updated successfully');
                    location.reload();
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Error updating status: ' + error.message);
            }
        });
    </script>
</body>
</html>
"""
