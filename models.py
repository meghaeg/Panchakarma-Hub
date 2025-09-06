from datetime import datetime
from utils import get_db_connection
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
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
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
            'updated_at': datetime.utcnow()
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
