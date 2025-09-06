from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, current_app
from datetime import datetime, timedelta
from models import Patient, Centre, Doctor, Appointment, DetoxAppointment, Feedback, Admin, ProgressTracking, Notification
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

# Detox Therapy Routes
@patient_bp.route('/book-detox', methods=['GET', 'POST'])
def book_detox():
    if 'user_id' not in session or session.get('role') != 'patient':
        return redirect(url_for('auth.login'))
    
    if request.method == 'GET':
        # Show detox booking form
        centre = Centre()
        centres = centre.get_approved_centres()
        return render_template('patient/book_detox.html', centres=centres)
    
    # Handle POST request
    data = request.get_json()
    centre_id = data.get('centre_id')
    plan_type = data.get('plan_type')  # weight_loss_short, weight_loss_full, diabetes_short, diabetes_full
    start_date = data.get('start_date')
    notes = data.get('notes', '')
    
    # Validate date is within next 5 days
    booking_date = datetime.strptime(start_date, '%Y-%m-%d')
    today = datetime.now()
    max_date = today + timedelta(days=5)
    
    if booking_date < today or booking_date > max_date:
        return jsonify({'success': False, 'message': 'Please select a date within the next 5 days'})
    
    # Create detox appointment (therapy_time will be auto-assigned after centre approval)
    detox_appointment_data = {
        'detox_appointment_id': generate_detox_appointment_id(),
        'patient_id': session.get('user_id'),
        'centre_id': centre_id,
        'plan_type': plan_type,
        'start_date': start_date,
        'notes': notes
    }
    
    detox_appointment = DetoxAppointment()
    result = detox_appointment.create(detox_appointment_data)
    
    if result:
        return jsonify({
            'success': True, 
            'message': 'Detox therapy request submitted successfully. You will receive confirmation once approved by the centre.',
            'detox_appointment_id': detox_appointment_data['detox_appointment_id']
        })
    
    return jsonify({'success': False, 'message': 'Failed to submit detox therapy request'})

@patient_bp.route('/detox-schedule/<detox_appointment_id>')
def view_detox_schedule(detox_appointment_id):
    if session.get('role') != 'patient':
        return redirect(url_for('auth.login'))
    
    detox_appointment = DetoxAppointment()
    appointment = detox_appointment.find_by_id(detox_appointment_id)
    
    if not appointment or appointment['patient_id'] != session.get('user_id'):
        return redirect(url_for('patient.dashboard'))
    
    return render_template('patient/detox_schedule.html', appointment=appointment)

@patient_bp.route('/detox-dashboard')
def detox_dashboard():
    if session.get('role') != 'patient':
        return redirect(url_for('auth.login'))
    
    patient_id = session.get('user_id')
    detox_appointment = DetoxAppointment()
    appointments = detox_appointment.find_by_patient(patient_id)
    
    return render_template('patient/detox_dashboard.html', appointments=appointments)


@patient_bp.route('/detox-progress/<detox_appointment_id>')
def detox_progress(detox_appointment_id):
    """Patient view of detox therapy progress"""
    if session.get('role') != 'patient':
        return redirect(url_for('auth.login'))
    
    patient_id = session.get('user_id')
    detox_appointment = DetoxAppointment()
    appointment = detox_appointment.find_by_id(detox_appointment_id)
    
    if not appointment or appointment['patient_id'] != patient_id:
        return redirect(url_for('patient.detox_dashboard'))
    
    # Get progress data
    progress_tracking = ProgressTracking()
    progress_data = progress_tracking.get_daily_progress_summary(detox_appointment_id)
    
    return render_template('patient/detox_progress.html', 
                         appointment=appointment, 
                         progress_data=progress_data)


