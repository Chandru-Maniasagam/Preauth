# Database Schema Documentation

## Overview

This document outlines the Firestore database schema and Firebase Storage structure for the RCM SaaS Application.

## Firestore Collections

### 1. Hospitals Collection (`hospitals`)

**Purpose**: Store hospital information and configuration

**Document Structure**:
```json
{
  "id": "hospital-uuid",
  "name": "Apollo Hospitals",
  "registration_number": "HOSP123456",
  "address": {
    "street": "123 Hospital Road",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001",
    "country": "India"
  },
  "contact_info": {
    "phone": "+91-22-12345678",
    "email": "info@apollo.com",
    "website": "https://apollo.com"
  },
  "license_info": {
    "license_number": "LIC123456",
    "license_expiry": "2025-12-31",
    "issuing_authority": "State Medical Council"
  },
  "subscription_plan": "premium",
  "subscription_status": "active",
  "subscription_expires_at": "2024-12-31T23:59:59Z",
  "max_patients": 10000,
  "max_users": 50,
  "features": ["advanced_analytics", "api_access", "custom_workflows"],
  "timezone": "Asia/Kolkata",
  "currency": "INR",
  "language": "en",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-09-24T10:30:00Z",
  "is_active": true
}
```

**Indexes**:
- `hospital_id` (single field)
- `subscription_status` (single field)
- `created_at` (single field)

### 2. Patients Collection (`patients`)

**Purpose**: Store patient information and medical records

**Document Structure**:
```json
{
  "id": "patient-uuid",
  "hospital_id": "hospital-uuid",
  "patient_id": "PAT_HOSP_20230924_ABC123",
  "first_name": "John",
  "last_name": "Doe",
  "middle_name": "Michael",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "phone_number": "+91 98765 43210",
  "email": "john.doe@email.com",
  "address": {
    "street": "456 Patient Street",
    "area": "Andheri",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400058",
    "country": "India"
  },
  "emergency_contact": {
    "name": "Jane Doe",
    "relation": "spouse",
    "phone": "+91 98765 43211",
    "email": "jane.doe@email.com"
  },
  "insurance_info": {
    "primary_insurance": "ICICI Lombard",
    "policy_number": "POL123456789",
    "policy_holder_name": "John Doe",
    "policy_holder_relation": "self",
    "coverage_amount": 500000,
    "valid_from": "2023-01-01",
    "valid_until": "2023-12-31"
  },
  "medical_history": [
    {
      "record_id": "record-uuid",
      "date": "2023-09-01T10:00:00Z",
      "type": "consultation",
      "description": "Regular checkup",
      "doctor": "Dr. Smith",
      "diagnosis": "Hypertension",
      "treatment": "Medication prescribed",
      "attachments": ["doc-uuid-1", "doc-uuid-2"]
    }
  ],
  "allergies": [
    {
      "allergy": "Penicillin",
      "severity": "severe",
      "added_date": "2023-01-01T00:00:00Z"
    }
  ],
  "medications": [
    {
      "medication_id": "med-uuid",
      "name": "Metformin",
      "dosage": "500mg",
      "frequency": "twice daily",
      "start_date": "2023-01-01T00:00:00Z",
      "end_date": null,
      "prescribed_by": "Dr. Smith",
      "is_active": true
    }
  ],
  "blood_group": "O+",
  "height": 175.5,
  "weight": 70.0,
  "notes": "Patient notes",
  "photo_url": "gs://bucket/patients/hospital-id/patient-id/photo.jpg",
  "documents": ["doc-uuid-1", "doc-uuid-2"],
  "last_visit": "2023-09-24T10:30:00Z",
  "visit_count": 5,
  "is_verified": true,
  "verification_date": "2023-01-01T00:00:00Z",
  "verification_method": "aadhaar",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-09-24T10:30:00Z",
  "is_active": true
}
```

**Indexes**:
- `hospital_id, created_at` (composite)
- `patient_id, hospital_id` (composite)
- `phone_number, hospital_id` (composite)
- `email, hospital_id` (composite)
- `is_verified, hospital_id` (composite)

### 3. Claims Collection (`claims`)

**Purpose**: Store preauthorization requests and claims (renamed from preauth_requests)

