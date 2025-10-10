# Preauth Process API - Curl Test Commands

# Base URL and Headers
BASE_URL="http://localhost:5000/api/v1/preauth-process"
HEADERS='Content-Type: application/json
X-Hospital-ID: HOSP_001
X-User-ID: test_user
X-User-Name: Test User
X-User-Role: preauth_executive'

echo "=== PREAUTH PROCESS API TESTING ==="
echo ""

# 1. Submit Preauth Request
echo "1. SUBMIT PREAUTH REQUEST"
echo "POST $BASE_URL/submit"
curl -X POST "$BASE_URL/submit" \
  -H "Content-Type: application/json" \
  -H "X-Hospital-ID: HOSP_001" \
  -H "X-User-ID: test_user" \
  -H "X-User-Name: Test User" \
  -H "X-User-Role: preauth_executive" \
  -d '{
    "patient_id": "PAT_001",
    "preauth_id": "PA_2024_001",
    "insurance_provider": "Apollo Munich Health Insurance",
    "policy_number": "POL123456789",
    "treatment_type": "Cardiac Surgery",
    "diagnosis_code": "I25.9",
    "estimated_cost": 500000.0,
    "requested_amount": 500000.0,
    "policy_holder_name": "John Doe",
    "policy_holder_relation": "self",
    "doctor_name": "Dr. Smith",
    "hospital_name": "Apollo Hospital",
    "remarks": "Urgent cardiac surgery required"
  }' | jq '.'

echo ""
echo "---"
echo ""

# 2. Update Status - Preauth Executive: Need More Info
echo "2. UPDATE STATUS - PREAUTH EXECUTIVE: NEED MORE INFO"
echo "PUT $BASE_URL/update-status"
curl -X PUT "$BASE_URL/update-status" \
  -H "Content-Type: application/json" \
  -H "X-Hospital-ID: HOSP_001" \
  -H "X-User-ID: test_user" \
  -H "X-User-Name: Test User" \
  -H "X-User-Role: preauth_executive" \
  -d '{
    "preauth_id": "PA_2024_001",
    "new_status": "Need More Info",
    "remarks": "Additional medical reports required",
    "state_data": {
      "required_documents": ["ECG Report", "Echocardiogram", "Blood Test Results"]
    }
  }' | jq '.'

echo ""
echo "---"
echo ""

# 3. Update Status - Preauth Executive: Info Submitted
echo "3. UPDATE STATUS - PREAUTH EXECUTIVE: INFO SUBMITTED"
echo "PUT $BASE_URL/update-status"
curl -X PUT "$BASE_URL/update-status" \
  -H "Content-Type: application/json" \
  -H "X-Hospital-ID: HOSP_001" \
  -H "X-User-ID: test_user" \
  -H "X-User-Name: Test User" \
  -H "X-User-Role: preauth_executive" \
  -d '{
    "preauth_id": "PA_2024_001",
    "new_status": "Info Submitted",
    "remarks": "All required documents submitted",
    "state_data": {
      "submitted_documents": ["ECG Report", "Echocardiogram", "Blood Test Results"],
      "submission_date": "2024-01-15T12:00:00Z"
    }
  }' | jq '.'

echo ""
echo "---"
echo ""

# 4. Update Status - Processor: Preauth Approved
echo "4. UPDATE STATUS - PROCESSOR: PREAUTH APPROVED"
echo "PUT $BASE_URL/update-status"
curl -X PUT "$BASE_URL/update-status" \
  -H "Content-Type: application/json" \
  -H "X-Hospital-ID: HOSP_001" \
  -H "X-User-ID: processor_user" \
  -H "X-User-Name: Processor User" \
  -H "X-User-Role: processor" \
  -d '{
    "preauth_id": "PA_2024_001",
    "new_status": "Preauth Approved",
    "remarks": "Preauth approved after review",
    "state_data": {
      "approval_reference": "APP_REF_001",
      "approved_amount": 450000.0,
      "approval_notes": "Approved with 10% reduction in room rent"
    }
  }' | jq '.'

echo ""
echo "---"
echo ""

# 5. Submit Discharge Information
echo "5. SUBMIT DISCHARGE INFORMATION"
echo "POST $BASE_URL/submit-discharge"
curl -X POST "$BASE_URL/submit-discharge" \
  -H "Content-Type: application/json" \
  -H "X-Hospital-ID: HOSP_001" \
  -H "X-User-ID: test_user" \
  -H "X-User-Name: Test User" \
  -H "X-User-Role: preauth_executive" \
  -d '{
    "preauth_id": "PA_2024_001",
    "discharge_data": {
      "discharge_date": "2024-01-20T14:00:00Z",
      "actual_cost": 480000.0,
      "discharge_summary": "Patient discharged successfully after cardiac surgery",
      "final_diagnosis": "I25.9 - Ischemic heart disease, unspecified",
      "complications": "None",
      "follow_up_required": true,
      "follow_up_date": "2024-02-01T10:00:00Z"
    }
  }' | jq '.'

