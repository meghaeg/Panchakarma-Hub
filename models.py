from datetime import datetime
from utils import get_db_connection, generate_progress_id, generate_notification_id
import bcrypt
from pymongo import ASCENDING


class User:
    def __init__(self):
        self.db = get_db_connection()
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    def check_password(self, password, hashed):
        """Check password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)

class Patient(User):
    def create(self, data):
        """Create new patient"""
        patient_data = {
            'patient_id': data['patient_id'],
            'aadhar': data['aadhar'],
            'name': data['name'],
            'age': data['age'],
            'dob': data['dob'],
            'email': data['email'],
            'phone': data['phone'],
            'address': data['address'],
            'blood_group': data['blood_group'],
            'health_issues': data['health_issues'],
            'medications': data['medications'],
            'password': self.hash_password(data['password']),
            'created_at': datetime.now(),
            'status': 'active'
        }
        return self.db.patients.insert_one(patient_data)
    
    def find_by_aadhar(self, aadhar):
        """Find patient by Aadhar number"""
        return self.db.patients.find_one({'aadhar': aadhar})
    
    def find_by_id(self, patient_id):
        """Find patient by ID"""
        return self.db.patients.find_one({'patient_id': patient_id})

class Centre(User):
    def create(self, data):
        """Create new centre"""
        centre_data = {
            'centre_id': data['centre_id'],
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'address': data['address'],
            'city': data['city'],
            'state': data['state'],
            'pincode': data['pincode'],
            'nabh_accredited': data.get('nabh_accredited', False),
            'license_number': data['license_number'],
            'password': self.hash_password(data['password']),
            'created_at': datetime.now(),
            'status': 'pending',  # pending, approved, rejected, suspended
            'approved_by': None,
            'approved_at': None
        }
        return self.db.centres.insert_one(centre_data)
    
    def find_by_email(self, email):
        """Find centre by email"""
        return self.db.centres.find_one({'email': email})
    
    def find_by_id(self, centre_id):
        """Find centre by ID"""
        return self.db.centres.find_one({'centre_id': centre_id})
    
    def get_approved_centres(self):
        """Get all approved centres"""
        return list(self.db.centres.find({'status': 'approved'}))

class Doctor(User):
    def create(self, data):
        """Create new doctor"""
        doctor_data = {
            'doctor_id': data['doctor_id'],
            'centre_id': data['centre_id'],
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'specialization': data['specialization'],
            'experience': data['experience'],
            'qualification': data['qualification'],
            'license_number': data['license_number'],
            'password': self.hash_password(data['password']),
            'created_at': datetime.now(),
            'status': 'active',
            'available_sessions': data.get('available_sessions', ['09:00-10:00', '10:00-11:00', '11:00-12:00', '14:00-15:00', '15:00-16:00', '16:00-17:00']),
            'working_days': data.get('working_days', ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])
        }
        return self.db.doctors.insert_one(doctor_data)
    
    def find_by_email(self, email):
        """Find doctor by email"""
        return self.db.doctors.find_one({'email': email})
    
    def find_by_centre(self, centre_id):
        """Find all doctors in a centre"""
        return list(self.db.doctors.find({'centre_id': centre_id, 'status': 'active'}))
    
    def find_by_id(self, doctor_id):
        """Find doctor by ID"""
        return self.db.doctors.find_one({'doctor_id': doctor_id})
    
    def get_available_slots(self, doctor_id, date):
        """Get available time slots for a doctor on a specific date"""
        doctor = self.find_by_id(doctor_id)
        if not doctor:
            return []
        
        # Get doctor's available sessions
        available_sessions = doctor.get('available_sessions', ['09:00-10:00', '10:00-11:00', '11:00-12:00', '14:00-15:00', '15:00-16:00', '16:00-17:00'])
        
        # Check which slots are already booked
        appointment = Appointment()
        booked_appointments = appointment.find_by_doctor_and_date(doctor_id, date, None)
        booked_slots = [apt.get('time_slot') for apt in booked_appointments if apt.get('time_slot')]
        
        # Return available slots
        return [slot for slot in available_sessions if slot not in booked_slots]

class Appointment:
    def __init__(self):
        self.db = get_db_connection()
    
    def create(self, data):
        """Create new appointment with auto-assignment of doctor and time slot"""
        # Check if centre is approved
        centre = self.db.centres.find_one(
            {'centre_id': data['centre_id'], 'status': 'approved'}
        )
        if not centre:
            raise ValueError('Centre not approved or does not exist')

        # Get available doctors at this centre
        doctors = list(self.db.doctors.find({
            'centre_id': data['centre_id'],
            'status': 'active'
        }))
        
        if not doctors:
            raise ValueError('No doctors available at this centre')

        # Convert appointment date to datetime object
        appointment_date = data['appointment_date']
        if isinstance(appointment_date, str):
            appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d')
        
        # Get day of week (e.g., 'monday', 'tuesday')
        day_of_week = appointment_date.strftime('%A').lower()
        
        # Find first available doctor with matching working day and available slot
        assigned_doctor = None
        assigned_slot = None
        
        for doctor in doctors:
            # Check if doctor works on this day
            working_days = [day.lower() for day in doctor.get('working_days', [])]
            if day_of_week not in working_days:
                continue
                
            # Get doctor's available sessions
            available_sessions = doctor.get('available_sessions', [
                '09:00-10:00', '10:00-11:00', '11:00-12:00',
                '14:00-15:00', '15:00-16:00', '16:00-17:00'
            ])
            
            # Get booked slots for this doctor on this date
            booked_appointments = self.find_by_doctor_and_date(
                doctor['doctor_id'], 
                appointment_date,
                None
            )
            booked_slots = [apt['time_slot'] for apt in booked_appointments 
                          if apt.get('time_slot')]
            
            # Find first available slot
            for slot in available_sessions:
                if slot not in booked_slots:
                    assigned_doctor = doctor
                    assigned_slot = slot
                    break
                    
            if assigned_doctor:
                break
        
        if not assigned_doctor or not assigned_slot:
            raise ValueError('No available time slots at this centre')
        
        # Create appointment
        appointment_data = {
            'appointment_id': data['appointment_id'],
            'patient_id': data['patient_id'],
            'centre_id': data['centre_id'],
            'doctor_id': assigned_doctor['doctor_id'],
            'therapy_type': data['therapy_type'],
            'appointment_date': appointment_date,
            'time_slot': assigned_slot,
            'status': 'pending_approval',  # Centre needs to confirm
            'notes': data.get('notes', ''),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'assigned_doctor': assigned_doctor['name']
        }
        
        result = self.db.appointments.insert_one(appointment_data)
        return result
    
    def find_by_id(self, appointment_id):
        """Find appointment by ID"""
        return self.db.appointments.find_one({'appointment_id': appointment_id})
    
    def find_by_doctor_and_date(self, doctor_id, date, time_slot=None):
        """Find appointments for doctor on specific date and optional time slot"""
        # Convert date to datetime object if it's a string
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d')
            
        # Set up date range for the entire day
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        
        query = {
            'doctor_id': doctor_id,
            'appointment_date': {
                '$gte': start_date,
                '$lt': end_date
            },
            'status': {'$in': ['confirmed', 'pending_approval']}
        }
        
        if time_slot:
            query['time_slot'] = time_slot
            
        return list(self.db.appointments.find(query))
    
    def update_status(self, appointment_id, status, **updates):
        """
        Update appointment status and optional fields
        
        Args:
            appointment_id: ID of the appointment to update
            status: New status (e.g., 'confirmed', 'cancelled', 'completed')
            **updates: Additional fields to update (e.g., doctor_id, time_slot)
        """
        update_data = {
            'status': status,
            'updated_at': datetime.now()
        }
        update_data.update(updates)
        
        return self.db.appointments.update_one(
            {'appointment_id': appointment_id},
            {'$set': update_data}
        )
    
    def find_by_centre(self, centre_id, status=None):
        """
        Find appointments for a centre with patient and doctor details
        
        Args:
            centre_id: ID of the centre
            status: Optional status filter (e.g., 'pending_approval', 'confirmed')
        """
        query = {'centre_id': centre_id}
        if status:
            query['status'] = status
            
        appointments = list(self.db.appointments.find(query).sort([('appointment_date', ASCENDING)]))
        
        # Populate patient and doctor names and contact details
        for appointment in appointments:
            # Get patient details
            if appointment.get('patient_id'):
                patient = self.db.patients.find_one({'patient_id': appointment['patient_id']})
                if patient:
                    appointment['patient_name'] = patient['name']
                    appointment['patient_email'] = patient.get('email', '')
                    appointment['patient_phone'] = patient.get('phone', '')
                else:
                    appointment['patient_name'] = 'Unknown Patient'
                    appointment['patient_email'] = ''
                    appointment['patient_phone'] = ''
            
            # Get doctor name
            if appointment.get('doctor_id'):
                doctor = self.db.doctors.find_one({'doctor_id': appointment['doctor_id']})
                appointment['doctor_name'] = doctor['name'] if doctor else 'Unknown Doctor'
        
        return appointments
    
    def find_available_slots(self, centre_id, date):
        """
        Find all available time slots at a centre on a specific date
        
        Args:
            centre_id: ID of the centre
            date: Date to check for available slots (YYYY-MM-DD or datetime)
            
        Returns:
            dict: {
                'doctor_id': {
                    'doctor_name': str,
                    'available_slots': [str]  # List of available time slots
                }
            }
        """
        # Convert date to datetime object if it's a string
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d')
        
        # Get all active doctors at this centre
        doctors = list(self.db.doctors.find({
            'centre_id': centre_id,
            'status': 'active'
        }))
        
        if not doctors:
            return {}
        
        # Get day of week (e.g., 'monday', 'tuesday')
        day_of_week = date.strftime('%A').lower()
        
        available_slots = {}
        
        for doctor in doctors:
            # Check if doctor works on this day
            working_days = [day.lower() for day in doctor.get('working_days', [])]
            if day_of_week not in working_days:
                continue
                
            # Get doctor's available sessions
            doctor_slots = doctor.get('available_sessions', [
                '09:00-10:00', '10:00-11:00', '11:00-12:00',
                '14:00-15:00', '15:00-16:00', '16:00-17:00'
            ])
            
            # Get booked slots for this doctor on this date
            booked_appointments = self.find_by_doctor_and_date(
                doctor['doctor_id'], 
                date
            )
            booked_slots = {apt['time_slot'] for apt in booked_appointments 
                          if apt.get('time_slot')}
            
            # Calculate available slots
            available = [slot for slot in doctor_slots if slot not in booked_slots]
            
            if available:
                available_slots[doctor['doctor_id']] = {
                    'doctor_name': doctor['name'],
                    'available_slots': available
                }
        
        return available_slots
    
    def find_by_patient(self, patient_id, status=None):
        """
        Find appointments for a patient with doctor and centre details
        
        Args:
            patient_id: ID of the patient
            status: Optional status filter (e.g., 'pending_approval', 'confirmed')
        """
        query = {'patient_id': patient_id}
        if status:
            query['status'] = status
            
        appointments = list(self.db.appointments
                          .find(query)
                          .sort('appointment_date', 1))
        
        # Populate doctor and centre names and contact details
        for appointment in appointments:
            # Get doctor details
            if appointment.get('doctor_id'):
                doctor = self.db.doctors.find_one({'doctor_id': appointment['doctor_id']})
                if doctor:
                    appointment['doctor_name'] = doctor['name']
                    appointment['doctor_email'] = doctor.get('email', '')
                    appointment['doctor_phone'] = doctor.get('phone', '')
                else:
                    appointment['doctor_name'] = 'Unknown Doctor'
                    appointment['doctor_email'] = ''
                    appointment['doctor_phone'] = ''
            
            # Get centre details
            if appointment.get('centre_id'):
                centre = self.db.centres.find_one({'centre_id': appointment['centre_id']})
                if centre:
                    appointment['centre_name'] = centre['name']
                    appointment['centre_email'] = centre.get('email', '')
                    appointment['centre_phone'] = centre.get('phone', '')
                else:
                    appointment['centre_name'] = 'Unknown Centre'
                    appointment['centre_email'] = ''
                    appointment['centre_phone'] = ''
        
        return appointments
    
    def find_by_doctor(self, doctor_id):
        """Find appointments by doctor with patient names"""
        appointments = list(self.db.appointments.find({'doctor_id': doctor_id}))
        
        # Populate patient names
        for appointment in appointments:
            if appointment.get('patient_id'):
                patient = self.db.patients.find_one({'patient_id': appointment['patient_id']})
                appointment['patient_name'] = patient['name'] if patient else 'Unknown Patient'
        
        return appointments

class Feedback:
    def __init__(self):
        self.db = get_db_connection()
    
    def create(self, data):
        """Create new feedback"""
        feedback_data = {
            'feedback_id': f"FB{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'patient_id': data['patient_id'],
            'appointment_id': data['appointment_id'],
            'feedback_type': data['feedback_type'],  # doctor, centre
            'target_id': data['target_id'],  # doctor_id or centre_id
            'rating': data['rating'],
            'comments': data['comments'],
            'created_at': datetime.now(),
            'status': 'pending'  # pending, reviewed
        }
        return self.db.feedback.insert_one(feedback_data)
    
    def find_by_target(self, target_id, feedback_type):
        """Find feedback by target (doctor/centre)"""
        return list(self.db.feedback.find({'target_id': target_id, 'feedback_type': feedback_type}))

class DetoxAppointment:
    def __init__(self):
        self.db = get_db_connection()
    
    def create(self, data):
        """Create new detox therapy appointment - doctor assigned after centre approval"""
        from detox_plans import DetoxPlans
        
        # Check if centre is approved
        centre = self.db.centres.find_one(
            {'centre_id': data['centre_id'], 'status': 'approved'}
        )
        if not centre:
            raise ValueError('Centre not approved or does not exist')
        
        # Generate detox schedule based on plan type (without doctor assignment yet)
        plan_type = data.get('plan_type', 'weight_loss_short')
        start_date = data.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        therapy_time = data.get('therapy_time', '10:00')
        
        schedule = DetoxPlans.generate_schedule(plan_type, start_date, therapy_time)
        
        # Create detox appointment without doctor assignment
        detox_appointment_data = {
            'detox_appointment_id': data['detox_appointment_id'],
            'patient_id': data['patient_id'],
            'centre_id': data['centre_id'],
            'doctor_id': None,  # Will be assigned after centre approval
            'plan_type': plan_type,
            'start_date': start_date,
            'therapy_time': therapy_time,
            'status': 'pending_approval',
            'schedule': schedule,
            'notes': data.get('notes', ''),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'assigned_doctor': None  # Will be set after doctor assignment
        }
        
        result = self.db.detox_appointments.insert_one(detox_appointment_data)
        return result
    
    def find_by_id(self, detox_appointment_id):
        """Find detox appointment by ID"""
        return self.db.detox_appointments.find_one({'detox_appointment_id': detox_appointment_id})
    
    def find_by_patient(self, patient_id, status=None):
        """Find detox appointments for a patient"""
        query = {'patient_id': patient_id}
        if status:
            query['status'] = status
            
        appointments = list(self.db.detox_appointments
                          .find(query)
                          .sort('start_date', 1))
        
        # Populate doctor and centre names
        for appointment in appointments:
            if appointment.get('doctor_id'):
                doctor = self.db.doctors.find_one({'doctor_id': appointment['doctor_id']})
                appointment['doctor_name'] = doctor['name'] if doctor else 'Unknown Doctor'
            
            if appointment.get('centre_id'):
                centre = self.db.centres.find_one({'centre_id': appointment['centre_id']})
                appointment['centre_name'] = centre['name'] if centre else 'Unknown Centre'
        
        return appointments
    
    def find_by_centre(self, centre_id, status=None):
        """Find detox appointments for a centre"""
        query = {'centre_id': centre_id}
        if status:
            query['status'] = status
            
        appointments = list(self.db.detox_appointments
                          .find(query)
                          .sort('start_date', 1))
        
        return appointments
    
    def find_by_doctor(self, doctor_id):
        """Find detox appointments by doctor"""
        appointments = list(self.db.detox_appointments.find({'doctor_id': doctor_id}))
        
        # Populate patient names
        for appointment in appointments:
            if appointment.get('patient_id'):
                patient = self.db.patients.find_one({'patient_id': appointment['patient_id']})
                appointment['patient_name'] = patient['name'] if patient else 'Unknown Patient'
        
        return appointments
    
    def update_status(self, detox_appointment_id, status, **updates):
        """Update detox appointment status"""
        update_data = {
            'status': status,
            'updated_at': datetime.now()
        }
        update_data.update(updates)
        
        return self.db.detox_appointments.update_one(
            {'detox_appointment_id': detox_appointment_id},
            {'$set': update_data}
        )
    
    def update_schedule(self, detox_appointment_id, day, slot, new_activity, modified_by):
        """Update a specific slot in the detox schedule"""
        from detox_plans import DetoxPlans
        
        appointment = self.find_by_id(detox_appointment_id)
        if not appointment:
            return False
        
        schedule = appointment.get('schedule', {})
        
        if 'daily_schedules' not in schedule:
            return False
        
        day_key = f'day_{day}'
        if day_key not in schedule['daily_schedules']:
            return False
        
        if slot not in schedule['daily_schedules'][day_key]['slots']:
            return False
        
        updated_schedule = DetoxPlans.update_slot_activity(
            schedule, day, slot, new_activity, modified_by
        )
        
        result = self.db.detox_appointments.update_one(
            {'detox_appointment_id': detox_appointment_id},
            {'$set': {'schedule': updated_schedule, 'updated_at': datetime.now()}}
        )
        
        return result.modified_count > 0
    
    def add_slot_notes(self, detox_appointment_id, day, slot, notes, modified_by):
        """Add notes to a specific slot in the detox schedule"""
        from detox_plans import DetoxPlans
        
        appointment = self.find_by_id(detox_appointment_id)
        if not appointment:
            return False
        
        schedule = appointment.get('schedule', {})
        
        if 'daily_schedules' not in schedule:
            return False
        
        day_key = f'day_{day}'
        if day_key not in schedule['daily_schedules']:
            return False
        
        if slot not in schedule['daily_schedules'][day_key]['slots']:
            return False
        
        updated_schedule = DetoxPlans.add_slot_notes(
            schedule, day, slot, notes, modified_by
        )
        
        result = self.db.detox_appointments.update_one(
            {'detox_appointment_id': detox_appointment_id},
            {'$set': {'schedule': updated_schedule, 'updated_at': datetime.now()}}
        )
        
        return result.modified_count > 0
    
    def assign_doctor_and_time_slot(self, detox_appointment_id, doctor_id, therapy_time):
        """Assign doctor and time slot after centre approval"""
        # Get the appointment
        appointment = self.find_by_id(detox_appointment_id)
        if not appointment:
            return False
        
        # Get doctor details
        doctor = self.db.doctors.find_one({'doctor_id': doctor_id})
        if not doctor:
            return False
        
        # Update the appointment with doctor assignment and time slot
        result = self.db.detox_appointments.update_one(
            {'detox_appointment_id': detox_appointment_id},
            {'$set': {
                'doctor_id': doctor_id,
                'assigned_doctor': doctor['name'],
                'therapy_time': therapy_time,
                'status': 'confirmed',
                'updated_at': datetime.now()
            }}
        )
        
        return result.modified_count > 0

class Admin(User):
    def find_by_email(self, email):
        """Find admin by email"""
        return self.db.admin.find_one({'email': email})
    
    def create_default_admin(self):
        """Create default admin user"""
        admin_data = {
            'admin_id': 'ADMIN001',
            'name': 'Ministry of Ayush Admin',
            'email': 'admin@ayush.gov.in',
            'password': self.hash_password('admin123'),
            'role': 'super_admin',
            'created_at': datetime.now()
        }
        existing = self.db.admin.find_one({'email': 'admin@ayush.gov.in'})
        if not existing:
            return self.db.admin.insert_one(admin_data)
        return existing


class ProgressTracking:
    """Model for tracking detox therapy progress, vitals, and summaries"""
    
    def __init__(self):
        self.db = get_db_connection()
    
    def create(self, data):
        """Create a new progress tracking entry"""
        progress_data = {
            'progress_id': generate_progress_id(),
            'detox_appointment_id': data['detox_appointment_id'],
            'patient_id': data['patient_id'],
            'doctor_id': data['doctor_id'],
            'day_number': data['day_number'],
            'date': data['date'],
            'update_type': data['update_type'],  # 'vitals', 'progress', 'summary'
            'vitals': data.get('vitals', {}),  # BP, blood sugar, weight, etc.
            'progress_score': data.get('progress_score', None),  # 1-10 scale
            'notes': data.get('notes', ''),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        return self.db.progress_tracking.insert_one(progress_data)
    
    def find_by_detox_appointment(self, detox_appointment_id):
        """Find all progress entries for a detox appointment"""
        return list(self.db.progress_tracking.find(
            {'detox_appointment_id': detox_appointment_id}
        ).sort('day_number', 1))
    
    def find_by_patient(self, patient_id):
        """Find all progress entries for a patient"""
        return list(self.db.progress_tracking.find(
            {'patient_id': patient_id}
        ).sort('created_at', -1))
    
    def find_by_doctor(self, doctor_id):
        """Find all progress entries created by a doctor"""
        return list(self.db.progress_tracking.find(
            {'doctor_id': doctor_id}
        ).sort('created_at', -1))
    
    def update(self, progress_id, data):
        """Update a progress tracking entry"""
        update_data = {
            'updated_at': datetime.now()
        }
        update_data.update(data)
        
        return self.db.progress_tracking.update_one(
            {'progress_id': progress_id},
            {'$set': update_data}
        )
    
    def get_daily_progress_summary(self, detox_appointment_id):
        """Get daily progress summary for visualization"""
        progress_entries = self.find_by_detox_appointment(detox_appointment_id)
        
        # Group by day and type
        daily_data = {}
        for entry in progress_entries:
            day = entry['day_number']
            if day not in daily_data:
                daily_data[day] = {
                    'date': entry['date'],
                    'vitals': {},
                    'progress_score': None,
                    'notes': []
                }
            
            if entry['update_type'] == 'vitals':
                daily_data[day]['vitals'].update(entry['vitals'])
            elif entry['update_type'] == 'progress':
                daily_data[day]['progress_score'] = entry['progress_score']
            
            if entry['notes']:
                daily_data[day]['notes'].append(entry['notes'])
        
        return daily_data


class Notification:
    """Model for managing dashboard notifications"""
    
    def __init__(self):
        self.db = get_db_connection()
    
    def create(self, data):
        """Create a new notification"""
        notification_data = {
            'notification_id': generate_notification_id(),
            'user_id': data['user_id'],
            'user_type': data['user_type'],  # 'patient', 'doctor', 'centre'
            'title': data['title'],
            'message': data['message'],
            'type': data['type'],  # 'appointment', 'detox', 'precaution', 'general'
            'priority': data.get('priority', 'medium'),  # 'low', 'medium', 'high', 'urgent'
            'related_id': data.get('related_id'),  # appointment_id, detox_appointment_id, etc.
            'is_read': False,
            'created_at': datetime.now(),
            'expires_at': data.get('expires_at')  # Optional expiration date
        }
        return self.db.notifications.insert_one(notification_data)
    
    def find_by_user(self, user_id, user_type, limit=50):
        """Find notifications for a specific user"""
        query = {
            'user_id': user_id,
            'user_type': user_type,
            'is_read': False
        }
        
        # Add expiration filter if expires_at exists
        query['$or'] = [
            {'expires_at': {'$exists': False}},
            {'expires_at': None},
            {'expires_at': {'$gt': datetime.now()}}
        ]
        
        return list(self.db.notifications.find(query)
                   .sort('created_at', -1)
                   .limit(limit))
    
    def mark_as_read(self, notification_id, user_id):
        """Mark a notification as read"""
        return self.db.notifications.update_one(
            {
                'notification_id': notification_id,
                'user_id': user_id
            },
            {'$set': {'is_read': True}}
        )
    
    def mark_all_as_read(self, user_id, user_type):
        """Mark all notifications as read for a user"""
        return self.db.notifications.update_many(
            {
                'user_id': user_id,
                'user_type': user_type,
                'is_read': False
            },
            {'$set': {'is_read': True}}
        )
    
    def get_unread_count(self, user_id, user_type):
        """Get count of unread notifications"""
        query = {
            'user_id': user_id,
            'user_type': user_type,
            'is_read': False
        }
        
        # Add expiration filter
        query['$or'] = [
            {'expires_at': {'$exists': False}},
            {'expires_at': None},
            {'expires_at': {'$gt': datetime.now()}}
        ]
        
        return self.db.notifications.count_documents(query)
    
    def create_bulk_notifications(self, notifications_data):
        """Create multiple notifications at once"""
        notifications = []
        for data in notifications_data:
            notification_data = {
                'notification_id': generate_notification_id(),
                'user_id': data['user_id'],
                'user_type': data['user_type'],
                'title': data['title'],
                'message': data['message'],
                'type': data['type'],
                'priority': data.get('priority', 'medium'),
                'related_id': data.get('related_id'),
                'is_read': False,
                'created_at': datetime.now(),
                'expires_at': data.get('expires_at')
            }
            notifications.append(notification_data)
        
        if notifications:
            return self.db.notifications.insert_many(notifications)
        return None
