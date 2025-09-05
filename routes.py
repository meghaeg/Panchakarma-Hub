from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, current_app
from datetime import datetime, timedelta
from models import Patient, Centre, Doctor, Appointment, Feedback, Admin
from utils import *
from email_service import *
import json
import csv
from io import StringIO

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
patient_bp = Blueprint('patient', __name__, url_prefix='/patient')
centre_bp = Blueprint('centre', __name__, url_prefix='/centre')
doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Authentication Routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        print(f"Login attempt: {data}")  # Debug log
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        
        if role == 'patient':
            # For patients, use Aadhar instead of email
            aadhar = data.get('aadhar')
            patient = Patient()
            user = patient.find_by_aadhar(aadhar)
            if user and patient.check_password(password, user['password']):
                session['user_id'] = user['patient_id']
                session['role'] = 'patient'
                session['name'] = user['name']
                return jsonify({'success': True, 'redirect': '/patient/dashboard'})
        
        elif role == 'centre':
            centre = Centre()
            user = centre.find_by_email(email)
            if user and centre.check_password(password, user['password']):
                if user['status'] != 'approved':
                    return jsonify({'success': False, 'message': 'Centre not approved yet'})
                session['user_id'] = user['centre_id']
                session['role'] = 'centre'
                session['name'] = user['name']
                return jsonify({'success': True, 'redirect': '/centre/dashboard'})
        
        elif role == 'doctor':
            doctor = Doctor()
            user = doctor.find_by_email(email)
            if user and doctor.check_password(password, user['password']):
                session['user_id'] = user['doctor_id']
                session['role'] = 'doctor'
                session['name'] = user['name']
                session['centre_id'] = user['centre_id']
                return jsonify({'success': True, 'redirect': '/doctor/dashboard'})
        
        elif role == 'admin':
            admin = Admin()
            user = admin.find_by_email(email)
            if user and admin.check_password(password, user['password']):
                session['user_id'] = user['admin_id']
                session['role'] = 'admin'
                session['name'] = user['name']
                return jsonify({'success': True, 'redirect': '/admin/dashboard'})
        
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('auth/login.html')