**Document Structure**:
```json
{
  "id": "claim-uuid",
  "hospital_id": "hospital-uuid",
  "patient_id": "patient-uuid",
  "preauth_id": "PA_HOSP_20230924_XYZ789",
  "claim_type": "preauth", // preauth, claim, appeal
  "insurance_provider": "ICICI Lombard",
  "policy_number": "POL123456789",
  "policy_holder_name": "John Doe",
  "policy_holder_relation": "self",
  "treatment_type": "Surgery",
  "diagnosis_code": "K35.9",
  "procedure_codes": ["12345", "67890"],
  "estimated_cost": 50000.0,
  "requested_amount": 45000.0,
  "approved_amount": 40000.0,
  "status": "approved", // pending, submitted, under_review, approved, rejected, expired, cancelled
  "priority": "normal", // low, normal, high, urgent
  "treatment_date": "2023-10-01",
  "admission_date": "2023-10-01",
  "discharge_date": "2023-10-05",
  "doctor_name": "Dr. Smith",
  "doctor_license": "MED123456",
  "hospital_name": "Apollo Hospitals",
  "room_type": "private",
  "room_rent": 2000.0,
  "consultation_fee": 1000.0,
  "investigation_cost": 5000.0,
  "medicine_cost": 3000.0,
  "surgery_cost": 35000.0,
  "other_costs": 2000.0,
  "remarks": "Patient requires immediate surgery",
  "insurance_remarks": "Approved with conditions",
  "documents": [
    {
      "document_id": "doc-uuid",
      "name": "Medical Report.pdf",
      "type": "medical_report",
      "url": "gs://bucket/claims/hospital-id/preauth-id/medical-report.pdf",
      "uploaded_at": "2023-09-24T10:30:00Z",
      "uploaded_by": "user-uuid",
      "size": 1024000,
      "is_required": true
    }
  ],
  "attachments": ["doc-uuid-1", "doc-uuid-2"],
  "submission_date": "2023-09-24T10:30:00Z",
  "approval_date": "2023-09-25T14:30:00Z",
  "rejection_date": null,
  "rejection_reason": "",
  "approval_reference": "APP123456789",
  "validity_period": 30,
  "expiry_date": "2023-10-24T10:30:00Z",
  "follow_up_required": false,
  "follow_up_date": null,
  "assigned_to": "user-uuid",
  "assigned_date": "2023-09-24T10:30:00Z",
  "completion_date": "2023-09-25T14:30:00Z",
  "is_urgent": false,
  "urgent_reason": "",
  "patient_contribution": 5000.0,
  "insurance_contribution": 40000.0,
  "copay_amount": 1000.0,
  "deductible_amount": 2000.0,
  "coverage_percentage": 80.0,
  "exclusions": ["cosmetic procedures"],
  "pre_existing_conditions": ["diabetes"],
  "waiting_period_applicable": false,
  "waiting_period_days": 0,
  "claim_number": "CLM123456789",
  "tpa_name": "MediAssist",
  "tpa_contact": {
    "phone": "+91-80-12345678",
    "email": "support@mediassist.com"
  },
  "verification_status": "verified",
  "verification_date": "2023-09-24T11:00:00Z",
  "verification_notes": "All documents verified",
  "created_at": "2023-09-24T10:30:00Z",
  "updated_at": "2023-09-25T14:30:00Z",
  "is_active": true
}
```

**Indexes**:
- `hospital_id, status, created_at` (composite)
- `patient_id, hospital_id` (composite)
- `insurance_provider, status` (composite)
- `created_at, status` (composite)
- `preauth_id, hospital_id` (composite)
- `claim_type, status` (composite)
- `submission_date, status` (composite)
- `approval_date, status` (composite)

### 4. Preauth States Collection (`preauth_states`)

**Purpose**: Track state changes in preauth/claim workflow

