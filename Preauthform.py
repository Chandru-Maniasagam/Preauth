"""
Pre-Authorisation Form for RCM SaaS Application
Integrates HTML form with claims API for seamless data handling
"""

from flask import Blueprint, render_template_string, request, jsonify, redirect, url_for, flash, make_response
from datetime import datetime
import logging
import sys
import os
import uuid
from werkzeug.utils import secure_filename
# import pdfkit
# from weasyprint import HTML, CSS

# Add the app directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.firebase_client import FirebaseClient
from app.database.models.claim import Claim
from app.utils.helpers import generate_claim_id, calculate_age_detailed

preauth_form_bp = Blueprint('preauth_form', __name__)

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size
FIREBASE_STORAGE_COLLECTION = 'Preauthform_files'

# Firebase client will be initialized when needed
firebase_client = None
db = None

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file_to_firebase(file, claim_id, file_type):
    """Save uploaded file to Firebase Storage and return file metadata"""
    if file and allowed_file(file.filename):
        try:
            # Get Firebase Storage bucket
            firebase_client = FirebaseClient()
            bucket = firebase_client.get_storage_bucket()
            
            # Generate unique filename
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{claim_id}_{file_type}_{uuid.uuid4().hex}.{file_extension}"
            
            # Create Firebase Storage path
            firebase_path = f"{FIREBASE_STORAGE_COLLECTION}/{claim_id}/{unique_filename}"
            
            # Create blob and upload file
            blob = bucket.blob(firebase_path)
            
            # Reset file pointer to beginning
            file.seek(0)
            
            # Upload file to Firebase Storage
            blob.upload_from_file(file, content_type='application/pdf')
            
            # Make the blob publicly accessible (optional)
            blob.make_public()
            
            # Get file metadata
            file_metadata = {
                'filename': file.filename,
                'firebase_path': firebase_path,
                'public_url': blob.public_url,
                'file_size': blob.size,
                'content_type': blob.content_type,
                'uploaded_at': datetime.now().isoformat(),
                'storage_bucket': bucket.name
            }
            
            # Store file metadata in Firestore
            db = get_db()
            file_doc_ref = db.collection('Preauth_Files').document()
            file_doc_ref.set({
                'claim_id': claim_id,
                'file_type': file_type,
                'original_filename': file.filename,
                'firebase_path': firebase_path,
                'public_url': blob.public_url,
                'file_size': blob.size,
                'content_type': 'application/pdf',
                'uploaded_at': datetime.now().isoformat(),
                'created_by': 'preauth_form',
                'is_active': True
            })
            
            logging.info(f"File uploaded to Firebase Storage: {firebase_path}")
            return file_metadata
            
        except Exception as e:
            logging.error(f"Error uploading file to Firebase Storage: {str(e)}")
            return None
    return None

def get_db():
    """Get Firestore database client"""
    global db, firebase_client
    if db is None:
        firebase_client = FirebaseClient()
        db = firebase_client.get_firestore_client()
    return db

def get_files_for_claim(claim_id: str) -> list:
    """Get all files for a specific claim from Firebase Storage"""
    try:
        db = get_db()
        files_query = db.collection('Preauth_Files').where('claim_id', '==', claim_id).where('is_active', '==', True)
        files_docs = files_query.get()
        
        files = []
        for doc in files_docs:
            file_data = doc.to_dict()
            file_data['file_id'] = doc.id
            files.append(file_data)
        
        return files
    except Exception as e:
        logging.error(f"Error retrieving files for claim {claim_id}: {str(e)}")
        return []

def get_file_download_url(firebase_path: str) -> str:
    """Get download URL for a file in Firebase Storage"""
    try:
        firebase_client = FirebaseClient()
        bucket = firebase_client.get_storage_bucket()
        blob = bucket.blob(firebase_path)
        
        # Generate a signed URL valid for 1 hour
        from datetime import timedelta
        url = blob.generate_signed_url(expiration=datetime.now() + timedelta(hours=1))
        return url
    except Exception as e:
        logging.error(f"Error generating download URL for {firebase_path}: {str(e)}")
        return None

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

def get_specialities():
    """Get all active specialities"""
    try:
        db = get_db()
        specialities_ref = db.collection('specialities').where('is_active', '==', True)
        specialities_docs = specialities_ref.get()
        
        specialities = []
        for doc in specialities_docs:
            speciality_data = doc.to_dict()
            speciality_data['id'] = doc.id
            specialities.append(speciality_data)
        
        return specialities
    except Exception as e:
        logging.error(f"Error fetching specialities: {str(e)}")
        return []

def get_doctors_by_hospital_and_speciality(hospital_id: str, speciality_id: str = None):
    """Get doctors filtered by hospital and speciality"""
    try:
        db = get_db()
        doctors_query = db.collection('doctors').where('hospital_id', '==', hospital_id).where('is_active', '==', True)
        
        if speciality_id:
            doctors_query = doctors_query.where('speciality_id', '==', speciality_id)
        
        doctors_docs = doctors_query.get()
        
        doctors = []
        for doc in doctors_docs:
            doctor_data = doc.to_dict()
            doctor_data['id'] = doc.id
            doctors.append(doctor_data)
        
        return doctors
    except Exception as e:
        logging.error(f"Error fetching doctors: {str(e)}")
        return []

# Routes
@preauth_form_bp.route('/preauth-form/<hospital_id>')
def show_preauth_form(hospital_id: str):
    """Show pre-authorisation form for a hospital"""
    try:
        hospital_info = get_hospital_info(hospital_id)
        
        # Ensure rohini_id is mapped to hospital_id
        if hospital_info:
            hospital_info['rohini_id'] = hospital_id
            
        specialities = get_specialities()
        doctors = get_doctors_by_hospital_and_speciality(hospital_id)
        
        return render_template_string(
            PREAUTH_FORM_TEMPLATE,
            hospital_info=hospital_info,
            specialities=specialities,
            doctors=doctors,
            hospital_id=hospital_id
        )
    except Exception as e:
        logging.error(f"Error rendering preauth form: {str(e)}")
        return f"Error loading form: {str(e)}", 500

