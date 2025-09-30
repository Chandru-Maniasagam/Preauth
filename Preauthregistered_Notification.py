"""
Preauthregistered_Notification.py
Handles pre-authorization notifications after form submission
"""

from flask import Blueprint, request, jsonify
from app.database.firebase_client import FirebaseClient
from datetime import datetime
import logging

# Initialize Firebase client
firebase_client = FirebaseClient()

def get_db():
    """Get Firestore database client"""
    return firebase_client.get_firestore_client()

# Create blueprint
preauth_notification_bp = Blueprint('preauth_notification', __name__)

def send_sms(phone_number: str, message: str) -> dict:
    """Send SMS notification (mock implementation)"""
    try:
        # Mock SMS sending - replace with actual SMS service
        logging.info(f"SMS sent to {phone_number}: {message[:50]}...")
        return {
            'success': True,
            'message_id': f"SMS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'status': 'sent'
        }
    except Exception as e:
        logging.error(f"SMS sending failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'status': 'failed'
        }

def send_email(email: str, subject: str, message: str) -> dict:
    """Send email notification (mock implementation)"""
    try:
        # Mock email sending - replace with actual email service
        logging.info(f"Email sent to {email}: {subject}")
        return {
            'success': True,
            'message_id': f"EMAIL_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'status': 'sent'
        }
    except Exception as e:
        logging.error(f"Email sending failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'status': 'failed'
        }

def send_whatsapp(phone_number: str, message: str) -> dict:
    """Send WhatsApp notification (mock implementation)"""
    try:
        # Mock WhatsApp sending - replace with actual WhatsApp service
        logging.info(f"WhatsApp sent to {phone_number}: {message[:50]}...")
        return {
            'success': True,
            'message_id': f"WA_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'status': 'sent'
        }
    except Exception as e:
        logging.error(f"WhatsApp sending failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'status': 'failed'
        }

def create_notification_message(claim_data: dict) -> str:
    """Create notification message for preauth registered"""
    patient_name = claim_data.get('patient_name', 'Patient')
    preauth_id = claim_data.get('claim_id', 'N/A')
    submission_date = claim_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    hospital_name = claim_data.get('hospital_name', 'Hospital')
    
    message = f"""Dear {patient_name},

Your Pre-Authorization request (ID: {preauth_id}) has been submitted successfully on {submission_date}.

We will notify you once the status is updated.

Thank you,
{hospital_name}
Contact: +91-9876543210"""
    return message