**Document Structure**:
```json
{
  "id": "state-uuid",
  "preauth_id": "preauth-uuid",
  "hospital_id": "hospital-uuid",
  "state": "approved",
  "previous_state": "under_review",
  "state_data": {
    "approver": "user-uuid",
    "approval_amount": 40000.0,
    "conditions": ["Follow-up required"]
  },
  "remarks": "Approved with conditions",
  "changed_by": "user-uuid",
  "changed_at": "2023-09-25T14:30:00Z",
  "duration_minutes": 120,
  "is_automatic": false,
  "trigger_event": "manual_approval",
  "next_actions": [
    {
      "action": "Notify patient",
      "due_date": "2023-09-25T16:00:00Z",
      "created_at": "2023-09-25T14:30:00Z",
      "completed": false
    }
  ],
  "assigned_to": "user-uuid",
  "estimated_completion": "2023-09-25T16:00:00Z",
  "actual_completion": "2023-09-25T15:45:00Z",
  "notes": "State change notes",
  "attachments": ["doc-uuid-1"],
  "notifications_sent": [
    {
      "notification_id": "notif-uuid",
      "type": "email",
      "sent_at": "2023-09-25T14:35:00Z"
    }
  ],
  "escalation_level": 0,
  "is_escalated": false,
  "escalation_reason": "",
  "sla_breach": false,
  "sla_breach_reason": "",
  "created_at": "2023-09-25T14:30:00Z",
  "updated_at": "2023-09-25T14:30:00Z",
  "is_active": true
}
```

**Indexes**:
- `preauth_id, state, created_at` (composite)
- `hospital_id, state, created_at` (composite)
- `changed_by, created_at` (composite)

### 5. Users Collection (`users`)

**Purpose**: Store user accounts and permissions

**Document Structure**:
```json
{
  "id": "user-uuid",
  "hospital_id": "hospital-uuid",
  "user_id": "USR_HOSP_001",
  "email": "doctor@apollo.com",
  "username": "dr_smith",
  "first_name": "John",
  "last_name": "Smith",
  "phone_number": "+91 98765 43210",
  "role": "doctor",
  "permissions": ["patients:read", "patients:create", "claims:read"],
  "department": "Cardiology",
  "designation": "Senior Doctor",
  "employee_id": "EMP001",
  "is_active": true,
  "is_verified": true,
  "last_login": "2023-09-24T10:30:00Z",
  "login_count": 45,
  "working_hours": {
    "monday": {"start": "09:00", "end": "17:00"},
    "tuesday": {"start": "09:00", "end": "17:00"},
    "wednesday": {"start": "09:00", "end": "17:00"},
    "thursday": {"start": "09:00", "end": "17:00"},
    "friday": {"start": "09:00", "end": "17:00"},
    "saturday": {"start": "09:00", "end": "13:00"},
    "sunday": {"start": "00:00", "end": "00:00"}
  },
  "specializations": ["Cardiology", "Internal Medicine"],
  "license_number": "MED123456",
  "license_expiry": "2025-12-31",
  "qualifications": ["MBBS", "MD Cardiology"],
  "experience_years": 10,
  "photo_url": "gs://bucket/users/hospital-id/user-id/photo.jpg",
  "address": {
    "street": "789 Doctor Street",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001"
  },
  "emergency_contact": {
    "name": "Jane Smith",
    "relation": "spouse",
    "phone": "+91 98765 43211"
  },
  "assigned_patients": ["patient-uuid-1", "patient-uuid-2"],
  "assigned_preauths": ["preauth-uuid-1", "preauth-uuid-2"],
  "workload_capacity": 100,
  "current_workload": 25,
  "skills": ["Cardiology", "Echocardiography"],
  "certifications": [
    {
      "certification_id": "cert-uuid",
      "name": "Fellowship in Cardiology",
      "issuer": "Cardiac Society of India",
      "issue_date": "2020-01-01",
      "expiry_date": "2025-01-01",
      "credential_id": "FIC123456"
    }
  ],
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-09-24T10:30:00Z",
  "is_active": true
}
```

**Indexes**:
- `hospital_id, role, is_active` (composite)
- `email, hospital_id` (composite)
- `user_id, hospital_id` (composite)
- `department, is_active` (composite)

## Firebase Storage Structure

### Storage Bucket: `mv20-a1a09.firebasestorage.app`

```
gs://mv20-a1a09.firebasestorage.app/
├── patients/
│   └── {hospital_id}/
│       └── {patient_id}/
│           ├── documents/
│           │   ├── medical_reports/
│           │   ├── prescriptions/
│           │   ├── lab_reports/
│           │   ├── imaging_reports/
│           │   └── identity_documents/
│           ├── photos/
│           │   └── profile_photo.jpg
│           └── temp/
├── claims/
│   └── {hospital_id}/
│       └── {preauth_id}/
│           ├── documents/
│           │   ├── medical_reports/
│           │   ├── insurance_documents/
│           │   ├── discharge_summaries/
│           │   └── supporting_documents/
│           ├── attachments/
│           └── temp/
├── documents/
│   └── {hospital_id}/
│       ├── patient_documents/
│       ├── claim_documents/
│       ├── medical_reports/
│       ├── insurance_documents/
│       └── identity_documents/
├── reports/
│   └── {hospital_id}/
│       ├── analytics/
│       ├── exports/
│       └── backups/
├── temp/
│   └── {hospital_id}/
│       └── uploads/
└── backups/
    └── {hospital_id}/
        ├── daily/
        ├── weekly/
        └── monthly/
```

