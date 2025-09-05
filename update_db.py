#!/usr/bin/env python3
"""
Database update script for Panchakarma Portal
This script deletes existing centres and doctors, then adds 5 new centres with 2 doctors each
"""

from models import get_db_connection, Centre, Doctor
from datetime import datetime
import os

def clear_database():
    """Remove all centres, doctors, and related data"""
    db = get_db_connection()
    
    # Delete all related data first
    db.appointments.delete_many({})
    db.doctors.delete_many({})
    db.centres.delete_many({})
    
    print("Cleared all centres, doctors, and related data")

def create_sample_centres():
    """Create 5 sample centres with 2 doctors each"""
    centres = [
        {
            'centre_id': 'CEN20240905001',
            'name': 'AyurVeda Wellness Center',
            'email': 'info@ayurvedawellness.com',
            'phone': '+91 9876543201',
            'address': '123 Green Park, Near Metro Station',
            'city': 'Delhi',
            'state': 'Delhi',
            'pincode': '110016',
            'nabh_accredited': True,
            'license_number': 'DL/AYU/2025/001',
            'password': 'centre123',
            'status': 'approved',
            'approved_by': 'ADMIN001',
            'approved_at': datetime.now(),
            'doctors': [
                {
                    'doctor_id': 'DOC20240905001',
                    'name': 'Dr. Rajesh Sharma',
                    'email': 'dr.rajesh@ayurvedawellness.com',
                    'phone': '+91 9876543202',
                    'specialization': 'Panchakarma Therapy',
                    'qualification': 'MD (Ayurveda), Panchakarma Specialist',
                    'experience': 12,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Monday', 'Wednesday', 'Friday'],
                    'available_sessions': ['09:00-12:00', '14:00-17:00']
                },
                {
                    'doctor_id': 'DOC20240905002',
                    'name': 'Dr. Priya Patel',
                    'email': 'dr.priya@ayurvedawellness.com',
                    'phone': '+91 9876543203',
                    'specialization': 'Kaya Chikitsa',
                    'qualification': 'BAMS, PG Diploma in Panchakarma',
                    'experience': 8,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Tuesday', 'Thursday', 'Saturday'],
                    'available_sessions': ['10:00-13:00', '15:00-18:00']
                }
            ]
        },
        {
            'centre_id': 'CEN20240905002',
            'name': 'Prakruti Ayurveda Hospital',
            'email': 'care@prakrutiayurveda.com',
            'phone': '+91 9876543204',
            'address': '456 MG Road, Shivaji Nagar',
            'city': 'Pune',
            'state': 'Maharashtra',
            'pincode': '411005',
            'nabh_accredited': True,
            'license_number': 'MH/AYU/2025/002',
            'password': 'centre123',
            'status': 'approved',
            'approved_by': 'ADMIN001',
            'approved_at': datetime.now(),
            'doctors': [
                {
                    'doctor_id': 'DOC20240905003',
                    'name': 'Dr. Amit Deshpande',
                    'email': 'dr.amit@prakrutiayurveda.com',
                    'phone': '+91 9876543205',
                    'specialization': 'Rasayana Therapy',
                    'qualification': 'MD (Ayurveda), PhD in Rasayana',
                    'experience': 15,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Monday', 'Wednesday', 'Friday'],
                    'available_sessions': ['09:00-12:00', '14:00-17:00']
                },
                {
                    'doctor_id': 'DOC20240905004',
                    'name': 'Dr. Meera Joshi',
                    'email': 'dr.meera@prakrutiayurveda.com',
                    'phone': '+91 9876543206',
                    'specialization': 'Stree Roga & Prasuti Tantra',
                    'qualification': 'BAMS, MS (Ay. Samhita)',
                    'experience': 10,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Tuesday', 'Thursday', 'Saturday'],
                    'available_sessions': ['10:00-13:00', '15:00-18:00']
                }
            ]
        },
        {
            'centre_id': 'CEN20240905003',
            'name': 'Swasthya Ayurvedic Center',
            'email': 'contact@swasthyaayur.com',
            'phone': '+91 9876543207',
            'address': '789 Residency Road',
            'city': 'Bangalore',
            'state': 'Karnataka',
            'pincode': '560025',
            'nabh_accredited': False,
            'license_number': 'KA/AYU/2025/003',
            'password': 'centre123',
            'status': 'approved',
            'approved_by': 'ADMIN001',
            'approved_at': datetime.now(),
            'doctors': [
                {
                    'doctor_id': 'DOC20240905005',
                    'name': 'Dr. Arjun Reddy',
                    'email': 'dr.arjun@swasthyaayur.com',
                    'phone': '+91 9876543208',
                    'specialization': 'Shalya Tantra',
                    'qualification': 'MS (Ay. Surgery)',
                    'experience': 9,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Monday', 'Wednesday', 'Friday'],
                    'available_sessions': ['09:00-12:00', '14:00-17:00']
                },
                {
                    'doctor_id': 'DOC20240905006',
                    'name': 'Dr. Ananya Iyer',
                    'email': 'dr.ananya@swasthyaayur.com',
                    'phone': '+91 9876543209',
                    'specialization': 'Kaumarabhritya',
                    'qualification': 'MD (Ay. Kaumarabhritya)',
                    'experience': 7,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Tuesday', 'Thursday', 'Saturday'],
                    'available_sessions': ['10:00-13:00', '15:00-18:00']
                }
            ]
        },
        {
            'centre_id': 'CEN20240905004',
            'name': 'Dhanvantari Ayurveda',
            'email': 'info@dhanvantariayur.com',
            'phone': '+91 9876543210',
            'address': '321 Temple Road, Mylapore',
            'city': 'Chennai',
            'state': 'Tamil Nadu',
            'pincode': '600004',
            'nabh_accredited': True,
            'license_number': 'TN/AYU/2025/004',
            'password': 'centre123',
            'status': 'approved',
            'approved_by': 'ADMIN001',
            'approved_at': datetime.now(),
            'doctors': [
                {
                    'doctor_id': 'DOC20240905007',
                    'name': 'Dr. Karthik Sundaram',
                    'email': 'dr.karthik@dhanvantariayur.com',
                    'phone': '+91 9876543211',
                    'specialization': 'Kayachikitsa',
                    'qualification': 'MD (Ay. Kayachikitsa)',
                    'experience': 11,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Monday', 'Wednesday', 'Friday'],
                    'available_sessions': ['09:00-12:00', '14:00-17:00']
                },
                {
                    'doctor_id': 'DOC20240905008',
                    'name': 'Dr. Nandini Venkatesh',
                    'email': 'dr.nandini@dhanvantariayur.com',
                    'phone': '+91 9876543212',
                    'specialization': 'Manas Roga',
                    'qualification': 'MD (Ay. Manas Roga)',
                    'experience': 6,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Tuesday', 'Thursday', 'Saturday'],
                    'available_sessions': ['10:00-13:00', '15:00-18:00']
                }
            ]
        },
        {
            'centre_id': 'CEN20240905005',
            'name': 'AyurSouk Herbal Center',
            'email': 'hello@ayursouk.com',
            'phone': '+91 9876543213',
            'address': '567 Park Street, Camac Street',
            'city': 'Kolkata',
            'state': 'West Bengal',
            'pincode': '700017',
            'nabh_accredited': True,
            'license_number': 'WB/AYU/2025/005',
            'password': 'centre123',
            'status': 'approved',
            'approved_by': 'ADMIN001',
            'approved_at': datetime.now(),
            'doctors': [
                {
                    'doctor_id': 'DOC20240905009',
                    'name': 'Dr. Debashish Banerjee',
                    'email': 'dr.debashish@ayursouk.com',
                    'phone': '+91 9876543214',
                    'specialization': 'Panchakarma & Marma',
                    'qualification': 'MD (Ay. Panchakarma)',
                    'experience': 13,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Monday', 'Wednesday', 'Friday'],
                    'available_sessions': ['09:00-12:00', '14:00-17:00']
                },
                {
                    'doctor_id': 'DOC20240905010',
                    'name': 'Dr. Indrani Das',
                    'email': 'dr.indrani@ayursouk.com',
                    'phone': '+91 9876543215',
                    'specialization': 'Dravyaguna',
                    'qualification': 'MD (Ay. Dravyaguna)',
                    'experience': 8,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Tuesday', 'Thursday', 'Saturday'],
                    'available_sessions': ['10:00-13:00', '15:00-18:00']
                }
            ]
        }
    ]
    
    # Initialize models
    centre_model = Centre()
    doctor_model = Doctor()
    
    # Create centres and doctors
    created_centres = 0
    created_doctors = 0
    
    for centre in centres:
        # Extract doctors before removing them from centre data
        doctors = centre.pop('doctors')
        
        # Create centre
        if centre_model.create(centre):
            created_centres += 1
            
            # Create doctors for this centre
            for doc in doctors:
                doc['centre_id'] = centre['centre_id']
                if doctor_model.create(doc):
                    created_doctors += 1
    
    print(f"Successfully created {created_centres} centres and {created_doctors} doctors")

if __name__ == "__main__":
    print("Starting database update...")
    
    # Clear existing data
    clear_database()
    
    # Create new sample data
    create_sample_centres()
    
    print("\nDatabase update completed successfully!")