@preauth_form_bp.route('/preauth-form/<claim_id>/view')
def show_preauth_form_for_claim(claim_id: str):
    """Show pre-authorisation form prefilled for a specific claim"""
    try:
        db = get_db()
        claim_ref = db.collection('claims').document(claim_id)
        claim_doc = claim_ref.get()
        
        if not claim_doc.exists:
            return "Claim not found", 404
        
        claim_data = claim_doc.to_dict()
        hospital_id = claim_data.get('hospital_id', 'HOSP_001')
        hospital_name = claim_data.get('hospital_name', 'Unknown Hospital')

        # Create hospital info from claim data instead of fetching from hospitals collection
        hospital_info = {
            'id': hospital_id,
            'name': hospital_name,
            'rohini_id': hospital_id,  # Map Rohini ID with Hospital ID
            'tpa_name': claim_data.get('payer_name', ''),
            'address': claim_data.get('hospital_address', ''),
            'email': claim_data.get('hospital_email', ''),
            'phone': claim_data.get('hospital_phone', ''),
            'fax': claim_data.get('hospital_fax', '')
        }
        
        specialities = get_specialities()
        doctors = get_doctors_by_hospital_and_speciality(hospital_id)
        
        return render_template_string(
            PREAUTH_FORM_TEMPLATE,
            hospital_info=hospital_info,
            specialities=specialities,
            doctors=doctors,
            hospital_id=hospital_id,
            claim=claim_data
        )
    except Exception as e:
        logging.error(f"Error rendering preauth form for claim {claim_id}: {str(e)}")
        return f"Error loading form: {str(e)}", 500

@preauth_form_bp.route('/api/files/<claim_id>')
def get_claim_files(claim_id: str):
    """Get all files for a specific claim"""
    try:
        files = get_files_for_claim(claim_id)
        return jsonify({
            'success': True,
            'claim_id': claim_id,
            'files': files,
            'count': len(files)
        })
    except Exception as e:
        logging.error(f"Error getting files for claim {claim_id}: {str(e)}")
        return jsonify({'error': 'Failed to retrieve files'}), 500

@preauth_form_bp.route('/api/files/<claim_id>/download/<file_id>')
def download_claim_file(claim_id: str, file_id: str):
    """Download a specific file for a claim"""
    try:
        db = get_db()
        file_doc = db.collection('Preauth_Files').document(file_id).get()
        
        if not file_doc.exists:
            return jsonify({'error': 'File not found'}), 404
        
        file_data = file_doc.to_dict()
        
        # Verify the file belongs to the claim
        if file_data.get('claim_id') != claim_id:
            return jsonify({'error': 'File does not belong to this claim'}), 403
        
        # Generate download URL
        download_url = get_file_download_url(file_data['firebase_path'])
        
        if download_url:
            return jsonify({
                'success': True,
                'download_url': download_url,
                'filename': file_data['original_filename'],
                'file_size': file_data['file_size'],
                'content_type': file_data['content_type']
            })
        else:
            return jsonify({'error': 'Failed to generate download URL'}), 500
            
    except Exception as e:
        logging.error(f"Error downloading file {file_id} for claim {claim_id}: {str(e)}")
        return jsonify({'error': 'Failed to download file'}), 500