# Patient booking route
@patient_bp.route('/book-appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'user_id' not in session or session.get('role') != 'patient':
        return redirect(url_for('auth.login'))
    
    if request.method == 'GET':
        # Show booking form
        centre = Centre()
        centres = centre.get_approved_centres()
        return render_template('patient/book_appointment.html', centres=centres)
    
    # Handle POST request
    data = request.get_json()
    centre_id = data.get('centre_id')
    therapy_type = data.get('therapy_type')
    preferred_date = data.get('preferred_date')
    time_slot = data.get('time_slot', '09:00-10:00')  # Get time slot from request
    notes = data.get('notes', '')
    
    # Validate date is within next 5 days
    from datetime import datetime, timedelta
    booking_date = datetime.strptime(preferred_date, '%Y-%m-%d')
    today = datetime.now()
    max_date = today + timedelta(days=5)
    
    if booking_date < today or booking_date > max_date:
        return jsonify({'success': False, 'message': 'Please select a date within the next 5 days'})
    
    # Create appointment with pending status (no doctor assigned yet)
    appointment_data = {
        'appointment_id': generate_appointment_id(),
        'patient_id': session.get('user_id'),
        'centre_id': centre_id,
        'doctor_id': None,  # No doctor assigned initially
        'therapy_type': therapy_type,
        'appointment_date': preferred_date,
        'time_slot': time_slot,
        'status': 'pending_approval',  # Needs centre approval
        'notes': notes,
        'created_at': datetime.now()
    }
    
    appointment = Appointment()
    result = appointment.create(appointment_data)
    
    if result:
        # Send notification to centre for approval
        send_appointment_notification_to_centre(centre_id, appointment_data)
        
        return jsonify({
            'success': True, 
            'message': 'Appointment request submitted successfully. You will receive confirmation once approved by the centre.',
            'appointment_id': appointment_data['appointment_id']
        })
    
    return jsonify({'success': False, 'message': 'Failed to submit appointment request'})

def find_available_doctor(centre_id, date, time_slot):
    """Find available doctor based on schedule"""
    doctor = Doctor()
    doctors = doctor.find_by_centre(centre_id)
    
    # Check each doctor's availability
    appointment = Appointment()
    for doc in doctors:
        existing_appointments = appointment.find_by_doctor_and_date(doc['doctor_id'], date, time_slot)
        if not existing_appointments:  # Doctor is available
            return doc
    
    return None

def send_appointment_notification_to_centre(centre_id, appointment_data):
    """Send appointment approval request to centre"""
    centre = Centre()
    centre_info = centre.find_by_id(centre_id)
    
    if centre_info:
        subject = "New Appointment Request - Approval Required"
        body = f"""
        Dear {centre_info['name']},
        
        A new appointment request has been submitted:
        
        Appointment ID: {appointment_data['appointment_id']}
        Patient ID: {appointment_data['patient_id']}
        Therapy Type: {appointment_data['therapy_type']}
        Preferred Date: {appointment_data['appointment_date']}
        Time Slot: {appointment_data['time_slot']}
        Assigned Doctor: {appointment_data.get('assigned_doctor', 'To be assigned')}
        
        Please log in to your centre dashboard to approve or reject this appointment.
        
        Best regards,
        Panchakarma Portal Team
        """
        
        send_email(centre_info['email'], subject, body)

# Centre approval route
@centre_bp.route('/approve-appointment', methods=['POST'])
def approve_appointment():
    if 'user_id' not in session or session.get('role') != 'centre':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.get_json()
    appointment_id = data.get('appointment_id')
    action = data.get('action')  # 'approve' or 'reject'
    
    appointment = Appointment()
    appointment_data = appointment.find_by_id(appointment_id)
    
    if not appointment_data:
        return jsonify({'success': False, 'message': 'Appointment not found'})
    
    if action == 'approve':
        appointment.update_status(appointment_id, 'confirmed')
        send_appointment_confirmation_to_patient(appointment_data)
        message = 'Appointment approved successfully'
    else:
        appointment.update_status(appointment_id, 'rejected')
        send_appointment_rejection_to_patient(appointment_data)
        message = 'Appointment rejected'
    
    return jsonify({'success': True, 'message': message})

def send_appointment_confirmation_to_patient(appointment_data):
    """Send appointment confirmation email to patient"""
    patient = Patient()
    patient_info = patient.find_by_id(appointment_data['patient_id'])
    
    if patient_info:
        subject = "Appointment Confirmed - Panchakarma Portal"
        body = f"""
        Dear {patient_info['name']},
        
        Your appointment has been confirmed!
        
        Appointment Details:
        - Appointment ID: {appointment_data['appointment_id']}
        - Date: {appointment_data['appointment_date']}
        - Time: {appointment_data['time_slot']}
        - Therapy Type: {appointment_data['therapy_type']}
        - Assigned Doctor: {appointment_data.get('assigned_doctor', 'TBD')}
        
        Please arrive 15 minutes before your scheduled time.
        
        Best regards,
        Panchakarma Portal Team
        """
        
        send_email(patient_info['email'], subject, body)

def send_appointment_rejection_to_patient(appointment_data):
    """Send appointment rejection email to patient"""
    patient = Patient()
    patient_info = patient.find_by_id(appointment_data['patient_id'])
    
    if patient_info:
        subject = "Appointment Request - Update Required"
        body = f"""
        Dear {patient_info['name']},
        
        We regret to inform you that your appointment request could not be confirmed for the selected date and time.
        
        Appointment ID: {appointment_data['appointment_id']}
        Requested Date: {appointment_data['appointment_date']}
        Requested Time: {appointment_data['time_slot']}
        
        Please try booking for a different date or time slot.
        
        Best regards,
        Panchakarma Portal Team
        """
        
        send_email(patient_info['email'], subject, body)

# Post-therapy report route
@doctor_bp.route('/complete-therapy', methods=['POST'])
def complete_therapy():
    if 'user_id' not in session or session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.get_json()
    appointment_id = data.get('appointment_id')
    progress_notes = data.get('progress_notes')
    medications = data.get('medications', '')
    after_therapy_instructions = data.get('after_therapy_instructions', '')
    next_session_recommendation = data.get('next_session_recommendation', '')
    
    # Update appointment status
    appointment = Appointment()
    appointment.update_status(appointment_id, 'completed')
    
    # Save therapy report
    therapy_report = {
        'appointment_id': appointment_id,
        'doctor_id': session['user_id'],
        'progress_notes': progress_notes,
        'medications': medications,
        'after_therapy_instructions': after_therapy_instructions,
        'next_session_recommendation': next_session_recommendation,
        'completed_at': datetime.now()
    }
    
    # Add therapy report to database
    db = get_db_connection()
    db.therapy_reports.insert_one(therapy_report)
    
    # Send post-therapy email to patient
    send_post_therapy_email(appointment_id, therapy_report)
    
    return jsonify({'success': True, 'message': 'Therapy completed and report sent to patient'})

def send_post_therapy_email(appointment_id, therapy_report):
    """Send post-therapy progress email to patient"""
    appointment = Appointment()
    appointment_data = appointment.find_by_id(appointment_id)
    
    if appointment_data:
        patient = Patient()
        patient_info = patient.find_by_id(appointment_data['patient_id'])
        
        if patient_info:
            subject = "Therapy Completed - Progress Report & Instructions"
            body = f"""
            Dear {patient_info['name']},
            
            Your Panchakarma therapy session has been completed successfully!
            
            Session Details:
            - Date: {appointment_data['appointment_date']}
            - Therapy Type: {appointment_data['therapy_type']}
            
            Progress Report:
            {therapy_report['progress_notes']}
            
            Prescribed Medications:
            {therapy_report['medications'] or 'None prescribed'}
            
            Post-Therapy Instructions:
            {therapy_report['after_therapy_instructions']}
            
            Next Session Recommendation:
            {therapy_report['next_session_recommendation'] or 'No immediate follow-up required'}
            
            Please follow the instructions carefully for optimal results. If you have any concerns, please contact your assigned doctor.
            
            Best regards,
            Your Panchakarma Care Team
            """
            
            send_email(patient_info['email'], subject, body)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'No data received'})
            
            role = data.get('role')
            print(f"Signup attempt: {role} - {data.get('name', 'Unknown')}")
            
            if role == 'patient':
                if not validate_aadhar(data.get('aadhar')):
                    return jsonify({'success': False, 'message': 'Invalid Aadhar number'})
                
                patient = Patient()
                # Detect DB mode and warn if using in-memory fallback (no persistence)
                try:
                    from utils import InMemoryDB  # type: ignore
                    if isinstance(patient.db, InMemoryDB):
                        return jsonify({'success': False, 'message': 'Database offline: running in in-memory mode. Please configure MongoDB Atlas/network access to persist data.'})
                except Exception:
                    pass
                existing = patient.find_by_aadhar(data['aadhar'])
                if existing:
                    return jsonify({'success': False, 'message': 'Patient already exists'})
                
                patient_data = {
                    'patient_id': generate_patient_id(),
                    'aadhar': data['aadhar'],
                    'name': data['name'],
                    'age': data['age'],
                    'dob': data['dob'],
                    'email': data['email'],
                    'phone': data['phone'],
                    'address': data['address'],
                    'blood_group': data.get('blood_group', ''),
                    'health_issues': data.get('health_issues', ''),
                    'medications': data.get('medications', ''),
                    'password': data['password']
                }
                
                # Attempt insert
                before_count = patient.db.patients.count_documents({'aadhar': patient_data['aadhar']}) if hasattr(patient.db.patients, 'count_documents') else 0
                result = patient.create(patient_data)
                print(f"Patient creation result: {result}")
                # Verify insert by fetching back by aadhar and count change
                created = patient.find_by_aadhar(patient_data['aadhar'])
                after_count = patient.db.patients.count_documents({'aadhar': patient_data['aadhar']}) if hasattr(patient.db.patients, 'count_documents') else (1 if created else 0)
                acknowledged = getattr(result, 'acknowledged', True)
                if result and hasattr(result, 'inserted_id') and created and after_count > before_count and acknowledged:
                    return jsonify({'success': True, 'message': 'Patient registered successfully'})
                else:
                    return jsonify({'success': False, 'message': 'Failed to create patient record'})
            elif role == 'centre':
                return jsonify({'success': False, 'message': 'Centre accounts are created by Super Admin only'})
            
            return jsonify({'success': False, 'message': 'Invalid role specified'})
            
        except Exception as e:
            print(f"Signup error: {e}")
            return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'})
    
    return render_template('auth/signup.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

# Patient Routes
@patient_bp.route('/dashboard')
def dashboard():
    if session.get('role') != 'patient':
        return redirect(url_for('auth.login'))
    
    patient_id = session.get('user_id')
    appointment = Appointment()
    appointments = appointment.find_by_patient(patient_id)
    
    return render_template('patient/dashboard.html', appointments=appointments)


@patient_bp.route('/progress/<appointment_id>')
def view_progress(appointment_id):
    if session.get('role') != 'patient':
        return redirect(url_for('auth.login'))
    
    appointment = Appointment()
    appointment_data = appointment.find_by_id(appointment_id)
    
    if not appointment_data or appointment_data['patient_id'] != session.get('user_id'):
        return redirect(url_for('patient.dashboard'))
    
    return render_template('patient/progress.html', appointment=appointment_data)

@patient_bp.route('/feedback', methods=['GET', 'POST'])
def submit_feedback():
    if session.get('role') != 'patient':
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        data = request.get_json()
        patient_id = session.get('user_id')
        
        feedback_data = {
            'patient_id': patient_id,
            'appointment_id': data['appointment_id'],
            'feedback_type': data['feedback_type'],
            'target_id': data['target_id'],
            'rating': data['rating'],
            'comments': data['comments']
        }
        
        feedback = Feedback()
        result = feedback.create(feedback_data)
        
        if result:
            return jsonify({'success': True, 'message': 'Feedback submitted successfully'})
        
        return jsonify({'success': False, 'message': 'Feedback submission failed'})
    
    # Get patient's completed appointments for feedback
    patient_id = session.get('user_id')
    appointment = Appointment()
    completed_appointments = [apt for apt in appointment.find_by_patient(patient_id) if apt['status'] == 'completed']
    
    return render_template('patient/feedback.html', appointments=completed_appointments)

# Centre Routes
@centre_bp.route('/dashboard')
def dashboard():
    if session.get('role') != 'centre':
        return redirect(url_for('auth.login'))
    
    centre_id = session.get('user_id')
    appointment = Appointment()
    appointments = appointment.find_by_centre(centre_id)
    
    # Get patient details for each appointment
    patient = Patient()
    for apt in appointments:
        patient_data = patient.find_by_id(apt['patient_id'])
        if patient_data:
            apt['patient_name'] = patient_data['name']
            apt['patient_email'] = patient_data['email']
            apt['patient_phone'] = patient_data['phone']
        else:
            apt['patient_name'] = 'Unknown'
            apt['patient_email'] = ''
            apt['patient_phone'] = ''
    
    doctor = Doctor()
    doctors = doctor.find_by_centre(centre_id)
    
    return render_template('centre/dashboard.html', appointments=appointments, doctors=doctors)

@centre_bp.route('/add-doctor', methods=['GET', 'POST'])
def add_doctor():
    if session.get('role') != 'centre':
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        data = request.get_json()
        centre_id = session.get('user_id')
        
        doctor_data = {
            'doctor_id': generate_doctor_id(),
            'centre_id': centre_id,
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'specialization': data['specialization'],
            'experience': data['experience'],
            'qualification': data['qualification'],
            'license_number': data['license_number'],
            'password': data['password']
        }
        
        doctor = Doctor()
        result = doctor.create(doctor_data)
        
        if result:
            return jsonify({'success': True, 'message': 'Doctor added successfully'})
        
        return jsonify({'success': False, 'message': 'Failed to add doctor'})
    
    return render_template('centre/add_doctor.html')

@centre_bp.route('/assign-doctor', methods=['POST'])
def assign_doctor():
    if session.get('role') != 'centre':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.get_json()
    appointment_id = data['appointment_id']
    doctor_id = data['doctor_id']
    
    # Get appointment details
    appointment = Appointment()
    apt_data = appointment.find_by_id(appointment_id)
    if not apt_data:
        return jsonify({'success': False, 'message': 'Appointment not found'})
    
    # Get doctor and find available time slot
    doctor = Doctor()
    available_slots = doctor.get_available_slots(doctor_id, apt_data['appointment_date'])
    
    if not available_slots:
        return jsonify({'success': False, 'message': 'No available time slots for this doctor on the selected date'})
    
    # Assign the first available slot
    assigned_time_slot = available_slots[0]
    
    db = get_db_connection()
    result = db.appointments.update_one(
        {'appointment_id': appointment_id},
        {'$set': {
            'doctor_id': doctor_id, 
            'status': 'confirmed',
            'time_slot': assigned_time_slot,
            'assigned_doctor': doctor.find_by_id(doctor_id)['name']
        }}
    )
    
    if result.modified_count > 0:
        # Send doctor assignment email to patient
        patient = Patient()
        patient_data = patient.find_by_id(apt_data['patient_id'])
        doctor_data = doctor.find_by_id(doctor_id)
        
        # Update appointment data for email
        apt_data['time_slot'] = assigned_time_slot
        apt_data['assigned_doctor'] = doctor_data['name']
        
        send_doctor_assignment(patient_data['email'], patient_data['name'], doctor_data)
        send_appointment_confirmation_to_patient(apt_data)
        
        return jsonify({
            'success': True, 
            'message': f'Doctor assigned successfully. Time slot: {assigned_time_slot}',
            'assigned_time_slot': assigned_time_slot
        })
    
    return jsonify({'success': False, 'message': 'Assignment failed'})

@centre_bp.route('/api/doctor-slots/<doctor_id>/<date>')
def get_doctor_slots(doctor_id, date):
    """Get available time slots for a doctor on a specific date"""
    if session.get('role') != 'centre':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    doctor = Doctor()
    available_slots = doctor.get_available_slots(doctor_id, date)
    
    return jsonify({
        'success': True,
        'available_slots': available_slots,
        'doctor_name': doctor.find_by_id(doctor_id)['name'] if doctor.find_by_id(doctor_id) else 'Unknown'
    })

# Doctor Routes
@doctor_bp.route('/dashboard')
def dashboard():
    if session.get('role') != 'doctor':
        return redirect(url_for('auth.login'))
    
    doctor_id = session.get('user_id')
    appointment = Appointment()
    # Only get appointments that are assigned to this doctor
    appointments = appointment.find_by_doctor(doctor_id)
    
    # Filter out pending appointments (only show confirmed and beyond)
    appointments = [apt for apt in appointments if apt.get('status') in ['confirmed', 'in_progress', 'completed']]
    
    # Get patient details for each appointment and convert ObjectId to string
    patient = Patient()
    for apt in appointments:
        # Convert ObjectId to string for JSON serialization
        if '_id' in apt:
            apt['_id'] = str(apt['_id'])
        
        patient_data = patient.find_by_id(apt['patient_id'])
        if patient_data:
            apt['patient_name'] = patient_data['name']
            apt['patient_email'] = patient_data['email']
            apt['patient_phone'] = patient_data['phone']
        else:
            apt['patient_name'] = 'Unknown'
            apt['patient_email'] = ''
            apt['patient_phone'] = ''
    
    return render_template('doctor/dashboard.html', appointments=appointments)

@doctor_bp.route('/start-therapy', methods=['POST'])
def start_therapy():
    if session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.get_json()
    appointment_id = data.get('appointment_id')
    
    if not appointment_id:
        return jsonify({'success': False, 'message': 'Appointment ID required'})
    
    # Update appointment status to in_progress
    appointment = Appointment()
    result = appointment.update_status(appointment_id, 'in_progress')
    
    if result.modified_count > 0:
        return jsonify({'success': True, 'message': 'Therapy started successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to start therapy'})

@doctor_bp.route('/patient/<appointment_id>')
def view_patient(appointment_id):
    if session.get('role') != 'doctor':
        return redirect(url_for('auth.login'))
    
    appointment = Appointment()
    appointment_data = appointment.find_by_id(appointment_id)
    
    if not appointment_data or appointment_data['doctor_id'] != session.get('user_id'):
        return redirect(url_for('doctor.dashboard'))
    
    patient = Patient()
    patient_data = patient.find_by_id(appointment_data['patient_id'])
    
    # Get patient's previous appointments with this doctor
    previous_appointments = [apt for apt in appointment.find_by_patient(appointment_data['patient_id']) 
                           if apt['doctor_id'] == session.get('user_id') and apt['status'] == 'completed']
    
    return render_template('doctor/patient_details.html', 
                         appointment=appointment_data, 
                         patient=patient_data,
                         previous_appointments=previous_appointments)

@doctor_bp.route('/add-vitals', methods=['POST'])
def add_vitals():
    if session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.get_json()
    appointment_id = data['appointment_id']
    vitals = {
        'date': datetime.now(),
        'bp_systolic': data['bp_systolic'],
        'bp_diastolic': data['bp_diastolic'],
        'blood_sugar': data['blood_sugar'],
        'notes': data['notes']
    }
    
    db = get_db_connection()
    result = db.appointments.update_one(
        {'appointment_id': appointment_id},
        {'$push': {'vitals': vitals}}
    )
    
    if result.modified_count > 0:
        return jsonify({'success': True, 'message': 'Vitals recorded successfully'})
    
    return jsonify({'success': False, 'message': 'Failed to record vitals'})

@doctor_bp.route('/add-progress', methods=['POST'])
def add_progress():
    if session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.get_json()
    appointment_id = data['appointment_id']
    progress = {
        'date': datetime.now(),
        'notes': data['notes'],
        'improvement_score': data['improvement_score']  # 1-10 scale
    }
    
    db = get_db_connection()
    result = db.appointments.update_one(
        {'appointment_id': appointment_id},
        {'$push': {'progress_notes': progress}}
    )
    
    if result.modified_count > 0:
        return jsonify({'success': True, 'message': 'Progress updated successfully'})
    
    return jsonify({'success': False, 'message': 'Failed to update progress'})

@doctor_bp.route('/complete-therapy-session', methods=['POST'])
def complete_therapy_session():
    if session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.get_json()
    appointment_id = data['appointment_id']
    
    therapy_summary = {
        'completion_date': datetime.now(),
        'summary': data['summary'],
        'recommendations': data['recommendations'],
        'next_session_date': data.get('next_session_date'),
        'final_vitals': data.get('final_vitals', {})
    }
    
    db = get_db_connection()
    result = db.appointments.update_one(
        {'appointment_id': appointment_id},
        {'$set': {'status': 'completed', 'therapy_summary': therapy_summary}}
    )
    
    if result.modified_count > 0:
        # Send therapy completion email
        appointment = Appointment()
        apt_data = appointment.find_by_id(appointment_id)
        patient = Patient()
        patient_data = patient.find_by_id(apt_data['patient_id'])
        doctor = Doctor()
        doctor_data = doctor.find_by_id(session.get('user_id'))
        centre = Centre()
        centre_data = centre.find_by_id(apt_data['centre_id'])
        
        summary_details = {
            'patient_id': apt_data['patient_id'],
            'therapy_type': apt_data['therapy_type'],
            'duration': len(apt_data.get('progress_notes', [])),
            'doctor_name': doctor_data['name'],
            'centre_name': centre_data['name'],
            'completion_date': therapy_summary['completion_date'].strftime('%Y-%m-%d'),
            'progress_summary': therapy_summary['summary'],
            'recommendations': therapy_summary['recommendations'],
            'next_session': therapy_summary.get('next_session_date', 'To be determined')
        }
        
        send_therapy_summary(patient_data['email'], patient_data['name'], summary_details)
        
        return jsonify({'success': True, 'message': 'Therapy completed successfully'})
    
    return jsonify({'success': False, 'message': 'Failed to complete therapy'})

# Admin Routes
@admin_bp.route('/dashboard')
def dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    
    centre = Centre()
    db = get_db_connection()
    
    all_centres = list(db.centres.find({}))
    approved_centres = list(db.centres.find({'status': 'approved'}))
    
    feedback = Feedback()
    centre_feedback = list(db.feedback.find({'feedback_type': 'centre', 'status': 'pending'}))
    
    return render_template('admin/dashboard.html', 
                         all_centres=all_centres,
                         approved_centres=approved_centres,
                         centre_feedback=centre_feedback)

@admin_bp.route('/generate-report')
def generate_report():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    db = get_db_connection()
    centres = list(db.centres.find({}))
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Centre ID', 'Name', 'Email', 'Phone', 'City', 'State', 'Pincode', 'NABH', 'Status', 'Created At'])
    for c in centres:
        writer.writerow([
            c.get('centre_id',''), c.get('name',''), c.get('email',''), c.get('phone',''),
            c.get('city',''), c.get('state',''), c.get('pincode',''),
            'Yes' if c.get('nabh_accredited') else 'No', c.get('status',''),
            c.get('created_at').strftime('%Y-%m-%d') if c.get('created_at') else ''
        ])
    output.seek(0)
    csv_data = output.getvalue()
    return current_app.response_class(
        csv_data,
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename="centres_report.csv"'
        }
    )

