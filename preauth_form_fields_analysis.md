# Preauth Form Fields Analysis

## Overview
This document provides a comprehensive analysis of all fields in the preauth form and their mapping to the claims document structure.

## Field Categories

### 1. **MANDATORY FIELDS** (Required for Form Submission)

#### Basic Patient Information
| Form Field | Claims Field | Type | Character Box | Description |
|------------|--------------|------|---------------|-------------|
| `patient_name` | `patient_name` | String | ✅ (50 chars) | Full name of the patient |
| `mobile_number` | `mobile_number` | String | ✅ (10 chars) | Primary contact number |
| `uhid` | `uhid` | String | ✅ (20 chars) | Unique Health ID |
| `claim_type` | `claim_type` | Select | ❌ | IP/OP/Day care |
| `admission_type` | `admission_type` | Radio | ❌ | Planned/Emergency |

### 2. **OPTIONAL FIELDS** (Can be filled later)

#### Patient Demographics
| Form Field | Claims Field | Type | Character Box | Description |
|------------|--------------|------|---------------|-------------|
| `gender` | `gender` | Radio | ❌ | Male/Female/Other |
| `date_of_birth` | `date_of_birth` | Date | ❌ | Patient's date of birth |
| `alternative_contact` | `alternative_contact` | String | ✅ (10 chars) | Relative's contact number |

#### Patient Identifiers
| Form Field | Claims Field | Type | Character Box | Description |
|------------|--------------|------|---------------|-------------|
| `customer_id` | `customer_id` | String | ✅ (20 chars) | Insured card ID number |
| `policy_number` | `policy_number` | String | ✅ (30 chars) | Policy number/corporate name |
| `employee_id` | `employee_id` | String | ✅ (20 chars) | Employee ID |

#### Address Information
| Form Field | Claims Field | Type | Character Box | Description |
|------------|--------------|------|---------------|-------------|
| `address_street` | `address.street` | String | ✅ (50 chars) | Street address |
| `address_city` | `address.city` | String | ✅ (30 chars) | City |
| `address_state` | `address.state` | String | ✅ (30 chars) | State |
| `address_pincode` | `address.pincode` | String | ✅ (6 chars) | Pincode |
| `occupation` | `occupation` | Select | ❌ | Service/Self employed/Retired/Business owner |

#### Insurance Information
| Form Field | Claims Field | Type | Character Box | Description |
|------------|--------------|------|---------------|-------------|
| `additional_policy` | `additional_policy` | Radio | ❌ | Yes/No for other insurance |
| `additional_policy_company` | `additional_policy_details.company` | String | ❌ | Other insurance company name |
| `additional_policy_details` | `additional_policy_details.details` | String | ❌ | Other insurance details |
| `family_physician` | `family_physician` | Radio | ❌ | Yes/No for family physician |
| `family_physician_name` | `family_physician_details.name` | String | ❌ | Family physician name |
| `family_physician_contact` | `family_physician_details.contact` | String | ❌ | Family physician contact |

#### Medical Information
| Form Field | Claims Field | Type | Character Box | Description |
|------------|--------------|------|---------------|-------------|
| `speciality_id` | `speciality_id` | Select | ❌ | Medical speciality |
| `treating_doctor_id` | `treating_doctor_id` | Select | ❌ | Treating doctor selection |
| `treating_doctor_name` | `treating_doctor_name` | String | ❌ | Doctor name (auto-filled) |
| `treating_doctor_contact` | `treating_doctor_contact` | String | ❌ | Doctor contact (auto-filled) |
| `treating_doctor_qualification` | `treating_doctor_qualification` | String | ❌ | Doctor qualification (auto-filled) |
| `treating_doctor_registration_number` | `treating_doctor_registration` | String | ❌ | Doctor registration (auto-filled) |
| `nature_of_illness` | `nature_of_illness` | String | ✅ (100 chars) | Nature of illness/disease |
| `relevant_clinical_findings` | `clinical_findings` | String | ✅ (100 chars) | Clinical findings |
| `duration_of_present_ailment` | `duration_of_ailment` | String | ✅ (30 chars) | Duration of ailment |
| `date_of_first_consultation` | `first_consultation_date` | Date | ❌ | First consultation date |
| `past_history_present_ailment` | `past_medical_history` | String | ✅ (100 chars) | Past medical history |
| `provisional_diagnosis` | `provisional_diagnosis` | String | ✅ (50 chars) | Provisional diagnosis |
| `icd_10_code` | `icd10_code` | String | ✅ (20 chars) | ICD-10 code |