@preauth_form_bp.route('/api/files/<claim_id>/delete/<file_id>', methods=['DELETE'])
def delete_claim_file(claim_id: str, file_id: str):
    """Delete a specific file for a claim"""
    try:
        db = get_db()
        file_doc_ref = db.collection('Preauth_Files').document(file_id)
        file_doc = file_doc_ref.get()
        
        if not file_doc.exists:
            return jsonify({'error': 'File not found'}), 404
        
        file_data = file_doc.to_dict()
        
        # Verify the file belongs to the claim
        if file_data.get('claim_id') != claim_id:
            return jsonify({'error': 'File does not belong to this claim'}), 403
        
        # Delete from Firebase Storage
        firebase_client = FirebaseClient()
        bucket = firebase_client.get_storage_bucket()
        blob = bucket.blob(file_data['firebase_path'])
        blob.delete()
        
        # Mark as inactive in Firestore (soft delete)
        file_doc_ref.update({
            'is_active': False,
            'deleted_at': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'message': 'File deleted successfully'
        })
        
    except Exception as e:
        logging.error(f"Error deleting file {file_id} for claim {claim_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete file'}), 500

@preauth_form_bp.route('/submit-preauth', methods=['POST'])
def submit_preauth_form():
    """Handle pre-authorisation form submission"""
    try:
        hospital_id = request.form.get('hospital_id', 'HOSP_001')
        user_id = request.form.get('user_id', 'form_user')
        user_name = request.form.get('user_name', 'Form User')
        action_type = request.form.get('action_type', 'preauth_registered')  # Default to submit
        
        # Determine status based on action type
        if action_type == 'draft':
            status = 'draft'
        elif action_type == 'cancel':
            status = 'archived'
        else:
            status = 'preauth_registered'
        
        # Validate mandatory fields only for submit action
        if action_type == 'preauth_registered':
            mandatory_fields = [
                'patient_name', 'mobile_number', 'uhid', 'payer_type', 'payer_name', 
                'claim_type', 'admission_type', 'gender', 'nature_of_illness', 
                'admission_datetime', 'ip_number', 'estimated_treatment_cost'
            ]
            missing_fields = []
            
            for field in mandatory_fields:
                if not request.form.get(field):
                    missing_fields.append(field)
            
            if missing_fields:
                error_message = f'Missing mandatory fields: {", ".join(missing_fields)}'
                
                # Return JSON response for AJAX calls
                if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': error_message,
                        'missing_fields': missing_fields
                    }), 400
                
                flash(error_message, 'error')
                return redirect(url_for('preauth_form.show_preauth_form', hospital_id=hospital_id))
        
        # Get hospital information
        hospital_info = get_hospital_info(hospital_id)
        
        # Generate Claim ID
        claim_id = generate_claim_id(hospital_id)
        
        # Prepare claim data
        claim_data = {
            'claim_id': claim_id,
            'hospital_id': hospital_id,
            'hospital_name': hospital_info.get('name', 'Unknown Hospital'),
            'patient_name': request.form.get('patient_name'),
            'mobile_number': request.form.get('mobile_number'),
            'uhid': request.form.get('uhid'),
            'claim_type': request.form.get('claim_type'),
            'admission_type': request.form.get('admission_type'),
            'status': status,
            'created_by': user_id,
            'updated_by': user_id,
            'created_by_name': user_name,
            'updated_by_name': user_name,
        }
        
        # Add optional fields if provided
        optional_fields = [
            'payer_type', 'payer_name', 'insurer_name', 'rohini_id', 'payer_email', 
            'payer_phone', 'payer_fax', 'hospital_address', 'email_id', 'abha_id', 
            'gender', 'date_of_birth', 'alternative_contact', 'customer_id', 
            'policy_number', 'employee_id', 'occupation', 'speciality_id', 
            'treating_doctor_id', 'treating_doctor_name', 'treating_doctor_contact', 
            'treating_doctor_qualification', 'treating_doctor_registration_number', 
            'nature_of_illness', 'relevant_clinical_findings', 'duration_of_present_ailment',
            'date_of_first_consultation', 'past_history_present_ailment',
            'provisional_diagnosis', 'icd_10_code', 'proposed_line_of_treatment',
            'ward_type', 'expected_length_of_stay', 'estimated_treatment_cost',
            'admission_datetime', 'ip_number', 'show_in_claims'
        ]
        
        for field in optional_fields:
            value = request.form.get(field)
            if value:
                claim_data[field] = value
        
        # Handle address fields
        address_fields = ['address_street', 'address_city', 'address_state', 'address_pincode']
        address = {}
        for field in address_fields:
            value = request.form.get(field)
            if value:
                field_name = field.replace('address_', '')
                address[field_name] = value
        
        if address:
            claim_data['address'] = address
        
        # Handle boolean fields
        boolean_fields = ['additional_policy', 'family_physician', 'rta_file', 'maternity']
        for field in boolean_fields:
            value = request.form.get(field)
            if value:
                claim_data[field] = value.lower() in ['true', '1', 'yes', 'on']
        
        # Calculate age if date of birth is provided
        if claim_data.get('date_of_birth'):
            age_details = calculate_age_detailed(claim_data['date_of_birth'])
            claim_data['age_years'] = age_details['years']
            claim_data['age_months'] = age_details['months']
            claim_data['age_days'] = age_details['days']
        
        # Handle file uploads
        uploaded_files = {}
        file_types = ['medical_reports', 'prescription', 'lab_reports', 'discharge_summary', 'other_documents']
        
        for file_type in file_types:
            file_key = f'{file_type}_file'
            if file_key in request.files:
                file = request.files[file_key]
                if file and file.filename:
                    # Check file size
                    file.seek(0, 2)  # Seek to end
                    file_size = file.tell()
                    file.seek(0)  # Reset to beginning
                    
                    if file_size > MAX_FILE_SIZE:
                        error_message = f'File {file.filename} is too large. Maximum size is 16MB.'
                        
                        # Return JSON response for AJAX calls
                        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return jsonify({
                                'success': False,
                                'message': error_message
                            }), 400
                        
                        flash(error_message, 'error')
                        return redirect(url_for('preauth_form.show_preauth_form', hospital_id=hospital_id))
                    
                    # Save file to Firebase Storage
                    file_metadata = save_uploaded_file_to_firebase(file, claim_id, file_type)
                    if file_metadata:
                        uploaded_files[file_type] = file_metadata
                    else:
                        error_message = f'Failed to upload {file.filename}. Please try again.'
                        
                        # Return JSON response for AJAX calls
                        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return jsonify({
                                'success': False,
                                'message': error_message
                            }), 500
                        
                        flash(error_message, 'error')
                        return redirect(url_for('preauth_form.show_preauth_form', hospital_id=hospital_id))
        
        # Add uploaded files to claim data
        if uploaded_files:
            claim_data['uploaded_files'] = uploaded_files
        
        # Create claim object
        claim = Claim(**claim_data)
        
        # Validate claim
        validation_errors = claim.validate()
        if validation_errors:
            error_message = f'Validation errors: {", ".join(validation_errors)}'
            
            # Return JSON response for AJAX calls
            if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': error_message,
                    'validation_errors': validation_errors
                }), 400
            
            flash(error_message, 'error')
            return redirect(url_for('preauth_form.show_preauth_form', hospital_id=hospital_id))
        
        # Save to Firestore
        db = get_db()
        claim_ref = db.collection('claims').document(claim_id)
        claim_ref.set(claim.to_dict())
        
        # Update file metadata in Preauthform_files collection
        if uploaded_files:
            for file_type, file_metadata in uploaded_files.items():
                file_doc_ref = db.collection(FIREBASE_STORAGE_COLLECTION).document()
                file_doc_ref.set({
                    'claim_id': claim_id,
                    'file_type': file_type,
                    'original_filename': file_metadata['filename'],
                    'firebase_path': file_metadata['firebase_path'],
                    'public_url': file_metadata['public_url'],
                    'file_size': file_metadata['file_size'],
                    'content_type': 'application/pdf',
                    'uploaded_at': datetime.now().isoformat(),
                    'created_by': 'preauth_form',
                    'is_active': True
                })
        
        # Send notification if status is preauth_registered
        if status == 'preauth_registered':
            try:
                import requests
                notification_url = f"http://localhost:5000/api/notifications/send-preauth-notification/{claim_id}"
                requests.post(notification_url, timeout=5)
                logging.info(f"Notification sent for claim {claim_id}")
            except Exception as e:
                logging.error(f"Failed to send notification for claim {claim_id}: {str(e)}")
                # Don't fail the form submission if notification fails
        
        # Determine success message based on action
        if status == 'draft':
            success_message = f'Pre-authorisation form saved as draft! Claim ID: {claim_id}'
        elif status == 'archived':
            success_message = f'Pre-authorisation form cancelled and archived! Claim ID: {claim_id}'
        else:
            success_message = f'Pre-authorisation form submitted successfully! Claim ID: {claim_id}'
        
        # Return JSON response for AJAX calls
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': success_message,
                'claim_id': claim_id,
                'status': status
            })
        
        flash(success_message, 'success')
        return redirect(url_for('preauth_form.show_preauth_form', hospital_id=hospital_id))
        
    except Exception as e:
        logging.error(f"Error submitting preauth form: {str(e)}")
        
        # Return JSON response for AJAX calls
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': 'An error occurred while submitting the form. Please try again.',
                'error': str(e)
            }), 500
        
        flash('An error occurred while submitting the form. Please try again.', 'error')
        return redirect(url_for('preauth_form.show_preauth_form', hospital_id=hospital_id))