@admin_bp.route('/create-centre', methods=['POST'])
def create_centre_by_admin():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        data = request.get_json()
        centre_model = Centre()
        existing = centre_model.find_by_email(data['email'])
        if existing:
            return jsonify({'success': False, 'message': 'Centre with this email already exists'})
        
        centre_data = {
            'centre_id': generate_centre_id(),
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'address': data['address'],
            'city': data['city'],
            'state': data['state'],
            'pincode': data['pincode'],
            'nabh_accredited': data.get('nabh_accredited', False),
            'license_number': data['license_number'],
            'password': centre_model.hash_password(data['password']),
            'created_at': datetime.now(),
            'status': 'approved',
            'approved_by': session.get('user_id'),
            'approved_at': datetime.now()
        }
        result = centre_model.db.centres.insert_one(centre_data)
        if result and hasattr(result, 'inserted_id'):
            return jsonify({'success': True, 'message': 'Centre created and approved successfully'})
        return jsonify({'success': False, 'message': 'Failed to create centre'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/suspend-centre', methods=['POST'])
def suspend_centre():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.get_json()
    centre_id = data['centre_id']
    reason = data['reason']
    
    db = get_db_connection()
    result = db.centres.update_one(
        {'centre_id': centre_id},
        {'$set': {'status': 'suspended', 'suspension_reason': reason, 'suspended_at': datetime.now()}}
    )
    
    if result.modified_count > 0:
        return jsonify({'success': True, 'message': 'Centre suspended successfully'})
    
    return jsonify({'success': False, 'message': 'Failed to suspend centre'})

@admin_bp.route('/force-withdraw-centre', methods=['POST'])
def force_withdraw_centre():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.get_json()
    centre_id = data['centre_id']
    reason = data.get('reason', 'Forced withdrawal by admin')
    
    db = get_db_connection()
    result = db.centres.update_one(
        {'centre_id': centre_id},
        {'$set': {'status': 'withdrawn', 'withdrawn_reason': reason, 'withdrawn_at': datetime.now()}}
    )
    
    if result.modified_count > 0:
        return jsonify({'success': True, 'message': 'Centre forcibly withdrawn successfully'})
    
    return jsonify({'success': False, 'message': 'Failed to force withdraw centre'})

@admin_bp.route('/schedule-audit', methods=['POST'])
def schedule_audit():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.get_json()
    centre_id = data.get('centre_id')
    audit_date = data.get('audit_date')
    notes = data.get('notes','')
    if not centre_id or not audit_date:
        return jsonify({'success': False, 'message': 'centre_id and audit_date are required'}), 400
    db = get_db_connection()
    audit = {
        'audit_id': f"AUD{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'centre_id': centre_id,
        'scheduled_by': session.get('user_id'),
        'audit_date': audit_date,
        'notes': notes,
        'created_at': datetime.now(),
        'status': 'scheduled'
    }
    res = db.audits.insert_one(audit)
    if res and hasattr(res, 'inserted_id'):
        return jsonify({'success': True, 'message': 'Audit scheduled successfully'})
    return jsonify({'success': False, 'message': 'Failed to schedule audit'})

@admin_bp.route('/analytics')
def analytics():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    db = get_db_connection()
    stats = {
        'patients': db.patients.count_documents({}) if hasattr(db.patients, 'count_documents') else len(db.patients.find()),
        'centres': db.centres.count_documents({}) if hasattr(db.centres, 'count_documents') else len(db.centres.find()),
        'doctors': db.doctors.count_documents({}) if hasattr(db.doctors, 'count_documents') else len(db.doctors.find()),
        'appointments': db.appointments.count_documents({}) if hasattr(db.appointments, 'count_documents') else len(db.appointments.find()),
        'feedback': db.feedback.count_documents({}) if hasattr(db.feedback, 'count_documents') else len(db.feedback.find()),
    }
    appt_status = {
        'pending_approval': len(list(db.appointments.find({'status': 'pending_approval'}))),
        'confirmed': len(list(db.appointments.find({'status': 'confirmed'}))),
        'completed': len(list(db.appointments.find({'status': 'completed'})))
    }
    avg_rating = 0
    ratings = [f.get('rating',0) for f in db.feedback.find({})]
    if ratings:
        avg_rating = round(sum(ratings)/len(ratings), 2)
    return render_template('admin/analytics.html', stats=stats, appt_status=appt_status, avg_rating=avg_rating)

@admin_bp.route('/patient-info/<patient_id>')
def get_patient_info(patient_id):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    patient = Patient()
    info = patient.find_by_id(patient_id)
    if not info:
        return jsonify({'success': False, 'message': 'Patient not found'}), 404
    
    response = {
        'success': True,
        'patient_id': info.get('patient_id'),
        'name': info.get('name'),
        'aadhar': info.get('aadhar'),
        'email': info.get('email'),
        'phone': info.get('phone'),
        'age': info.get('age'),
        'dob': info.get('dob'),
        'blood_group': info.get('blood_group'),
        'address': info.get('address'),
        'health_issues': info.get('health_issues'),
        'medications': info.get('medications')
    }
    return jsonify(response)

# API Routes for getting data
@patient_bp.route('/api/centres')
def get_centres():
    centre = Centre()
    centres = centre.get_approved_centres()
    return jsonify([{
        'centre_id': c['centre_id'],
        'name': c['name'],
        'city': c['city'],
        'state': c['state'],
        'nabh_accredited': c.get('nabh_accredited', False)
    } for c in centres])

@doctor_bp.route('/api/progress-data/<appointment_id>')
def get_progress_data(appointment_id):
    if session.get('role') not in ['doctor', 'patient']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    appointment = Appointment()
    apt_data = appointment.find_by_id(appointment_id)
    
    if not apt_data:
        return jsonify({'error': 'Appointment not found'}), 404
    
    # Format progress data for chart
    progress_data = []
    for i, note in enumerate(apt_data.get('progress_notes', [])):
        progress_data.append({
            'day': i + 1,
            'score': note.get('improvement_score', 0),
            'date': note['date'].strftime('%Y-%m-%d') if isinstance(note['date'], datetime) else note['date']
        })
    
    return jsonify(progress_data)
