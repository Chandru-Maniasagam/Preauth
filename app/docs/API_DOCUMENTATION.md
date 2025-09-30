# API Documentation

## Overview

The RCM SaaS Application provides a comprehensive RESTful API for managing patients, preauthorization requests, and business intelligence dashboards for Indian hospitals.

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

All API endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Common Headers

```
Content-Type: application/json
Authorization: Bearer <jwt-token>
X-Hospital-ID: <hospital-id>
X-User-ID: <user-id>
```

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "data": { ... },
  "message": "Success message",
  "status": "success",
  "timestamp": "2023-09-24T10:30:00Z"
}
```

### Error Response
```json
{
  "error": "Error message",
  "status": "error",
  "status_code": 400,
  "timestamp": "2023-09-24T10:30:00Z"
}
```

### Paginated Response
```json
{
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  },
  "status": "success"
}
```

## Endpoints

### Patient Management

#### Get All Patients
```http
GET /patients
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 20)
- `search` (string): Search term
- `status` (string): Filter by status (active, inactive)

**Response:**
```json
{
  "data": [
    {
      "id": "patient-uuid",
      "hospital_id": "hospital-uuid",
      "patient_id": "PAT_HOSP_20230924_ABC123",
      "first_name": "John",
      "last_name": "Doe",
      "date_of_birth": "1990-01-01",
      "gender": "male",
      "phone_number": "+91 98765 43210",
      "email": "john.doe@email.com",
      "blood_group": "O+",
      "is_verified": true,
      "created_at": "2023-09-24T10:30:00Z",
      "updated_at": "2023-09-24T10:30:00Z"
    }
  ],
  "pagination": { ... }
}
```

#### Create Patient
```http
POST /patients
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "phone_number": "+91 98765 43210",
  "email": "john.doe@email.com",
  "address": {
    "street": "123 Main St",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001"
  },
  "blood_group": "O+"
}
```

#### Get Patient by ID
```http
GET /patients/{patient_id}
```

#### Update Patient
```http
PUT /patients/{patient_id}
```

#### Delete Patient
```http
DELETE /patients/{patient_id}
```

### Preauth Management

#### Get All Preauth Requests
```http
GET /preauth
```

**Query Parameters:**
- `page` (int): Page number
- `per_page` (int): Items per page
- `status` (string): Filter by status
- `priority` (string): Filter by priority
- `insurance_provider` (string): Filter by insurance provider
- `date_from` (string): Start date filter
- `date_to` (string): End date filter

#### Create Preauth Request
```http
POST /preauth
```

**Request Body:**
```json
{
  "patient_id": "patient-uuid",
  "insurance_provider": "ICICI Lombard",
  "policy_number": "POL123456789",
  "policy_holder_name": "John Doe",
  "policy_holder_relation": "self",
  "treatment_type": "Surgery",
  "diagnosis_code": "K35.9",
  "procedure_codes": ["12345", "67890"],
  "estimated_cost": 50000,
  "requested_amount": 45000,
  "treatment_date": "2023-10-01",
  "doctor_name": "Dr. Smith",
  "doctor_license": "MED123456",
  "priority": "normal"
}
```

#### Submit Preauth Request
```http
POST /preauth/{preauth_id}/submit
```

#### Approve Preauth Request
```http
POST /preauth/{preauth_id}/approve
```

**Request Body:**
```json
{
  "approved_amount": 40000,
  "approval_reference": "APP123456789",
  "remarks": "Approved with conditions"
}
```

#### Reject Preauth Request
```http
POST /preauth/{preauth_id}/reject
```

**Request Body:**
```json
{
  "rejection_reason": "Insufficient documentation"
}
```

### Dashboard & Analytics

#### Get Dashboard Overview
```http
GET /dashboard/overview
```

**Query Parameters:**
- `date_from` (string): Start date
- `date_to` (string): End date

**Response:**
```json
{
  "data": {
    "total_patients": 1250,
    "total_preauth_requests": 350,
    "approved_preauth_requests": 280,
    "pending_preauth_requests": 45,
    "rejected_preauth_requests": 25,
    "total_revenue": 1250000,
    "approval_rate": 80.0,
    "average_processing_time": 2.5
  }
}
```

#### Get Preauth Analytics
```http
GET /dashboard/preauth-analytics
```

**Query Parameters:**
- `date_from` (string): Start date
- `date_to` (string): End date
- `group_by` (string): Group by (day, week, month)

#### Get Revenue Analytics
```http
GET /dashboard/revenue-analytics
```

#### Get Patient Analytics
```http
GET /dashboard/patient-analytics
```

### User Management

#### Get All Users
```http
GET /users
```

#### Create User
```http
POST /users
```

**Request Body:**
```json
{
  "email": "user@hospital.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone_number": "+91 98765 43210",
  "role": "doctor",
  "department": "Cardiology",
  "designation": "Senior Doctor"
}
```

### Notifications

#### Get Notifications
```http
GET /notifications
```

#### Mark Notification as Read
```http
POST /notifications/{notification_id}/read
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource conflict |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

## Rate Limiting

API requests are rate limited to prevent abuse:
- Default: 1000 requests per hour per IP
- Authenticated users: Higher limits based on role
- Rate limit headers included in responses:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## Pagination

List endpoints support pagination:
- `page`: Page number (starts from 1)
- `per_page`: Items per page (max 100)
- Response includes pagination metadata

## Filtering and Sorting

Many endpoints support filtering and sorting:
- Use query parameters for filters
- Use `sort` parameter for sorting
- Use `order` parameter for sort direction (asc, desc)

## File Uploads

File uploads are supported for documents:
- Maximum file size: 16MB
- Allowed formats: PDF, PNG, JPG, JPEG, DOC, DOCX
- Files stored in Firebase Storage
- Secure URLs generated for access

## Webhooks

The API supports webhooks for real-time notifications:
- Configure webhook URLs in hospital settings
- Events: preauth_status_change, patient_created, etc.
- Webhook payload includes event data and signature

## SDKs and Libraries

Official SDKs available for:
- Python
- JavaScript/Node.js
- Java
- PHP

## Support

For API support:
- Check the documentation
- Create an issue in the repository
- Contact the development team