### Document Storage Rules

1. **Patient Documents**: `patients/{hospital_id}/{patient_id}/documents/{document_type}/`
2. **Claim Documents**: `claims/{hospital_id}/{preauth_id}/documents/`
3. **General Documents**: `documents/{hospital_id}/{document_type}/`
4. **Temporary Files**: `temp/{hospital_id}/uploads/`

### File Naming Convention

- **Patient Documents**: `{document_type}_{timestamp}_{random_id}.{extension}`
- **Claim Documents**: `{document_type}_{preauth_id}_{timestamp}.{extension}`
- **General Documents**: `{document_type}_{hospital_id}_{timestamp}.{extension}`

### Security Rules

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Patients documents
    match /patients/{hospitalId}/{patientId}/{allPaths=**} {
      allow read, write: if request.auth != null 
        && request.auth.token.hospital_id == hospitalId;
    }
    
    // Claims documents
    match /claims/{hospitalId}/{preauthId}/{allPaths=**} {
      allow read, write: if request.auth != null 
        && request.auth.token.hospital_id == hospitalId;
    }
    
    // General documents
    match /documents/{hospitalId}/{allPaths=**} {
      allow read, write: if request.auth != null 
        && request.auth.token.hospital_id == hospitalId;
    }
    
    // Temporary files (auto-delete after 24 hours)
    match /temp/{hospitalId}/{allPaths=**} {
      allow read, write: if request.auth != null 
        && request.auth.token.hospital_id == hospitalId;
    }
  }
}
```

## Data Relationships

### Primary Relationships

1. **Hospital → Patients**: One-to-Many
2. **Hospital → Users**: One-to-Many
3. **Hospital → Claims**: One-to-Many
4. **Patient → Claims**: One-to-Many
5. **User → Assigned Patients**: Many-to-Many
6. **User → Assigned Claims**: Many-to-Many
7. **Claim → Preauth States**: One-to-Many

### Foreign Key References

- All documents reference `hospital_id` for multi-tenancy
- Claims reference `patient_id` for patient association
- Preauth states reference `preauth_id` for claim tracking
- Documents reference their parent entity IDs

## Indexing Strategy

### Composite Indexes

1. **Query Pattern**: Get patients by hospital and creation date
   - Index: `hospital_id, created_at`

2. **Query Pattern**: Get claims by hospital and status
   - Index: `hospital_id, status, created_at`

3. **Query Pattern**: Get claims by patient
   - Index: `patient_id, hospital_id`

4. **Query Pattern**: Get users by hospital and role
   - Index: `hospital_id, role, is_active`

### Single Field Indexes

- `hospital_id` (for multi-tenancy)
- `email` (for user lookup)
- `phone_number` (for patient lookup)
- `status` (for filtering)
- `created_at` (for sorting)

## Data Retention and Archiving

### Retention Policies

1. **Active Data**: Keep indefinitely
2. **Archived Data**: Move to cold storage after 7 years
3. **Audit Logs**: Keep for 10 years
4. **Temporary Files**: Auto-delete after 24 hours

### Archiving Strategy

1. **Patient Data**: Archive after 7 years of inactivity
2. **Claim Data**: Archive after 5 years of completion
3. **User Data**: Archive after 2 years of inactivity
4. **Documents**: Archive based on parent entity policy

## Backup and Recovery

### Backup Strategy

1. **Daily Backups**: Full database backup
2. **Weekly Backups**: Incremental backup
3. **Monthly Backups**: Full backup with compression
4. **Storage Backups**: Daily file system backup

### Recovery Procedures

1. **Point-in-time Recovery**: Available for last 30 days
2. **Cross-region Replication**: For disaster recovery
3. **Data Export**: JSON format for migration
4. **Document Recovery**: From Firebase Storage backups