@patient_bp.route('/api/detox-progress-data/<detox_appointment_id>')
def api_detox_progress_data(detox_appointment_id):
    """API endpoint for detox progress data (for charts)"""
    if session.get('role') != 'patient':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        patient_id = session.get('user_id')
        detox_appointment = DetoxAppointment()
        appointment = detox_appointment.find_by_id(detox_appointment_id)
        
        if not appointment or appointment['patient_id'] != patient_id:
            return jsonify({'success': False, 'message': 'Unauthorized'})
        
        progress_tracking = ProgressTracking()
        progress_data = progress_tracking.get_daily_progress_summary(detox_appointment_id)
        
        # Format data for Chart.js
        chart_data = {
            'labels': [],  # Day numbers
            'progress_scores': [],  # Progress scores
            'vitals': {
                'bp_systolic': [],
                'bp_diastolic': [],
                'blood_sugar': [],
                'weight': [],
                'heart_rate': []
            }
        }
        
        for day_num in sorted(progress_data.keys()):
            day_data = progress_data[day_num]
            chart_data['labels'].append(f"Day {day_num}")
            
            # Progress scores
            chart_data['progress_scores'].append(day_data.get('progress_score', None))
            
            # Vitals
            vitals = day_data.get('vitals', {})
            chart_data['vitals']['bp_systolic'].append(vitals.get('bp_systolic', None))
            chart_data['vitals']['bp_diastolic'].append(vitals.get('bp_diastolic', None))
            chart_data['vitals']['blood_sugar'].append(vitals.get('blood_sugar', None))
            chart_data['vitals']['weight'].append(vitals.get('weight', None))
            chart_data['vitals']['heart_rate'].append(vitals.get('heart_rate', None))
        
        return jsonify({'success': True, 'data': chart_data})
        
    except Exception as e:
        print(f"Error in api_detox_progress_data: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

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

# Centre Detox Approval Routes
@centre_bp.route('/detox-dashboard')
def detox_dashboard():
    if session.get('role') != 'centre':
        return redirect(url_for('auth.login'))
    
    centre_id = session.get('user_id')
    detox_appointment = DetoxAppointment()
    appointments = detox_appointment.find_by_centre(centre_id)
    
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
    
    # Get doctors for this centre
    doctor = Doctor()
    doctors = doctor.find_by_centre(centre_id)
    
    return render_template('centre/detox_dashboard.html', appointments=appointments, doctors=doctors)

@centre_bp.route('/approve-detox', methods=['POST'])
def approve_detox():
    try:
        if session.get('role') != 'centre':
            return jsonify({'success': False, 'message': 'Unauthorized'})
        
        data = request.get_json()
        detox_appointment_id = data.get('detox_appointment_id')
        action = data.get('action')  # 'approve' or 'reject'
        doctor_id = data.get('doctor_id')
        therapy_time = data.get('therapy_time')
        
        detox_appointment = DetoxAppointment()
        appointment_data = detox_appointment.find_by_id(detox_appointment_id)
        
        if not appointment_data:
            return jsonify({'success': False, 'message': 'Detox appointment not found'})
        
        if action == 'approve':
            if not doctor_id or not therapy_time:
                return jsonify({'success': False, 'message': 'Doctor and time slot must be selected'})
            
            # Check for conflicts
            doctor = Doctor()
            doctor_data = doctor.find_by_id(doctor_id)
            
            if not doctor_data:
                return jsonify({'success': False, 'message': 'Selected doctor not found'})
            
            # Check if doctor is available at the selected time for the entire detox duration
            start_date = datetime.strptime(appointment_data['start_date'], '%Y-%m-%d')
            
            # Get duration safely
            duration = 7  # Default duration
            if 'schedule' in appointment_data and 'plan_info' in appointment_data['schedule']:
                duration = appointment_data['schedule']['plan_info'].get('duration', 7)
            
            # Check for conflicts with existing appointments
            db = get_db_connection()
            
            # Calculate working days (excluding Sundays)
            working_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
            doctor_working_days = doctor_data.get('working_days', working_days)
            doctor_working_days = [day.lower() for day in doctor_working_days if day.lower() != 'sunday']
            
            # Check each day, skipping Sundays
            day_count = 0
            current_date = start_date
            
            while day_count < duration:
                day_of_week = current_date.strftime('%A').lower()
                
                # Skip Sundays - don't count them in the duration
                if day_of_week == 'sunday':
                    current_date += timedelta(days=1)
                    continue
                
                # Check if doctor works on this day
                if day_of_week not in doctor_working_days:
                    return jsonify({'success': False, 'message': f'Doctor not available on {day_of_week} (Day {day_count + 1})'})
                
                # Check for existing appointments
                try:
                    existing_appointments = db.detox_appointments.find({
                        'doctor_id': doctor_id,
                        'start_date': current_date.strftime('%Y-%m-%d'),
                        'therapy_time': therapy_time,
                        'status': {'$in': ['confirmed', 'in_progress']}
                    })
                    
                    # Convert to list to check count safely
                    existing_list = list(existing_appointments)
                    if len(existing_list) > 0:
                        return jsonify({'success': False, 'message': f'Doctor already has an appointment at {therapy_time} on {current_date.strftime("%Y-%m-%d")} (Day {day_count + 1})'})
                except Exception as e:
                    print(f"Error checking existing appointments: {e}")
                    # Continue without conflict check if there's an error
                
                # Move to next day and increment counter
                current_date += timedelta(days=1)
                day_count += 1
            
            # Assign doctor and time slot
            result = detox_appointment.assign_doctor_and_time_slot(
                detox_appointment_id, 
                doctor_id, 
                therapy_time
            )
            
            if result:
                # Send email notification to patient
                send_detox_approval_notification(appointment_data, doctor_data, therapy_time)
                
                # Create dashboard notifications
                notification = Notification()
                
                # Patient notification
                notification.create({
                    'user_id': appointment_data['patient_id'],
                    'user_type': 'patient',
                    'title': '✅ Detox Therapy Approved!',
                    'message': f'Your {appointment_data["schedule"]["plan_info"]["name"]} has been approved and assigned to Dr. {doctor_data["name"]} starting {appointment_data["start_date"]} at {therapy_time}.',
                    'type': 'detox',
                    'priority': 'high',
                    'related_id': detox_appointment_id
                })
                
                # Doctor notification
                notification.create({
                    'user_id': doctor_id,
                    'user_type': 'doctor',
                    'title': '👨‍⚕️ New Patient Assignment',
                    'message': f'You have been assigned a new detox therapy patient for {appointment_data["schedule"]["plan_info"]["name"]} starting {appointment_data["start_date"]} at {therapy_time}.',
                    'type': 'detox',
                    'priority': 'medium',
                    'related_id': detox_appointment_id
                })
                
                # Send doctor assignment email
                send_doctor_assignment_notification(doctor_data['email'], doctor_data['name'], appointment_data, appointment_data.get('patient_name', 'Patient'))
                
                message = f'Detox therapy approved and assigned to Dr. {doctor_data["name"]} at {therapy_time}'
            else:
                message = 'Failed to assign doctor and time slot'
        else:
            detox_appointment.update_status(detox_appointment_id, 'rejected')
            send_detox_rejection_notification(appointment_data)
            
            # Create rejection notification for patient
            notification = Notification()
            notification.create({
                'user_id': appointment_data['patient_id'],
                'user_type': 'patient',
                'title': '❌ Detox Therapy Request Update',
                'message': f'Your {appointment_data["schedule"]["plan_info"]["name"]} request could not be approved at this time. Please contact your centre for more information.',
                'type': 'detox',
                'priority': 'medium',
                'related_id': detox_appointment_id
            })
            
            message = 'Detox therapy rejected'
        
        return jsonify({'success': True, 'message': message})
    
    except Exception as e:
        print(f"Error in approve_detox: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@centre_bp.route('/detox-schedule/<detox_appointment_id>')
def centre_view_detox_schedule(detox_appointment_id):
    """Centre view detox schedule for a specific appointment"""
    if session.get('role') != 'centre':
        return redirect(url_for('auth.login'))
    
    detox_appointment = DetoxAppointment()
    appointment = detox_appointment.find_by_id(detox_appointment_id)
    
    if not appointment or appointment['centre_id'] != session.get('user_id'):
        return redirect(url_for('centre.detox_dashboard'))
    
    return render_template('centre/detox_schedule.html', appointment=appointment)

def send_detox_approval_notification(appointment_data, doctor, time_slot):
    """Send detox approval notification to patient"""
    patient = Patient()
    patient_info = patient.find_by_id(appointment_data['patient_id'])
    
    if patient_info:
        subject = "Detox Therapy Approved - Panchakarma Portal"
        body = f"""
        Dear {patient_info['name']},
        
        Your detox therapy has been approved and a doctor has been assigned!
        
        Therapy Details:
        - Plan: {appointment_data['schedule']['plan_info']['name']}
        - Start Date: {appointment_data['start_date']}
        - Duration: {appointment_data['schedule']['plan_info']['duration']} days
        - Assigned Doctor: Dr. {doctor['name']}
        - Daily Therapy Time: {time_slot}
        
        Please log in to your dashboard to view your detailed schedule.
        
        Best regards,
        Panchakarma Portal Team
        """
        
        send_email(patient_info['email'], subject, body)

def send_detox_rejection_notification(appointment_data):
    """Send detox rejection notification to patient"""
    patient = Patient()
    patient_info = patient.find_by_id(appointment_data['patient_id'])
    
    if patient_info:
        subject = "Detox Therapy Request - Update Required"
        body = f"""
        Dear {patient_info['name']},
        
        We regret to inform you that your detox therapy request could not be approved at this time.
        
        Plan: {appointment_data['schedule']['plan_info']['name']}
        Requested Start Date: {appointment_data['start_date']}
        
        Please try booking for a different date or contact the centre directly for more information.
        
        Best regards,
        Panchakarma Portal Team
        """
        
        send_email(patient_info['email'], subject, body)

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

# Doctor Detox Therapy Routes
@doctor_bp.route('/detox-dashboard')
def detox_dashboard():
    if session.get('role') != 'doctor':
        return redirect(url_for('auth.login'))
    
    doctor_id = session.get('user_id')
    detox_appointment = DetoxAppointment()
    appointments = detox_appointment.find_by_doctor(doctor_id)
    
    # Filter out pending appointments (only show confirmed and beyond)
    appointments = [apt for apt in appointments if apt.get('status') in ['confirmed', 'in_progress', 'completed']]
    
    return render_template('doctor/detox_dashboard.html', appointments=appointments)

@doctor_bp.route('/detox-schedule/<detox_appointment_id>')
def view_detox_schedule_doctor(detox_appointment_id):
    if session.get('role') != 'doctor':
        return redirect(url_for('auth.login'))
    
    detox_appointment = DetoxAppointment()
    appointment = detox_appointment.find_by_id(detox_appointment_id)
    
    if not appointment or appointment['doctor_id'] != session.get('user_id'):
        return redirect(url_for('doctor.detox_dashboard'))
    
    return render_template('doctor/detox_schedule.html', appointment=appointment)

@doctor_bp.route('/update-detox-slot', methods=['POST'])
def update_detox_slot():
    try:
        if session.get('role') != 'doctor':
            return jsonify({'success': False, 'message': 'Unauthorized'})
        
        data = request.get_json()
        detox_appointment_id = data.get('detox_appointment_id')
        day = data.get('day')
        slot = data.get('slot')
        new_activity = data.get('new_activity')
        
        if not all([detox_appointment_id, day, slot, new_activity]):
            return jsonify({'success': False, 'message': 'Missing required parameters'})
        
        detox_appointment = DetoxAppointment()
        result = detox_appointment.update_schedule(
            detox_appointment_id, day, slot, new_activity, session.get('name', 'Doctor')
        )
        
        if result:
            return jsonify({'success': True, 'message': 'Schedule updated successfully'})
        
        return jsonify({'success': False, 'message': 'Failed to update schedule'})
    
    except Exception as e:
        print(f"Error in update_detox_slot: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@doctor_bp.route('/add-detox-notes', methods=['POST'])
def add_detox_notes():
    try:
        if session.get('role') != 'doctor':
            return jsonify({'success': False, 'message': 'Unauthorized'})
        
        data = request.get_json()
        detox_appointment_id = data.get('detox_appointment_id')
        day = data.get('day')
        slot = data.get('slot')
        notes = data.get('notes')
        
        if not all([detox_appointment_id, day, slot]):
            return jsonify({'success': False, 'message': 'Missing required parameters'})
        
        detox_appointment = DetoxAppointment()
        result = detox_appointment.add_slot_notes(
            detox_appointment_id, day, slot, notes, session.get('name', 'Doctor')
        )
        
        if result:
            return jsonify({'success': True, 'message': 'Notes added successfully'})
        
        return jsonify({'success': False, 'message': 'Failed to add notes'})
    
    except Exception as e:
        print(f"Error in add_detox_notes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@doctor_bp.route('/approve-detox', methods=['POST'])
def approve_detox():
    if session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.get_json()
    detox_appointment_id = data.get('detox_appointment_id')
    action = data.get('action')  # 'approve' or 'reject'
    
    detox_appointment = DetoxAppointment()
    if action == 'approve':
        result = detox_appointment.update_status(detox_appointment_id, 'confirmed')
        message = 'Detox therapy approved successfully'
    else:
        result = detox_appointment.update_status(detox_appointment_id, 'rejected')
        message = 'Detox therapy rejected'
    
    if result.modified_count > 0:
        return jsonify({'success': True, 'message': message})
    
    return jsonify({'success': False, 'message': 'Failed to update detox therapy status'})


@doctor_bp.route('/quick-update-detox', methods=['POST'])
def quick_update_detox():
    """Quick update for detox therapy progress and vitals"""
    if session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        data = request.get_json()
        detox_appointment_id = data.get('detox_appointment_id')
        update_type = data.get('update_type')  # 'vitals' or 'progress'
        day_number = data.get('day_number')
        notes = data.get('notes', '')
        
        if not all([detox_appointment_id, update_type, day_number]):
            return jsonify({'success': False, 'message': 'Missing required parameters'})
        
        # Get detox appointment details
        detox_appointment = DetoxAppointment()
        appointment = detox_appointment.find_by_id(detox_appointment_id)
        
        if not appointment:
            return jsonify({'success': False, 'message': 'Detox appointment not found'})
        
        # Get current date for the day
        start_date = datetime.strptime(appointment['start_date'], '%Y-%m-%d')
        current_date = start_date + timedelta(days=day_number - 1)
        
        progress_data = {
            'detox_appointment_id': detox_appointment_id,
            'patient_id': appointment['patient_id'],
            'doctor_id': session.get('user_id'),
            'day_number': day_number,
            'date': current_date.strftime('%Y-%m-%d'),
            'update_type': update_type,
            'notes': notes
        }
        
        if update_type == 'vitals':
            vitals = {}
            if data.get('bp_systolic'):
                vitals['bp_systolic'] = data.get('bp_systolic')
            if data.get('bp_diastolic'):
                vitals['bp_diastolic'] = data.get('bp_diastolic')
            if data.get('blood_sugar'):
                vitals['blood_sugar'] = data.get('blood_sugar')
            if data.get('weight'):
                vitals['weight'] = data.get('weight')
            if data.get('temperature'):
                vitals['temperature'] = data.get('temperature')
            if data.get('heart_rate'):
                vitals['heart_rate'] = data.get('heart_rate')
            
            progress_data['vitals'] = vitals
            
        elif update_type == 'progress':
            progress_score = data.get('progress_score')
            if progress_score is not None:
                progress_data['progress_score'] = int(progress_score)
        
        # Create progress tracking entry
        progress_tracking = ProgressTracking()
        result = progress_tracking.create(progress_data)
        
        if result.inserted_id:
            return jsonify({'success': True, 'message': f'{update_type.title()} updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save update'})
            
    except Exception as e:
        print(f"Error in quick_update_detox: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})


@doctor_bp.route('/get-detox-progress/<detox_appointment_id>')
def get_detox_progress(detox_appointment_id):
    """Get progress data for a detox appointment"""
    if session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        progress_tracking = ProgressTracking()
        progress_data = progress_tracking.get_daily_progress_summary(detox_appointment_id)
        
        return jsonify({'success': True, 'data': progress_data})
        
    except Exception as e:
        print(f"Error in get_detox_progress: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})


# Notification Routes
@patient_bp.route('/notifications')
def patient_notifications():
    """Get patient notifications"""
    if session.get('role') != 'patient':
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    notification = Notification()
    notifications = notification.find_by_user(user_id, 'patient')
    unread_count = notification.get_unread_count(user_id, 'patient')
    
    return render_template('patient/notifications.html', 
                         notifications=notifications, 
                         unread_count=unread_count)


@doctor_bp.route('/notifications')
def doctor_notifications():
    """Get doctor notifications"""
    if session.get('role') != 'doctor':
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    notification = Notification()
    notifications = notification.find_by_user(user_id, 'doctor')
    unread_count = notification.get_unread_count(user_id, 'doctor')
    
    return render_template('doctor/notifications.html', 
                         notifications=notifications, 
                         unread_count=unread_count)


@centre_bp.route('/notifications')
def centre_notifications():
    """Get centre notifications"""
    if session.get('role') != 'centre':
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    notification = Notification()
    notifications = notification.find_by_user(user_id, 'centre')
    unread_count = notification.get_unread_count(user_id, 'centre')
    
    return render_template('centre/notifications.html', 
                         notifications=notifications, 
                         unread_count=unread_count)


@patient_bp.route('/api/notifications')
def api_patient_notifications():
    """API endpoint for patient notifications"""
    if session.get('role') != 'patient':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        user_id = session.get('user_id')
        notification = Notification()
        notifications = notification.find_by_user(user_id, 'patient', limit=20)
        unread_count = notification.get_unread_count(user_id, 'patient')
        
        # Format notifications for JSON response
        formatted_notifications = []
        for notif in notifications:
            formatted_notifications.append({
                'id': notif['notification_id'],
                'title': notif['title'],
                'message': notif['message'],
                'type': notif['type'],
                'priority': notif['priority'],
                'created_at': notif['created_at'].strftime('%Y-%m-%d %H:%M'),
                'is_read': notif['is_read']
            })
        
        return jsonify({
            'success': True, 
            'notifications': formatted_notifications,
            'unread_count': unread_count
        })
        
    except Exception as e:
        print(f"Error in api_patient_notifications: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})


@doctor_bp.route('/api/notifications')
def api_doctor_notifications():
    """API endpoint for doctor notifications"""
    if session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        user_id = session.get('user_id')
        notification = Notification()
        notifications = notification.find_by_user(user_id, 'doctor', limit=20)
        unread_count = notification.get_unread_count(user_id, 'doctor')
        
        # Format notifications for JSON response
        formatted_notifications = []
        for notif in notifications:
            formatted_notifications.append({
                'id': notif['notification_id'],
                'title': notif['title'],
                'message': notif['message'],
                'type': notif['type'],
                'priority': notif['priority'],
                'created_at': notif['created_at'].strftime('%Y-%m-%d %H:%M'),
                'is_read': notif['is_read']
            })
        
        return jsonify({
            'success': True, 
            'notifications': formatted_notifications,
            'unread_count': unread_count
        })
        
    except Exception as e:
        print(f"Error in api_doctor_notifications: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})


@centre_bp.route('/api/notifications')
def api_centre_notifications():
    """API endpoint for centre notifications"""
    if session.get('role') != 'centre':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        user_id = session.get('user_id')
        notification = Notification()
        notifications = notification.find_by_user(user_id, 'centre', limit=20)
        unread_count = notification.get_unread_count(user_id, 'centre')
        
        # Format notifications for JSON response
        formatted_notifications = []
        for notif in notifications:
            formatted_notifications.append({
                'id': notif['notification_id'],
                'title': notif['title'],
                'message': notif['message'],
                'type': notif['type'],
                'priority': notif['priority'],
                'created_at': notif['created_at'].strftime('%Y-%m-%d %H:%M'),
                'is_read': notif['is_read']
            })
        
        return jsonify({
            'success': True, 
            'notifications': formatted_notifications,
            'unread_count': unread_count
        })
        
    except Exception as e:
        print(f"Error in api_centre_notifications: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})


@patient_bp.route('/mark-notification-read/<notification_id>', methods=['POST'])
def mark_patient_notification_read(notification_id):
    """Mark a patient notification as read"""
    if session.get('role') != 'patient':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        user_id = session.get('user_id')
        notification = Notification()
        result = notification.mark_as_read(notification_id, user_id)
        
        if result.modified_count > 0:
            return jsonify({'success': True, 'message': 'Notification marked as read'})
        else:
            return jsonify({'success': False, 'message': 'Notification not found'})
            
    except Exception as e:
        print(f"Error in mark_patient_notification_read: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})


@doctor_bp.route('/mark-notification-read/<notification_id>', methods=['POST'])
def mark_doctor_notification_read(notification_id):
    """Mark a doctor notification as read"""
    if session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        user_id = session.get('user_id')
        notification = Notification()
        result = notification.mark_as_read(notification_id, user_id)
        
        if result.modified_count > 0:
            return jsonify({'success': True, 'message': 'Notification marked as read'})
        else:
            return jsonify({'success': False, 'message': 'Notification not found'})
            
    except Exception as e:
        print(f"Error in mark_doctor_notification_read: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})


@centre_bp.route('/mark-notification-read/<notification_id>', methods=['POST'])
def mark_centre_notification_read(notification_id):
    """Mark a centre notification as read"""
    if session.get('role') != 'centre':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        user_id = session.get('user_id')
        notification = Notification()
        result = notification.mark_as_read(notification_id, user_id)
        
        if result.modified_count > 0:
            return jsonify({'success': True, 'message': 'Notification marked as read'})
        else:
            return jsonify({'success': False, 'message': 'Notification not found'})
            
    except Exception as e:
        print(f"Error in mark_centre_notification_read: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})


@patient_bp.route('/mark-all-notifications-read', methods=['POST'])
def mark_all_patient_notifications_read():
    """Mark all patient notifications as read"""
    if session.get('role') != 'patient':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        user_id = session.get('user_id')
        notification = Notification()
        result = notification.mark_all_as_read(user_id, 'patient')
        
        return jsonify({
            'success': True, 
            'message': f'{result.modified_count} notifications marked as read'
        })
        
    except Exception as e:
        print(f"Error in mark_all_patient_notifications_read: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})


@doctor_bp.route('/mark-all-notifications-read', methods=['POST'])
def mark_all_doctor_notifications_read():
    """Mark all doctor notifications as read"""
    if session.get('role') != 'doctor':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        user_id = session.get('user_id')
        notification = Notification()
        result = notification.mark_all_as_read(user_id, 'doctor')
        
        return jsonify({
            'success': True, 
            'message': f'{result.modified_count} notifications marked as read'
        })
        
    except Exception as e:
        print(f"Error in mark_all_doctor_notifications_read: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})


@centre_bp.route('/mark-all-notifications-read', methods=['POST'])
def mark_all_centre_notifications_read():
    """Mark all centre notifications as read"""
    if session.get('role') != 'centre':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        user_id = session.get('user_id')
        notification = Notification()
        result = notification.mark_all_as_read(user_id, 'centre')
        
        return jsonify({
            'success': True, 
            'message': f'{result.modified_count} notifications marked as read'
        })
        
    except Exception as e:
        print(f"Error in mark_all_centre_notifications_read: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})


# Precaution Notification Functions
def send_precaution_notifications():
    """Send precaution notifications for upcoming detox therapies"""
    try:
        detox_appointment = DetoxAppointment()
        db = get_db_connection()
        
        # Get all confirmed detox appointments starting tomorrow
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        appointments = list(db.detox_appointments.find({
            'start_date': tomorrow,
            'status': 'confirmed'
        }))
        
        notification = Notification()
        
        for appointment in appointments:
            # Get patient details
            patient = db.patients.find_one({'patient_id': appointment['patient_id']})
            if not patient:
                continue
            
            # Send pre-therapy precautions email
            send_pre_therapy_precautions_notification(
                patient['email'], 
                patient['name'], 
                appointment
            )
            
            # Create dashboard notification
            notification.create({
                'user_id': appointment['patient_id'],
                'user_type': 'patient',
                'title': '⚠️ Pre-Therapy Precautions',
                'message': f'Your detox therapy starts tomorrow! Please review the important precautions and preparations.',
                'type': 'precaution',
                'priority': 'high',
                'related_id': appointment['detox_appointment_id'],
                'expires_at': datetime.now() + timedelta(days=2)  # Expire after 2 days
            })
        
        print(f"Sent precaution notifications for {len(appointments)} appointments")
        return True
        
    except Exception as e:
        print(f"Error sending precaution notifications: {str(e)}")
        return False


def send_daily_reminders():
    """Send daily therapy reminders"""
    try:
        detox_appointment = DetoxAppointment()
        db = get_db_connection()
        
        # Get all in-progress detox appointments
        appointments = list(db.detox_appointments.find({
            'status': 'in_progress'
        }))
        
        notification = Notification()
        
        for appointment in appointments:
            # Calculate current day
            start_date = datetime.strptime(appointment['start_date'], '%Y-%m-%d')
            current_day = (datetime.now() - start_date).days + 1
            
            if current_day <= appointment['schedule']['plan_info']['duration']:
                # Get patient details
                patient = db.patients.find_one({'patient_id': appointment['patient_id']})
                if not patient:
                    continue
                
                # Send daily reminder email
                send_daily_therapy_reminder(
                    patient['email'], 
                    patient['name'], 
                    appointment, 
                    current_day
                )
                
                # Create dashboard notification
                notification.create({
                    'user_id': appointment['patient_id'],
                    'user_type': 'patient',
                    'title': f'📅 Daily Therapy Reminder - Day {current_day}',
                    'message': f'Your detox therapy session for day {current_day} is scheduled. Please arrive on time.',
                    'type': 'reminder',
                    'priority': 'medium',
                    'related_id': appointment['detox_appointment_id'],
                    'expires_at': datetime.now() + timedelta(days=1)  # Expire after 1 day
                })
        
        print(f"Sent daily reminders for {len(appointments)} appointments")
        return True
        
    except Exception as e:
        print(f"Error sending daily reminders: {str(e)}")
        return False


def send_completion_notifications():
    """Send post-therapy completion notifications"""
    try:
        detox_appointment = DetoxAppointment()
        db = get_db_connection()
        
        # Get all detox appointments that completed today
        today = datetime.now().strftime('%Y-%m-%d')
        
        appointments = list(db.detox_appointments.find({
            'status': 'in_progress'
        }))
        
        notification = Notification()
        completed_count = 0
        
        for appointment in appointments:
            # Calculate if therapy should be completed today
            start_date = datetime.strptime(appointment['start_date'], '%Y-%m-%d')
            duration = appointment['schedule']['plan_info']['duration']
            
            # Calculate end date (skipping Sundays)
            end_date = start_date
            day_count = 0
            while day_count < duration:
                day_of_week = end_date.strftime('%A').lower()
                if day_of_week != 'sunday':
                    day_count += 1
                end_date += timedelta(days=1)
            
            if end_date.strftime('%Y-%m-%d') == today:
                # Get patient details
                patient = db.patients.find_one({'patient_id': appointment['patient_id']})
                if not patient:
                    continue
                
                # Update status to completed
                detox_appointment.update_status(appointment['detox_appointment_id'], 'completed')
                
                # Send completion email
                send_post_therapy_precautions_notification(
                    patient['email'], 
                    patient['name'], 
                    appointment
                )
                
                # Create dashboard notification
                notification.create({
                    'user_id': appointment['patient_id'],
                    'user_type': 'patient',
                    'title': '🏁 Therapy Completed!',
                    'message': f'Congratulations! Your {appointment["schedule"]["plan_info"]["name"]} has been completed. Please review the post-therapy care instructions.',
                    'type': 'completion',
                    'priority': 'high',
                    'related_id': appointment['detox_appointment_id']
                })
                
                completed_count += 1
        
        print(f"Sent completion notifications for {completed_count} appointments")
        return True
        
    except Exception as e:
        print(f"Error sending completion notifications: {str(e)}")
        return False


# Scheduled notification routes (can be called by cron jobs or scheduled tasks)
@patient_bp.route('/send-precaution-notifications', methods=['POST'])
def send_precaution_notifications_route():
    """Route to send precaution notifications (for scheduled tasks)"""
    if send_precaution_notifications():
        return jsonify({'success': True, 'message': 'Precaution notifications sent successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to send precaution notifications'})


@patient_bp.route('/send-daily-reminders', methods=['POST'])
def send_daily_reminders_route():
    """Route to send daily reminders (for scheduled tasks)"""
    if send_daily_reminders():
        return jsonify({'success': True, 'message': 'Daily reminders sent successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to send daily reminders'})


@patient_bp.route('/send-completion-notifications', methods=['POST'])
def send_completion_notifications_route():
    """Route to send completion notifications (for scheduled tasks)"""
    if send_completion_notifications():
        return jsonify({'success': True, 'message': 'Completion notifications sent successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to send completion notifications'})


# Email Testing Routes
@patient_bp.route('/test-email', methods=['POST'])
def test_email():
    """Test email functionality"""
    try:
        data = request.get_json()
        test_email_address = data.get('email')
        
        if not test_email_address:
            return jsonify({'success': False, 'message': 'Email address required'})
        
        # Test email connection first
        from email_service import test_email_connection, send_test_email
        
        if not test_email_connection():
            return jsonify({'success': False, 'message': 'Email connection failed. Please check credentials.'})
        
        # Send test email
        if send_test_email(test_email_address):
            return jsonify({'success': True, 'message': f'Test email sent successfully to {test_email_address}'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send test email'})
            
    except Exception as e:
        print(f"Error in test_email: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})


@patient_bp.route('/email-test-page')
def email_test_page():
    """Serve email test page"""
    return render_template('email_test.html')