echo ""
echo "---"
echo ""

# 6. Update Status - Processor: Discharge Approved
echo "6. UPDATE STATUS - PROCESSOR: DISCHARGE APPROVED"
echo "PUT $BASE_URL/update-status"
curl -X PUT "$BASE_URL/update-status" \
  -H "Content-Type: application/json" \
  -H "X-Hospital-ID: HOSP_001" \
  -H "X-User-ID: processor_user" \
  -H "X-User-Name: Processor User" \
  -H "X-User-Role: processor" \
  -d '{
    "preauth_id": "PA_2024_001",
    "new_status": "Discharge Approved",
    "remarks": "Discharge approved after verification",
    "state_data": {
      "final_approved_amount": 480000.0,
      "settlement_reference": "SET_REF_001"
    }
  }' | jq '.'

echo ""
echo "---"
echo ""

# 7. Get Current Status
echo "7. GET CURRENT STATUS"
echo "GET $BASE_URL/current-status/PA_2024_001"
curl -X GET "$BASE_URL/current-status/PA_2024_001" \
  -H "Content-Type: application/json" \
  -H "X-Hospital-ID: HOSP_001" \
  -H "X-User-ID: test_user" \
  -H "X-User-Name: Test User" \
  -H "X-User-Role: preauth_executive" | jq '.'

echo ""
echo "---"
echo ""

# 8. Get Status History
echo "8. GET STATUS HISTORY"
echo "GET $BASE_URL/status-history/PA_2024_001"
curl -X GET "$BASE_URL/status-history/PA_2024_001" \
  -H "Content-Type: application/json" \
  -H "X-Hospital-ID: HOSP_001" \
  -H "X-User-ID: test_user" \
  -H "X-User-Name: Test User" \
  -H "X-User-Role: preauth_executive" | jq '.'

echo ""
echo "---"
echo ""

# 9. List Preauth Requests
echo "9. LIST PREAUTH REQUESTS"
echo "GET $BASE_URL/list"
curl -X GET "$BASE_URL/list" \
  -H "Content-Type: application/json" \
  -H "X-Hospital-ID: HOSP_001" \
  -H "X-User-ID: test_user" \
  -H "X-User-Name: Test User" \
  -H "X-User-Role: preauth_executive" | jq '.'

echo ""
echo "---"
echo ""

# 10. List with Status Filter
echo "10. LIST WITH STATUS FILTER"
echo "GET $BASE_URL/list?status=Preauth%20Registered&limit=5"
curl -X GET "$BASE_URL/list?status=Preauth%20Registered&limit=5" \
  -H "Content-Type: application/json" \
  -H "X-Hospital-ID: HOSP_001" \
  -H "X-User-ID: test_user" \
  -H "X-User-Name: Test User" \
  -H "X-User-Role: preauth_executive" | jq '.'

echo ""
echo "---"
echo ""

# 11. Test Invalid Status Transition (Error Case)
echo "11. TEST INVALID STATUS TRANSITION (ERROR CASE)"
echo "PUT $BASE_URL/update-status"
curl -X PUT "$BASE_URL/update-status" \
  -H "Content-Type: application/json" \
  -H "X-Hospital-ID: HOSP_001" \
  -H "X-User-ID: test_user" \
  -H "X-User-Name: Test User" \
  -H "X-User-Role: preauth_executive" \
  -d '{
    "preauth_id": "PA_2024_001",
    "new_status": "Need More Info",
    "remarks": "This should fail - invalid transition"
  }' | jq '.'

echo ""
echo "---"
echo ""

# 12. Test Missing Required Fields (Error Case)
echo "12. TEST MISSING REQUIRED FIELDS (ERROR CASE)"
echo "POST $BASE_URL/submit"
curl -X POST "$BASE_URL/submit" \
  -H "Content-Type: application/json" \
  -H "X-Hospital-ID: HOSP_001" \
  -H "X-User-ID: test_user" \
  -H "X-User-Name: Test User" \
  -H "X-User-Role: preauth_executive" \
  -d '{
    "patient_id": "PAT_002",
    "preauth_id": "PA_2024_002"
  }' | jq '.'

echo ""
echo "=== TESTING COMPLETE ==="
