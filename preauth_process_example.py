"""
Example usage of Preauth Process API endpoints

This file demonstrates how to use the preauth process API endpoints
with the status transitions and role-based access control.
"""

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:5000/api/v1/preauth-process"

# Headers for authentication (currently disabled for development)
HEADERS = {
    'Content-Type': 'application/json',
    'X-Hospital-ID': 'HOSP_001',
    'X-User-ID': 'test_user',
    'X-User-Name': 'Test User',
    'X-User-Role': 'preauth_executive'  # or 'processor'
}

def submit_preauth():
    """Submit a new preauth request"""
    data = {
        'patient_id': 'PAT_001',
        'preauth_id': 'PA_2024_001',
        'insurance_provider': 'Apollo Munich Health Insurance',
        'policy_number': 'POL123456789',
        'treatment_type': 'Cardiac Surgery',
        'diagnosis_code': 'I25.9',
        'estimated_cost': 500000.0,
        'requested_amount': 500000.0,
        'policy_holder_name': 'John Doe',
        'policy_holder_relation': 'self',
        'doctor_name': 'Dr. Smith',
        'hospital_name': 'Apollo Hospital',
        'remarks': 'Urgent cardiac surgery required'
    }
    
    response = requests.post(f"{BASE_URL}/submit", headers=HEADERS, json=data)
    print("Submit Preauth Response:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def update_status(preauth_id, new_status, user_role='preauth_executive'):
    """Update preauth status"""
    headers = HEADERS.copy()
    headers['X-User-Role'] = user_role
    
    data = {
        'preauth_id': preauth_id,
        'new_status': new_status,
        'remarks': f'Status updated to {new_status}',
        'state_data': {
            'approval_reference': 'APP_REF_001' if new_status == 'Preauth Approved' else '',
            'approved_amount': 450000.0 if new_status == 'Preauth Approved' else 0
        }
    }
    
    response = requests.put(f"{BASE_URL}/update-status", headers=headers, json=data)
    print(f"\nUpdate Status to {new_status} Response:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def get_current_status(preauth_id):
    """Get current status and allowed transitions"""
    response = requests.get(f"{BASE_URL}/current-status/{preauth_id}", headers=HEADERS)
    print(f"\nCurrent Status Response:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def get_status_history(preauth_id):
    """Get status history"""
    response = requests.get(f"{BASE_URL}/status-history/{preauth_id}", headers=HEADERS)
    print(f"\nStatus History Response:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def submit_discharge(preauth_id):
    """Submit discharge information"""
    data = {
        'preauth_id': preauth_id,
        'discharge_data': {
            'discharge_date': datetime.now().isoformat(),
            'actual_cost': 480000.0,
            'discharge_summary': 'Patient discharged successfully after cardiac surgery',
            'final_diagnosis': 'I25.9 - Ischemic heart disease, unspecified'
        }
    }
    
    response = requests.post(f"{BASE_URL}/submit-discharge", headers=HEADERS, json=data)
    print(f"\nSubmit Discharge Response:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def demonstrate_workflow():
    """Demonstrate the complete preauth workflow"""
    print("=== PREAUTH PROCESS WORKFLOW DEMONSTRATION ===\n")
    
    # 1. Submit preauth request (starts with 'Preauth Registered')
    print("1. Submitting preauth request...")
    submit_result = submit_preauth()
    preauth_id = submit_result['data']['preauth_id']
    
    # 2. Check current status
    print("\n2. Checking current status...")
    get_current_status(preauth_id)
    
    # 3. Preauth Executive transitions: Preauth Registered -> Need More Info
    print("\n3. Preauth Executive: Moving to 'Need More Info'...")
    update_status(preauth_id, 'Need More Info', 'preauth_executive')
    
    # 4. Preauth Executive transitions: Need More Info -> Info Submitted
    print("\n4. Preauth Executive: Moving to 'Info Submitted'...")
    update_status(preauth_id, 'Info Submitted', 'preauth_executive')
    
    # 5. Processor transitions: Info Submitted -> Preauth Approved
    print("\n5. Processor: Moving to 'Preauth Approved'...")
    update_status(preauth_id, 'Preauth Approved', 'processor')
    
    # 6. Submit discharge
    print("\n6. Submitting discharge information...")
    submit_discharge(preauth_id)
    
    # 7. Processor transitions: Discharge Submitted -> Discharge Approved
    print("\n7. Processor: Moving to 'Discharge Approved'...")
    update_status(preauth_id, 'Discharge Approved', 'processor')
    
    # 8. Get final status history
    print("\n8. Final status history...")
    get_status_history(preauth_id)

def demonstrate_role_restrictions():
    """Demonstrate role-based access restrictions"""
    print("\n=== ROLE-BASED ACCESS DEMONSTRATION ===\n")
    
    preauth_id = "PA_2024_001"
    
    # Try invalid transition as processor
    print("1. Trying invalid transition as processor...")
    update_status(preauth_id, 'Info Submitted', 'processor')  # This should fail
    
    # Try valid transition as processor
    print("\n2. Trying valid transition as processor...")
    update_status(preauth_id, 'Preauth Approved', 'processor')  # This should work

if __name__ == "__main__":
    # Run the demonstration
    demonstrate_workflow()
    demonstrate_role_restrictions()
    
    print("\n=== STATUS TRANSITION MATRIX ===")
    print("""
    PREAUTH EXECUTIVE ROLE:
    - Preauth Registered -> Need More Info, Preauth Approved, Preauth Denial
    - Need More Info -> Info Submitted
    - Discharge Submitted -> Discharge NMI, Discharge Approved, Discharge Denial
    - Discharge NMI -> Discharge NMI Submitted
    
    PROCESSOR ROLE:
    - Preauth Registered -> Need More Info, Preauth Approved, Preauth Denial
    - Discharge Submitted -> Discharge NMI, Discharge Approved, Discharge Denial
    
    INITIAL STATUS: Preauth Registered (when preauth form is submitted)
    """)