# HTML Template for the Pre-Authorisation Form
PREAUTH_FORM_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pre-Authorisation Form</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Josefin+Sans:ital,wght@0,100..700;1,100..700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Josefin Sans', sans-serif;
            color: #4A5568; /* gray-700 */
        }
        .form-section-title {
            font-weight: 600;
            font-size: 1.25rem; /* text-xl */
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #E2E8F0; /* gray-300 */
            color: #2D3748; /* gray-800 */
        }
        .form-container {
            max-width: 900px;
            margin: 2rem auto;
            padding: 2rem;
            background-color: #ffffff;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #E2E8F0; /* gray-300 */
        }
        .char-box-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.25rem; /* 4px */
        }
        .char-box {
            width: 1.75rem; /* 28px */
            height: 1.75rem; /* 28px */
            text-align: center;
            border: 1px solid #CBD5E0; /* gray-400 */
            border-radius: 0.375rem; /* rounded-md */
            font-size: 1rem; /* text-base */
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .char-box-input {
            width: 100%;
            height: 100%;
            border: none;
            background: transparent;
            text-align: center;
            font-size: 1rem;
            font-weight: bold;
            color: #2d3748;
            outline: none;
        }
        .char-box.filled {
            background-color: #f7fafc;
            border-color: #4a5568;
        }
        label {
            font-weight: 500;
        }
        .checkbox-label {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 400;
        }
        .grid-cols-custom {
             grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        }
        .printable-checkbox {
            display: inline-block;
            width: 1rem;
            height: 1rem;
            border: 1px solid #4A5568;
            border-radius: 0.25rem;
            vertical-align: middle;
        }
        .separator {
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            font-weight: bold;
            color: #718096;
            height: 1.75rem;
        }
        .file-input {
            border: 2px dashed #cbd5e0;
            background: #f7fafc;
            transition: all 0.3s ease;
        }
        .file-input:hover {
            border-color: #4299e1;
            background: #ebf8ff;
        }
        .file-item {
            background: #f0f9ff;
            border: 1px solid #0ea5e9;
            border-radius: 0.5rem;
            padding: 0.75rem;
            margin: 0.5rem 0;
        }
        .signature-field {
            width: 100%;
            height: 80px;
            border: 2px dashed #CBD5E0;
            border-radius: 0.375rem;
            background: #f7fafc;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #718096;
            font-style: italic;
        }
        .dropdown-field {
            width: 100%;
            padding: 0.5rem;
            border: 1px solid #CBD5E0;
            border-radius: 0.375rem;
            background: white;
        }

        @media print {
            body {
                background-color: #ffffff;
                color: #000000;
            }
            .form-container {
                box-shadow: none;
                border: none;
                margin: 0;
                padding: 0;
                max-width: 100%;
            }
            .print-button-container {
                display: none;
            }
            .form-section-title {
                color: #000000;
            }
            section {
                page-break-inside: avoid;
            }
            .char-box {
                border-color: #718096;
            }
        }
    </style>
</head>
<body class="bg-gray-100">

    <div class="form-container">
        <div class="print-button-container text-right mb-4">
            <button onclick="window.print()" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors">
                Print Form
            </button>
        </div>

        <header class="text-center mb-8">
            <h1 class="text-3xl font-bold text-gray-800">Pre-Authorisation Form</h1>
            <p class="text-md mt-1">Request for Cashless Hospitalisation for Medical Insurance Policy</p>
            <p class="text-sm mt-2 text-gray-600">Hospital: {{ hospital_info.name }}</p>
        </header>

        <form method="POST" action="{{ url_for('preauth_form.submit_preauth_form') }}" enctype="multipart/form-data" class="space-y-8">
            <input type="hidden" name="hospital_id" value="{{ hospital_id }}">
            <input type="hidden" name="user_id" value="form_user">
            <input type="hidden" name="user_name" value="Form User">
            <input type="hidden" name="action_type" id="action_type" value="">

            <!-- Section: TPA Details -->
            <section class="mb-8">
                <h2 class="form-section-title">Details of the Third Party Administrator</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-6">
                    <div>
                        <label>a) Name of TPA/Insurance Company: <span class="text-red-500">*</span></label>
                        <div id="payer_name_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="payer_name" id="payer_name_input">
                    </div>
                    <div>
                        <label>d) Name of Hospital:</label>
                        <div id="hospital_name_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="hospital_name" id="hospital_name_input">
                    </div>
                    <div>
                        <label>b) Toll Free Phone No.:</label>
                        <div id="payer_phone_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="payer_phone" id="payer_phone_input">
                    </div>
                    <div>
                        <label>i) Address:</label>
                        <div id="hospital_address_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="hospital_address" id="hospital_address_input">
                    </div>
                    <div>
                        <label>c) Toll Free FAX:</label>
                        <div id="payer_fax_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="payer_fax" id="payer_fax_input">
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label>ii) Rohini ID:</label>
                            <div id="rohini_id_boxes" class="char-box-container mt-1"></div>
                            <input type="hidden" name="rohini_id" id="rohini_id_input">
                        </div>
                        <div>
                            <label>iii) Email ID:</label>
                            <div id="payer_email_boxes" class="char-box-container mt-1"></div>
                            <input type="hidden" name="payer_email" id="payer_email_input">
                        </div>
                    </div>
                </div>
            </section>

            <!-- Section: Patient Details -->
            <section class="mb-8">
                <h2 class="form-section-title">To be filled by the Insured/Patient</h2>
                <div class="grid grid-cols-1 md:grid-cols-custom gap-x-6 gap-y-6">
                    <!-- Patient Name -->
                    <div class="md:col-span-2">
                        <label>a) Name of the Patient: <span class="text-red-500">*</span></label>
                        <div id="patient_name_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="patient_name" id="patient_name_input">
                        <p class="text-xs text-gray-500 mt-1">(First Name, Middle Name, Last Name)</p>
                    </div>

                    <!-- Gender -->
                    <div>
                        <label>b) Gender: <span class="text-red-500">*</span></label>
                        <div class="flex gap-4 mt-2 pt-2">
                            <label class="checkbox-label">
                                <input type="radio" name="gender" value="Male" {{ 'checked' if claim_data and claim_data.gender == 'Male' else '' }}>
                                Male
                            </label>
                            <label class="checkbox-label">
                                <input type="radio" name="gender" value="Female" {{ 'checked' if claim_data and claim_data.gender == 'Female' else '' }}>
                                Female
                            </label>
                            <label class="checkbox-label">
                                <input type="radio" name="gender" value="Other" {{ 'checked' if claim_data and claim_data.gender == 'Other' else '' }}>
                                Other
                            </label>
                        </div>
                    </div>
                    
                    <!-- Age & DOB -->
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label>c) Age:</label>
                            <div id="age_years_boxes" class="char-box-container mt-1"></div>
                            <input type="hidden" name="age_years" id="age_years_input">
                        </div>
                        <div>
                            <label>d) Date of Birth:</label>
                            <div id="date_of_birth_boxes" class="char-box-container mt-1"></div>
                            <input type="hidden" name="date_of_birth" id="date_of_birth_input">
                        </div>
                    </div>

                    <!-- Contact Numbers -->
                    <div>
                        <label>e) Contact Number: <span class="text-red-500">*</span></label>
                        <div id="mobile_number_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="mobile_number" id="mobile_number_input">
                    </div>
                    <div>
                        <label>f) Contact Number of Attending Relative:</label>
                        <div id="alternative_contact_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="alternative_contact" id="alternative_contact_input">
                    </div>

                    <!-- Payer Type -->
                    <div>
                        <label>Payer Type: <span class="text-red-500">*</span></label>
                        <select name="payer_type" class="dropdown-field mt-1" required>
                            <option value="">Select Payer Type</option>
                            <option value="TPA" {{ 'selected' if claim_data and claim_data.payer_type == 'TPA' else '' }}>TPA</option>
                            <option value="Insurance Company" {{ 'selected' if claim_data and claim_data.payer_type == 'Insurance Company' else '' }}>Insurance Company</option>
                            <option value="Corporate" {{ 'selected' if claim_data and claim_data.payer_type == 'Corporate' else '' }}>Corporate</option>
                            <option value="Social scheme" {{ 'selected' if claim_data and claim_data.payer_type == 'Social scheme' else '' }}>Social scheme</option>
                            <option value="Others" {{ 'selected' if claim_data and claim_data.payer_type == 'Others' else '' }}>Others</option>
                        </select>
                    </div>

                    <!-- IDs -->
                    <div>
                        <label>g) Insured Card ID Number: <span class="text-red-500">*</span></label>
                        <div id="uhid_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="uhid" id="uhid_input">
                    </div>
                    <div>
                        <label>h) Policy Number/Name of Corporate: <span class="text-red-500">*</span></label>
                        <div id="policy_number_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="policy_number" id="policy_number_input">
                    </div>
                    <div>
                        <label>i) Employee ID:</label>
                        <div id="employee_id_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="employee_id" id="employee_id_input">
                    </div>

                    <!-- Other Insurance -->
                    <div class="md:col-span-2">
                        <label>j) Currently do you have any other Mediclaim/Health Insurance:</label>
                        <div class="flex gap-4 mt-2">
                            <label class="checkbox-label">
                                <input type="radio" name="additional_policy" value="true" {{ 'checked' if claim_data and claim_data.additional_policy else '' }}>
                                Yes
                            </label>
                            <label class="checkbox-label">
                                <input type="radio" name="additional_policy" value="false" {{ 'checked' if claim_data and not claim_data.additional_policy else '' }}>
                                No
                            </label>
                        </div>
                    </div>

                    <!-- Family Physician -->
                    <div class="md:col-span-2">
                        <label>k) Do you have a family physician:</label>
                        <div class="flex gap-4 mt-2">
                            <label class="checkbox-label">
                                <input type="radio" name="family_physician" value="true" {{ 'checked' if claim_data and claim_data.family_physician else '' }}>
                                Yes
                            </label>
                            <label class="checkbox-label">
                                <input type="radio" name="family_physician" value="false" {{ 'checked' if claim_data and not claim_data.family_physician else '' }}>
                                No
                            </label>
                        </div>
                    </div>
                    
                    <div class="md:col-span-2">
                        <label>n) Current Address of the Insured Patient:</label>
                        <textarea name="address_street" rows="2" class="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">{{ claim_data.address.street if claim_data and claim_data.address else '' }}</textarea>
                    </div>
                    <div>
                        <label>o) Occupation of Insured Person:</label>
                        <input type="text" name="occupation" value="{{ claim_data.occupation if claim_data else '' }}" class="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                </div>
            </section>

            <!-- Section: To be filled by the Treating Doctor/Hospital -->
            <section class="mb-8">
                <h2 class="form-section-title">To be filled by the Treating Doctor/Hospital</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-6">
                    <!-- Speciality -->
                    <div>
                        <label>Speciality:</label>
                        <select name="speciality_id" id="speciality_id" class="dropdown-field mt-1">
                            <option value="">Select Speciality</option>
                            {% for speciality in specialities %}
                            <option value="{{ speciality.id }}" {{ 'selected' if claim_data and claim_data.speciality_id == speciality.id else '' }}>{{ speciality.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <!-- Treating Doctor -->
                    <div>
                        <label>Treating Doctor:</label>
                        <select name="treating_doctor_id" id="treating_doctor_id" class="dropdown-field mt-1">
                            <option value="">Select Doctor</option>
                        </select>
                    </div>
                    
                    <div>
                        <label>a) Name of the treating doctor:</label>
                        <div id="treating_doctor_name_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="treating_doctor_name" id="treating_doctor_name_input">
                    </div>
                    <div>
                        <label>b) Contact Number:</label>
                        <div id="treating_doctor_contact_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="treating_doctor_contact" id="treating_doctor_contact_input">
                    </div>
                    <div class="md:col-span-2">
                        <label>c) Nature of Illness/Disease with presenting complaints: <span class="text-red-500">*</span></label>
                        <div id="nature_of_illness_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="nature_of_illness" id="nature_of_illness_input">
                    </div>
                    <div class="md:col-span-2">
                        <label>d) Relevant clinical findings:</label>
                        <div id="relevant_clinical_findings_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="relevant_clinical_findings" id="relevant_clinical_findings_input">
                    </div>
                    <div>
                        <label>e) Duration of the present ailment:</label>
                        <div id="duration_of_present_ailment_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="duration_of_present_ailment" id="duration_of_present_ailment_input">
                        <span class="text-sm text-gray-500">days</span>
                    </div>
                    <div>
                        <label>i) Date of first consultation:</label>
                        <div id="date_of_first_consultation_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="date_of_first_consultation" id="date_of_first_consultation_input">
                    </div>
                    <div class="md:col-span-2">
                        <label>ii) Past history of present ailment if any:</label>
                        <div id="past_history_present_ailment_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="past_history_present_ailment" id="past_history_present_ailment_input">
                    </div>
                    <div>
                        <label>f) Provisional diagnosis:</label>
                        <div id="provisional_diagnosis_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="provisional_diagnosis" id="provisional_diagnosis_input">
                    </div>
                    <div>
                        <label>g) ICD 10 Code:</label>
                        <div id="icd_10_code_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="icd_10_code" id="icd_10_code_input">
                    </div>
                </div>
            </section>
            
            <!-- Section: Patient Admitted Details -->
            <section>
                <h2 class="form-section-title">Details of the patient admitted</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-6">
                    <div>
                        <label>a) Date of Admission: <span class="text-red-500">*</span></label>
                        <div id="admission_datetime_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="admission_datetime" id="admission_datetime_input">
                    </div>
                    <div>
                        <label>b) IP Number: <span class="text-red-500">*</span></label>
                        <div id="ip_number_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="ip_number" id="ip_number_input">
                    </div>
                    <div>
                        <label>c) Is this an emergency/a planned hospitalization event?: <span class="text-red-500">*</span></label>
                        <div class="flex gap-4 mt-2">
                            <label class="checkbox-label">
                                <input type="radio" name="admission_type" value="Emergency" {{ 'checked' if claim_data and claim_data.admission_type == 'Emergency' else '' }}>
                                Emergency
                            </label>
                            <label class="checkbox-label">
                                <input type="radio" name="admission_type" value="Planned" {{ 'checked' if claim_data and claim_data.admission_type == 'Planned' else '' }}>
                                Planned
                            </label>
                        </div>
                    </div>
                    <div>
                        <label>d) Expected no. of days stay in hospital:</label>
                        <div id="expected_length_of_stay_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="expected_length_of_stay" id="expected_length_of_stay_input">
                        <span class="text-sm text-gray-500">days</span>
                    </div>
                    <div>
                        <label>e) Room Type:</label>
                        <div id="ward_type_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="ward_type" id="ward_type_input">
                    </div>
                    
                    <div class="md:col-span-2">
                        <label class="font-semibold text-lg">n) Sum Total expected cost of hospitalization: <span class="text-red-500">*</span></label>
                        <div id="estimated_treatment_cost_boxes" class="char-box-container mt-1"></div>
                        <input type="hidden" name="estimated_treatment_cost" id="estimated_treatment_cost_input">
                        <span class="text-sm text-gray-500">Rs.</span>
                    </div>
                </div>
            </section>

            <!-- Section: Signature Fields -->
            <section class="mb-8">
                <h2 class="form-section-title">Signatures</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-6">
                    <div>
                        <h3 class="font-semibold text-lg mb-4">Doctor's Details & Signature</h3>
                        <div class="space-y-6">
                            <div>
                                <label>a) Name of the treating doctor:</label>
                                <div id="doctor_name_boxes" class="char-box-container mt-1"></div>
                                <input type="hidden" name="doctor_name" id="doctor_name_input">
                            </div>
                            <div>
                                <label>b) Qualification:</label>
                                <div id="doctor_qualification_boxes" class="char-box-container mt-1"></div>
                                <input type="hidden" name="doctor_qualification" id="doctor_qualification_input">
                            </div>
                            <div>
                                <label>c) Registration No. with State Code:</label>
                                <div id="doctor_registration_boxes" class="char-box-container mt-1"></div>
                                <input type="hidden" name="doctor_registration" id="doctor_registration_input">
                            </div>
                            <div class="pt-4">
                                <label>Doctor's Signature:</label>
                                <div class="signature-field mt-1">Signature Area</div>
                            </div>
                        </div>
                    </div>
                    <div>
                        <h3 class="font-semibold text-lg mb-4">Patient/Insured Signature</h3>
                        <div class="space-y-6">
                            <div>
                                <label>Patient's/Insured's Name:</label>
                                <div id="patient_signature_name_boxes" class="char-box-container mt-1"></div>
                                <input type="hidden" name="patient_signature_name" id="patient_signature_name_input">
                            </div>
                            <div>
                                <label>Patient's/Insured's Signature:</label>
                                <div class="signature-field mt-1">Signature Area</div>
                            </div>
                            <div class="grid grid-cols-2 gap-4 pt-4">
                                <div>
                                    <label>Date:</label>
                                    <div id="signature_date_boxes" class="char-box-container mt-1"></div>
                                    <input type="hidden" name="signature_date" id="signature_date_input">
                                </div>
                                <div>
                                    <label>Time:</label>
                                    <div id="signature_time_boxes" class="char-box-container mt-1"></div>
                                    <input type="hidden" name="signature_time" id="signature_time_input">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- File Upload Section -->
            <section class="mb-8">
                <h2 class="form-section-title">📁 File Upload Section</h2>
                <div class="bg-blue-50 p-4 rounded-lg border border-blue-200">
                    <p class="text-sm text-blue-800 mb-4">
                        <strong>Note:</strong> Only PDF files are allowed. Maximum file size: 16MB per file.
                    </p>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Medical Reports</label>
                            <input type="file" name="medical_reports_file" accept=".pdf" class="file-input w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Prescription</label>
                            <input type="file" name="prescription_file" accept=".pdf" class="file-input w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Lab Reports</label>
                            <input type="file" name="lab_reports_file" accept=".pdf" class="file-input w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Discharge Summary</label>
                            <input type="file" name="discharge_summary_file" accept=".pdf" class="file-input w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                        
                        <div class="md:col-span-2">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Other Documents</label>
                            <input type="file" name="other_documents_file" accept=".pdf" class="file-input w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                    </div>
                </div>
            </section>

            <!-- Action Buttons -->
            <div class="mt-8 text-center">
                <div class="flex gap-4 justify-center">
                    <button type="button" onclick="submitForm('draft')" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition-colors text-lg">
                        Save as Draft
                    </button>
                    <button type="button" onclick="submitForm('preauth_registered')" class="bg-green-500 hover:bg-green-700 text-white font-bold py-3 px-8 rounded-lg transition-colors text-lg">
                        Submit Pre-Authorisation Form
                    </button>
                    <button type="button" onclick="submitForm('cancel')" class="bg-red-500 hover:bg-red-700 text-white font-bold py-3 px-8 rounded-lg transition-colors text-lg">
                        Cancel Pre-Authorisation
                    </button>
                </div>
            </div>
        </form>
    </div>

    <script>
        // Character box functions
        function createCharBoxes(containerId, maxLength = 50, fieldName = '') {
            const container = document.getElementById(containerId);
            container.innerHTML = '';
            
            for (let i = 0; i < maxLength; i++) {
                const charBox = document.createElement('div');
                charBox.className = 'char-box';
                charBox.setAttribute('data-index', i);
                charBox.setAttribute('data-field', fieldName);
                
                const input = document.createElement('input');
                input.type = 'text';
                input.className = 'char-box-input';
                input.maxLength = 1;
                input.addEventListener('input', function(e) {
                    updateHiddenField(fieldName);
                    // Move to next box
                    if (e.target.value && i < maxLength - 1) {
                        const nextBox = container.querySelector(`[data-index="${i + 1}"] input`);
                        if (nextBox) nextBox.focus();
                    }
                });
                input.addEventListener('keydown', function(e) {
                    // Handle backspace
                    if (e.key === 'Backspace' && !e.target.value && i > 0) {
                        const prevBox = container.querySelector(`[data-index="${i - 1}"] input`);
                        if (prevBox) prevBox.focus();
                    }
                });
                
                charBox.appendChild(input);
                container.appendChild(charBox);
            }
        }

        function updateHiddenField(fieldName) {
            const container = document.getElementById(fieldName + '_boxes');
            const hiddenInput = document.getElementById(fieldName + '_input');
            if (container && hiddenInput) {
                const inputs = container.querySelectorAll('.char-box-input');
                let value = '';
                inputs.forEach(input => {
                    if (input.value) {
                        value += input.value;
                    }
                });
                hiddenInput.value = value;
            }
        }

        function populateCharBoxes(containerId, value) {
            const container = document.getElementById(containerId);
            if (container && value) {
                const inputs = container.querySelectorAll('.char-box-input');
                const chars = value.toString().split('');
                inputs.forEach((input, index) => {
                    if (chars[index]) {
                        input.value = chars[index];
                        input.parentElement.classList.add('filled');
                    }
                });
            }
        }

        // Doctor loading functions
        function loadDoctors() {
            const specialityId = document.getElementById('speciality_id').value;
            const doctorSelect = document.getElementById('treating_doctor_id');
            
            // Clear existing options
            doctorSelect.innerHTML = '<option value="">Select Doctor</option>';
            
            if (specialityId) {
                // Filter doctors by speciality
                const doctors = {{ doctors | tojson }};
                const filteredDoctors = doctors.filter(doctor => doctor.speciality_id === specialityId);
                
                filteredDoctors.forEach(doctor => {
                    const option = document.createElement('option');
                    option.value = doctor.id;
                    option.textContent = doctor.name;
                    doctorSelect.appendChild(option);
                });
            }
        }

        function loadDoctorDetails() {
            const doctorId = document.getElementById('treating_doctor_id').value;
            if (doctorId) {
                const doctors = {{ doctors | tojson }};
                const doctor = doctors.find(d => d.id === doctorId);
                if (doctor) {
                    // Populate doctor details
                    populateCharBoxes('treating_doctor_name_boxes', doctor.name || '');
                    populateCharBoxes('treating_doctor_contact_boxes', doctor.contact_number || '');
                    updateHiddenField('treating_doctor_name');
                    updateHiddenField('treating_doctor_contact');
                }
            }
        }

        // Form submission function
        function submitForm(actionType) {
            // Set the action type in hidden field
            document.getElementById('action_type').value = actionType;
            
            // Validate form based on action type
            if (actionType === 'preauth_registered') {
                // For submit, validate all mandatory fields
                const mandatoryFields = [
                    'patient_name', 'mobile_number', 'uhid', 'payer_type', 'payer_name', 
                    'claim_type', 'admission_type', 'gender', 'nature_of_illness', 
                    'admission_datetime', 'ip_number', 'estimated_treatment_cost'
                ];
                
                let missingFields = [];
                for (let field of mandatoryFields) {
                    const element = document.querySelector(`[name="${field}"]`);
                    if (!element || !element.value.trim()) {
                        missingFields.push(field);
                    }
                }
                
                if (missingFields.length > 0) {
                    alert(`Please fill in all mandatory fields: ${missingFields.join(', ')}`);
                    return;
                }
            }
            
            // Show loading state
            const submitButton = event.target;
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Processing...';
            submitButton.disabled = true;
            
            // Create FormData for AJAX submission
            const form = document.querySelector('form');
            const formData = new FormData(form);
            
            // Submit via AJAX
            fetch('/submit-preauth', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success popup
                    alert(data.message);
                    
                    // If it's a submit (not draft), redirect to view the claim
                    if (actionType === 'preauth_registered' && data.claim_id) {
                        window.location.href = `/preauth-form/${data.claim_id}/view`;
                    }
                } else {
                    alert(data.message || 'An error occurred while submitting the form.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while submitting the form. Please try again.');
            })
            .finally(() => {
                // Reset button state
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            });
        }

        // Initialize form when page loads
        document.addEventListener('DOMContentLoaded', function() {
            // Create character boxes
            createCharBoxes('payer_name_boxes', 20, 'payer_name');
            createCharBoxes('hospital_name_boxes', 20, 'hospital_name');
            createCharBoxes('payer_phone_boxes', 15, 'payer_phone');
            createCharBoxes('hospital_address_boxes', 24, 'hospital_address');
            createCharBoxes('payer_fax_boxes', 15, 'payer_fax');
            createCharBoxes('rohini_id_boxes', 10, 'rohini_id');
            createCharBoxes('payer_email_boxes', 20, 'payer_email');
            createCharBoxes('patient_name_boxes', 24, 'patient_name');
            createCharBoxes('age_years_boxes', 3, 'age_years');
            createCharBoxes('date_of_birth_boxes', 10, 'date_of_birth');
            createCharBoxes('mobile_number_boxes', 10, 'mobile_number');
            createCharBoxes('alternative_contact_boxes', 10, 'alternative_contact');
            createCharBoxes('uhid_boxes', 15, 'uhid');
            createCharBoxes('policy_number_boxes', 15, 'policy_number');
            createCharBoxes('employee_id_boxes', 15, 'employee_id');
            createCharBoxes('treating_doctor_name_boxes', 20, 'treating_doctor_name');
            createCharBoxes('treating_doctor_contact_boxes', 12, 'treating_doctor_contact');
            createCharBoxes('nature_of_illness_boxes', 50, 'nature_of_illness');
            createCharBoxes('relevant_clinical_findings_boxes', 50, 'relevant_clinical_findings');
            createCharBoxes('duration_of_present_ailment_boxes', 3, 'duration_of_present_ailment');
            createCharBoxes('date_of_first_consultation_boxes', 10, 'date_of_first_consultation');
            createCharBoxes('past_history_present_ailment_boxes', 50, 'past_history_present_ailment');
            createCharBoxes('provisional_diagnosis_boxes', 20, 'provisional_diagnosis');
            createCharBoxes('icd_10_code_boxes', 8, 'icd_10_code');
            createCharBoxes('admission_datetime_boxes', 16, 'admission_datetime');
            createCharBoxes('ip_number_boxes', 20, 'ip_number');
            createCharBoxes('expected_length_of_stay_boxes', 3, 'expected_length_of_stay');
            createCharBoxes('ward_type_boxes', 15, 'ward_type');
            createCharBoxes('estimated_treatment_cost_boxes', 12, 'estimated_treatment_cost');
            createCharBoxes('doctor_name_boxes', 20, 'doctor_name');
            createCharBoxes('doctor_qualification_boxes', 15, 'doctor_qualification');
            createCharBoxes('doctor_registration_boxes', 15, 'doctor_registration');
            createCharBoxes('patient_signature_name_boxes', 20, 'patient_signature_name');
            createCharBoxes('signature_date_boxes', 10, 'signature_date');
            createCharBoxes('signature_time_boxes', 5, 'signature_time');

            // Add event listener to speciality dropdown
            document.getElementById('speciality_id').addEventListener('change', loadDoctors);
            document.getElementById('treating_doctor_id').addEventListener('change', loadDoctorDetails);

            // Populate form with existing claim data if available
            {% if claim %}
            const prefillClaim = {{ claim | tojson }};
            const c = prefillClaim;
            
            // Populate character boxes
            if (c.payer_name) {
                populateCharBoxes('payer_name', c.payer_name);
                updateHiddenField('payer_name');
            }
            
            if (c.hospital_name) {
                populateCharBoxes('hospital_name_boxes', c.hospital_name);
                updateHiddenField('hospital_name');
            }
            
            if (c.patient_name) {
                populateCharBoxes('patient_name_boxes', c.patient_name);
                updateHiddenField('patient_name');
            }
            
            if (c.mobile_number) {
                populateCharBoxes('mobile_number_boxes', c.mobile_number);
                updateHiddenField('mobile_number');
            }
            
            if (c.uhid) {
                populateCharBoxes('uhid_boxes', c.uhid);
                updateHiddenField('uhid');
            }
            
            if (c.policy_number) {
                populateCharBoxes('policy_number_boxes', c.policy_number);
                updateHiddenField('policy_number');
            }
            
            if (c.nature_of_illness) {
                populateCharBoxes('nature_of_illness_boxes', c.nature_of_illness);
                updateHiddenField('nature_of_illness');
            }
            
            if (c.ip_number) {
                populateCharBoxes('ip_number_boxes', c.ip_number);
                updateHiddenField('ip_number');
            }
            
            if (c.estimated_treatment_cost) {
                populateCharBoxes('estimated_treatment_cost_boxes', c.estimated_treatment_cost);
                updateHiddenField('estimated_treatment_cost');
            }
            
            // Populate regular fields
            if (c.payer_type) {
                document.querySelector('[name="payer_type"]').value = c.payer_type;
            }
            if (c.gender) {
                document.querySelector(`[name="gender"][value="${c.gender}"]`).checked = true;
            }
            if (c.admission_type) {
                document.querySelector(`[name="admission_type"][value="${c.admission_type}"]`).checked = true;
            }
            
            // Auto-populate speciality and doctor
            if (c.speciality_id) {
                document.getElementById('speciality_id').value = c.speciality_id;
                setTimeout(() => {
                    loadDoctors();
                    if (c.treating_doctor_id) {
                        setTimeout(() => {
                            document.getElementById('treating_doctor_id').value = c.treating_doctor_id;
                            loadDoctorDetails();
                        }, 500);
                    }
                }, 500);
            }
            {% endif %}
        });
    </script>
</body>
</html>
'''