@preauth_notification_bp.route('/send-preauth-notification/<claim_id>', methods=['POST'])
def send_preauth_notification(claim_id: str):
    """Send notification for a specific claim"""
    try:
        db = get_db()
        claim_ref = db.collection('claims').document(claim_id)
        claim_doc = claim_ref.get()
        
        if not claim_doc.exists:
            return jsonify({'error': 'Claim not found'}), 404
        
        claim_data = claim_doc.to_dict()
        
        # Check if claim is in preauth_registered status
        if claim_data.get('status') != 'preauth_registered':
            return jsonify({
                'error': 'Claim is not in preauth_registered status',
                'current_status': claim_data.get('status')
            }), 400
        
        # Get patient and doctor contact information
        patient_name = claim_data.get('patient_name', 'Patient')
        patient_mobile = claim_data.get('mobile_number', '')
        patient_email = claim_data.get('email_id', '')
        
        doctor_name = claim_data.get('treating_doctor_name', '')
        doctor_contact = claim_data.get('treating_doctor_contact', '')
        
        # Create notification message
        message = create_notification_message(claim_data)
        
        # Send notifications
        notifications_sent_details = []
        
        # Send to patient
        if patient_mobile:
            sms_result = send_sms(patient_mobile, message)
            notifications_sent_details.append({
                'type': 'SMS',
                'recipient': patient_mobile,
                'status': sms_result['status'],
                'message_id': sms_result.get('message_id', '')
            })
        
        if patient_email:
            email_result = send_email(patient_email, f"Pre-Authorization Request {claim_id}", message)
            notifications_sent_details.append({
                'type': 'Email',
                'recipient': patient_email,
                'status': email_result['status'],
                'message_id': email_result.get('message_id', '')
            })
        
        # Send WhatsApp to patient
        if patient_mobile:
            whatsapp_result = send_whatsapp(patient_mobile, message)
            notifications_sent_details.append({
                'type': 'WhatsApp',
                'recipient': patient_mobile,
                'status': whatsapp_result['status'],
                'message_id': whatsapp_result.get('message_id', '')
            })
        
        # Send to doctor
        if doctor_contact:
            doctor_message = f"""Dear Dr. {doctor_name},

A new Pre-Authorization request (ID: {claim_id}) has been submitted for your patient {patient_name}.

Please review and provide necessary medical documentation.

Thank you,
{claim_data.get('hospital_name', 'Hospital')}"""
            
            sms_result = send_sms(doctor_contact, doctor_message)
            notifications_sent_details.append({
                'type': 'SMS',
                'recipient': doctor_contact,
                'status': sms_result['status'],
                'message_id': sms_result.get('message_id', '')
            })
            
            whatsapp_result = send_whatsapp(doctor_contact, doctor_message)
            notifications_sent_details.append({
                'type': 'WhatsApp',
                'recipient': doctor_contact,
                'status': whatsapp_result['status'],
                'message_id': whatsapp_result.get('message_id', '')
            })
        
        # Update claim with notification details
        claim_ref.update({
            'notification_sent_at': datetime.now().isoformat(),
            'notification_details': notifications_sent_details,
            'last_notification_status': 'sent'
        })
        
        return jsonify({
            'success': True,
            'message': 'Notifications sent successfully',
            'details': {
                'claim_id': claim_id,
                'patient_name': patient_name,
                'notifications_sent': notifications_sent_details
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error sending notification for claim {claim_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to send notification',
            'details': str(e)
        }), 500

@preauth_notification_bp.route('/preauth-notification-status/<claim_id>', methods=['GET'])
def get_preauth_notification_status(claim_id: str):
    """Get notification status for a specific claim"""
    try:
        db = get_db()
        claim_ref = db.collection('claims').document(claim_id)
        claim_doc = claim_ref.get()
        
        if not claim_doc.exists:
            return jsonify({'error': 'Claim not found'}), 404
        
        claim_data = claim_doc.to_dict()
        
        return jsonify({
            'claim_id': claim_id,
            'status': claim_data.get('status'),
            'notification_sent_at': claim_data.get('notification_sent_at'),
            'last_notification_status': claim_data.get('last_notification_status'),
            'notification_details': claim_data.get('notification_details', [])
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting notification status for claim {claim_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to get notification status',
            'details': str(e)
        }), 500

@preauth_notification_bp.route('/resend-preauth-notification/<claim_id>', methods=['POST'])
def resend_preauth_notification(claim_id: str):
    """Resend notification for a specific claim"""
    return send_preauth_notification(claim_id)

@preauth_notification_bp.route('/bulk-send-notifications', methods=['POST'])
def bulk_send_notifications():
    """Send notifications for multiple claims"""
    try:
        data = request.get_json()
        claim_ids = data.get('claim_ids', [])
        
        if not claim_ids:
            return jsonify({'error': 'No claim IDs provided'}), 400
        
        results = []
        for claim_id in claim_ids:
            try:
                # Call the individual notification function
                response = send_preauth_notification(claim_id)
                results.append({
                    'claim_id': claim_id,
                    'success': response[1] == 200,
                    'status_code': response[1],
                    'message': response[0].get_json() if hasattr(response[0], 'get_json') else str(response[0])
                })
            except Exception as e:
                results.append({
                    'claim_id': claim_id,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'message': 'Bulk notification processing completed',
            'results': results
        }), 200
        
    except Exception as e:
        logging.error(f"Error in bulk notification: {str(e)}")
        return jsonify({
            'error': 'Failed to process bulk notifications',
            'details': str(e)
        }), 500