#### Admission Details
| Form Field | Claims Field | Type | Character Box | Description |
|------------|--------------|------|---------------|-------------|
| `admission_datetime` | `admission_datetime` | Date | ❌ | Date of admission |
| `admission_time` | `admission_datetime` | Time | ❌ | Time of admission |
| `ip_number` | `ip_number` | String | ✅ (20 chars) | IP number |
| `expected_length_of_stay` | `expected_length_stay` | Number | ❌ | Expected days of stay |
| `ward_type` | `ward_type` | Select | ❌ | Single room/Twin sharing/ICU/3+ beds |
| `proposed_line_of_treatment` | `proposed_treatment` | Select | ❌ | Medical/Surgical/ICU/Investigation/Non-allopathic |
| `estimated_treatment_cost` | `estimated_treatment_cost` | Number | ❌ | Estimated cost in INR |

#### Display and Control
| Form Field | Claims Field | Type | Character Box | Description |
|------------|--------------|------|---------------|-------------|
| `show_in_claims` | `show_in_claims` | Radio | ❌ | Show in claims dashboard |

### 3. **SIGNATURE FIELDS** (Not in Claims Document)

| Form Field | Type | Character Box | Description |
|------------|------|---------------|-------------|
| `patient_signature_date` | Date | ❌ | Date for patient signature |
| `doctor_signature_date` | Date | ❌ | Date for doctor signature |

### 4. **HIDDEN/SYSTEM FIELDS** (Not User Input)

| Form Field | Claims Field | Type | Description |
|------------|--------------|------|-------------|
| `hospital_id` | `hospital_id` | Hidden | Hospital identifier |
| `user_id` | `created_by` | Hidden | User creating the form |
| `user_name` | `created_by_name` | Hidden | User name creating the form |

### 5. **TPA/INSURANCE COMPANY FIELDS** (Not in Claims Document)

| Form Field | Type | Character Box | Description |
|------------|------|---------------|-------------|
| `payer_name` | String | ❌ | TPA/Insurance Company name |
| `payer_phone` | String | ❌ | Toll-free phone number |
| `payer_fax` | String | ❌ | Toll-free FAX |
| `payer_email` | Email | ❌ | Email address |
| `rohini_id` | String | ❌ | Rohini ID |
| `hospital_address` | String | ❌ | Hospital address |

## Character Box Implementation Summary

### Fields with Character Boxes (18 total):
1. `patient_name` (50 characters)
2. `mobile_number` (10 characters)
3. `uhid` (20 characters)
4. `alternative_contact` (10 characters)
5. `customer_id` (20 characters)
6. `policy_number` (30 characters)
7. `employee_id` (20 characters)
8. `address_street` (50 characters)
9. `address_city` (30 characters)
10. `address_state` (30 characters)
11. `address_pincode` (6 characters)
12. `nature_of_illness` (100 characters)
13. `relevant_clinical_findings` (100 characters)
14. `duration_of_present_ailment` (30 characters)
15. `past_history_present_ailment` (100 characters)
16. `provisional_diagnosis` (50 characters)
17. `icd_10_code` (20 characters)
18. `ip_number` (20 characters)

### Fields without Character Boxes:
- All select dropdowns
- All radio buttons
- All date/time fields
- All number fields
- All signature areas
- Auto-filled doctor information fields

## Field Validation Alignment

The preauth form fields are aligned with the claims validation in `claims.py`:

### Mandatory Fields (from claims.py validation):
- `patient_name` (min 2 characters)
- `mobile_number` (valid Indian phone format)
- `uhid` (min 3 characters)
- `claim_type` (IP/OP/Day care)
- `admission_type` (Planned/Emergency)

### Optional Fields with Validation:
- Email format validation
- Phone number format validation
- Pincode format validation
- Payer type validation
- Ward type validation
- Daycare procedure validation
- Nature of illness validation
- Cause of injury validation
- Treatment line validation
- Drug administration route validation
- Occupation validation

## Data Flow

1. **Form Submission** → Claims Collection (Firestore)
2. **Character Box Data** → Hidden input fields → Form submission
3. **Auto-filled Data** → Doctor/speciality information from API
4. **Validation** → Client-side and server-side validation
5. **PDF Generation** → HTML form with populated data

## Print/Download Features

- **Print Button**: Browser print functionality
- **PDF Download**: HTML to PDF conversion (temporarily disabled)
- **Signature Areas**: Dedicated spaces for physical signatures
- **Character Boxes**: Print-friendly individual character input boxes

