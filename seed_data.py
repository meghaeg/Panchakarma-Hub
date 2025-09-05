#!/usr/bin/env python3
"""
Seed data script for Panchakarma Therapy Management Portal
This script populates the database with sample data for testing
"""

from datetime import datetime, timedelta
from models import Patient, Centre, Doctor, Appointment, Feedback, Admin
from utils import get_db_connection
import random

def create_sample_data():
    """Create sample data for all collections"""
    
    # Initialize models
    admin = Admin()
    patient = Patient()
    centre = Centre()
    doctor = Doctor()
    appointment = Appointment()
    feedback = Feedback()
    
    print("Creating sample data for Panchakarma Portal...")
    
    # 1. Create default admin
    print("Creating admin user...")
    admin.create_default_admin()
    
    # 2. Create sample centres
    print("Creating sample centres...")
    centres_data = [
        {
            'centre_id': 'CEN20241001001',
            'name': 'Kerala Ayurvedic Healing Center',
            'email': 'info@keralaayurveda.com',
            'phone': '+91 9876543210',
            'address': 'Ayurveda Lane, Fort Kochi',
            'city': 'Kochi',
            'state': 'Kerala',
            'pincode': '682001',
            'nabh_accredited': True,
            'license_number': 'KER/AYU/2024/001',
            'password': 'centre123'
        },
        {
            'centre_id': 'CEN20241001002',
            'name': 'Rishikesh Panchakarma Wellness Resort',
            'email': 'contact@rishikeshpanchakarma.com',
            'phone': '+91 9876543211',
            'address': 'Yoga Capital Road, Rishikesh',
            'city': 'Rishikesh',
            'state': 'Uttarakhand',
            'pincode': '249201',
            'nabh_accredited': True,
            'license_number': 'UTK/AYU/2024/002',
            'password': 'centre123'
        },
        {
            'centre_id': 'CEN20241001003',
            'name': 'Bangalore Traditional Ayurveda Hospital',
            'email': 'admin@bangaloreayurveda.com',
            'phone': '+91 9876543212',
            'address': 'MG Road, Bangalore',
            'city': 'Bangalore',
            'state': 'Karnataka',
            'pincode': '560001',
            'nabh_accredited': False,
            'license_number': 'KAR/AYU/2024/003',
            'password': 'centre123'
        },
        {
            'centre_id': 'CEN20241001004',
            'name': 'Pune Holistic Health Center',
            'email': 'info@puneholistic.com',
            'phone': '+91 9876543213',
            'address': 'FC Road, Pune',
            'city': 'Pune',
            'state': 'Maharashtra',
            'pincode': '411004',
            'nabh_accredited': True,
            'license_number': 'MAH/AYU/2024/004',
            'password': 'centre123'
        }
    ]
    
    created_centres = []
    for centre_data in centres_data:
        result = centre.create(centre_data)
        if result:
            # Approve first 3 centres
            if len(created_centres) < 3:
                db = get_db_connection()
                db.centres.update_one(
                    {'centre_id': centre_data['centre_id']},
                    {'$set': {'status': 'approved', 'approved_by': 'ADMIN001', 'approved_at': datetime.now()}}
                )
            created_centres.append(centre_data['centre_id'])
    
    print(f"Created {len(created_centres)} centres")
    
    # 3. Create sample doctors
    print("Creating sample doctors...")
    doctors_data = [
        {
            'doctor_id': 'DOC20241001001',
            'centre_id': 'CEN20241001001',
            'name': 'Rajesh Kumar',
            'email': 'dr.rajesh@keralaayurveda.com',
            'phone': '+91 9876543220',
            'specialization': 'Panchakarma Specialist',
            'experience': 15,
            'qualification': 'BAMS, MD (Panchakarma)',
            'license_number': 'DOC/KER/001',
            'password': 'doctor123'
        },
        {
            'doctor_id': 'DOC20241001002',
            'centre_id': 'CEN20241001001',
            'name': 'Priya Nair',
            'email': 'dr.priya@keralaayurveda.com',
            'phone': '+91 9876543221',
            'specialization': 'Kayachikitsa',
            'experience': 12,
            'qualification': 'BAMS, MD (Kayachikitsa)',
            'license_number': 'DOC/KER/002',
            'password': 'doctor123'
        },
        {
            'doctor_id': 'DOC20241001003',
            'centre_id': 'CEN20241001002',
            'name': 'Amit Sharma',
            'email': 'dr.amit@rishikeshpanchakarma.com',
            'phone': '+91 9876543222',
            'specialization': 'Panchakarma Specialist',
            'experience': 18,
            'qualification': 'BAMS, MD (Panchakarma)',
            'license_number': 'DOC/UTK/001',
            'password': 'doctor123'
        },
        {
            'doctor_id': 'DOC20241001004',
            'centre_id': 'CEN20241001003',
            'name': 'Sunita Reddy',
            'email': 'dr.sunita@bangaloreayurveda.com',
            'phone': '+91 9876543223',
            'specialization': 'Prasuti Tantra',
            'experience': 10,
            'qualification': 'BAMS, MD (Prasuti Tantra)',
            'license_number': 'DOC/KAR/001',
            'password': 'doctor123'
        }
    ]
    
    created_doctors = []
    for doctor_data in doctors_data:
        result = doctor.create(doctor_data)
        if result:
            created_doctors.append(doctor_data['doctor_id'])
    
    print(f"Created {len(created_doctors)} doctors")
    
    # 4. Create sample patients
    print("Creating sample patients...")
    patients_data = [
        {
            'patient_id': 'PAT20241001001',
            'aadhar': '123456789012',
            'name': 'Arjun Patel',
            'age': 35,
            'dob': '1989-05-15',
            'email': 'arjun.patel@email.com',
            'phone': '+91 9876543230',
            'address': '123 Gandhi Road, Mumbai',
            'blood_group': 'O+',
            'health_issues': 'Chronic back pain, stress',
            'medications': 'Paracetamol as needed',
            'password': 'patient123'
        },
        {
            'patient_id': 'PAT20241001002',
            'aadhar': '123456789013',
            'name': 'Meera Singh',
            'age': 42,
            'dob': '1982-08-22',
            'email': 'meera.singh@email.com',
            'phone': '+91 9876543231',
            'address': '456 Nehru Street, Delhi',
            'blood_group': 'A+',
            'health_issues': 'Arthritis, high blood pressure',
            'medications': 'Amlodipine 5mg daily',
            'password': 'patient123'
        },
        {
            'patient_id': 'PAT20241001003',
            'aadhar': '123456789014',
            'name': 'Vikram Joshi',
            'age': 28,
            'dob': '1996-12-10',
            'email': 'vikram.joshi@email.com',
            'phone': '+91 9876543232',
            'address': '789 MG Road, Pune',
            'blood_group': 'B+',
            'health_issues': 'Digestive issues, anxiety',
            'medications': 'None',
            'password': 'patient123'
        },
        {
            'patient_id': 'PAT20241001004',
            'aadhar': '123456789015',
            'name': 'Kavya Menon',
            'age': 31,
            'dob': '1993-03-18',
            'email': 'kavya.menon@email.com',
            'phone': '+91 9876543233',
            'address': '321 Beach Road, Chennai',
            'blood_group': 'AB+',
            'health_issues': 'Migraine, insomnia',
            'medications': 'Sumatriptan as needed',
            'password': 'patient123'
        }
    ]
    
    created_patients = []
    for patient_data in patients_data:
        result = patient.create(patient_data)
        if result:
            created_patients.append(patient_data['patient_id'])
    
    print(f"Created {len(created_patients)} patients")
    
    # 5. Create sample appointments
    print("Creating sample appointments...")
    therapy_types = [
        'Panchakarma Full', 'Panchakarma Short', 'Abhyanga', 
        'Shirodhara', 'Udvartana', 'Nasya', 'Basti'
    ]
    
    statuses = ['booked', 'confirmed', 'in_progress', 'completed']
    
    appointments_data = []
    for i in range(10):
        appointment_date = datetime.now() - timedelta(days=random.randint(1, 30))
        appointments_data.append({
            'appointment_id': f'APT2024100100{i+1}',
            'patient_id': random.choice(created_patients),
            'centre_id': random.choice(created_centres[:3]),  # Only approved centres
            'doctor_id': random.choice(created_doctors) if random.choice([True, False]) else None,
            'therapy_type': random.choice(therapy_types),
            'appointment_date': appointment_date,
            'time_slot': random.choice(['09:00-10:00', '10:00-11:00', '14:00-15:00', '15:00-16:00']),
            'notes': f'Sample appointment {i+1} notes'
        })
    
    created_appointments = []
    for apt_data in appointments_data:
        result = appointment.create(apt_data)
        if result:
            created_appointments.append(apt_data['appointment_id'])
            
            # Add some progress notes and vitals for completed appointments
            if random.choice([True, False]):
                db = get_db_connection()
                
                # Add sample vitals
                sample_vitals = []
                for day in range(1, random.randint(3, 8)):
                    vital = {
                        'date': apt_data['appointment_date'] + timedelta(days=day),
                        'bp_systolic': random.randint(110, 140),
                        'bp_diastolic': random.randint(70, 90),
                        'blood_sugar': random.randint(80, 120),
                        'notes': f'Day {day} vitals recorded'
                    }
                    sample_vitals.append(vital)
                
                # Add sample progress notes
                sample_progress = []
                for day in range(1, len(sample_vitals) + 1):
                    progress = {
                        'date': apt_data['appointment_date'] + timedelta(days=day),
                        'notes': f'Day {day}: Patient showing good response to treatment. Energy levels improved.',
                        'improvement_score': random.randint(6, 9)
                    }
                    sample_progress.append(progress)
                
                # Update appointment with sample data
                update_data = {
                    'status': random.choice(statuses),
                    'vitals': sample_vitals,
                    'progress_notes': sample_progress
                }
                
                # Add therapy summary for completed appointments
                if update_data['status'] == 'completed':
                    update_data['therapy_summary'] = {
                        'completion_date': apt_data['appointment_date'] + timedelta(days=len(sample_vitals)),
                        'summary': 'Patient responded well to treatment. Significant improvement in symptoms observed.',
                        'recommendations': 'Continue with prescribed diet and lifestyle changes. Follow-up after 3 months.',
                        'next_session_date': (apt_data['appointment_date'] + timedelta(days=90)).strftime('%Y-%m-%d')
                    }
                
                db.appointments.update_one(
                    {'appointment_id': apt_data['appointment_id']},
                    {'$set': update_data}
                )
    
    print(f"Created {len(created_appointments)} appointments")
    
    # 6. Create sample feedback
    print("Creating sample feedback...")
    feedback_data = [
        {
            'patient_id': 'PAT20241001001',
            'appointment_id': 'APT20241001001',
            'feedback_type': 'doctor',
            'target_id': 'DOC20241001001',
            'rating': 5,
            'comments': 'Excellent treatment! Dr. Rajesh was very knowledgeable and caring.'
        },
        {
            'patient_id': 'PAT20241001002',
            'appointment_id': 'APT20241001002',
            'feedback_type': 'centre',
            'target_id': 'CEN20241001001',
            'rating': 4,
            'comments': 'Good facilities and clean environment. Staff was helpful.'
        },
        {
            'patient_id': 'PAT20241001003',
            'appointment_id': 'APT20241001003',
            'feedback_type': 'centre',
            'target_id': 'CEN20241001002',
            'rating': 2,
            'comments': 'Treatment was okay but facilities need improvement. Long waiting times.'
        }
    ]
    
    created_feedback = 0
    for fb_data in feedback_data:
        result = feedback.create(fb_data)
        if result:
            created_feedback += 1
    
    print(f"Created {created_feedback} feedback entries")
    
    print("\n" + "="*50)
    print("SAMPLE DATA CREATION COMPLETED!")
    print("="*50)
    print("\nLogin Credentials:")
    print("\n1. ADMIN LOGIN:")
    print("   Email: admin@ayush.gov.in")
    print("   Password: admin123")
    
    print("\n2. PATIENT LOGINS:")
    for i, patient_data in enumerate(patients_data, 1):
        print(f"   Patient {i}: Aadhar: {patient_data['aadhar']}, Password: patient123")
    
    print("\n3. CENTRE LOGINS:")
    for i, centre_data in enumerate(centres_data, 1):
        print(f"   Centre {i}: Email: {centre_data['email']}, Password: centre123")
    
    print("\n4. DOCTOR LOGINS:")
    for i, doctor_data in enumerate(doctors_data, 1):
        print(f"   Doctor {i}: Email: {doctor_data['email']}, Password: doctor123")
    
    print("\nNOTE: Make sure to update email credentials in email_service.py for email notifications to work.")
    print("="*50)

if __name__ == "__main__":
    create_sample_data()
