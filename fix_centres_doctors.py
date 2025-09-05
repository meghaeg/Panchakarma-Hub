"""
Script to fix centres and doctors in the database
1. Drops existing centres and doctors collections
2. Creates 5 new centres with 2 doctors each
3. Uses the same connection and models as the main application
"""

import sys
import os
from datetime import datetime

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Centre, Doctor, get_db_connection

def clear_existing_data():
    """Remove all existing centres and doctors"""
    db = get_db_connection()
    
    # Drop collections
    db.centres.drop()
    db.doctors.drop()
    
    # Recreate indexes if needed
    db.centres.create_index("centre_id", unique=True)
    db.doctors.create_index("doctor_id", unique=True)
    
    print("Cleared existing centres and doctors")

def create_sample_centres():
    """Create 5 sample centres with 2 doctors each"""
    centre_model = Centre()
    doctor_model = Doctor()
    
    # Sample data for centres and doctors
    centres_data = [
        {
            'centre_id': 'CEN001',
            'name': 'AyurVeda Wellness Center',
            'email': 'info@ayurvedawellness.com',
            'phone': '+91 9876543201',
            'address': '123 Green Park, Delhi',
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
                    'doctor_id': 'DOC001',
                    'name': 'Dr. Rajesh Sharma',
                    'email': 'dr.rajesh@ayurvedawellness.com',
                    'phone': '+91 9876543202',
                    'specialization': 'Panchakarma Therapy',
                    'qualification': 'MD (Ayurveda)',
                    'experience': 12,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Monday', 'Wednesday', 'Friday'],
                    'available_sessions': ['09:00-12:00', '14:00-17:00']
                },
                {
                    'doctor_id': 'DOC002',
                    'name': 'Dr. Priya Patel',
                    'email': 'dr.priya@ayurvedawellness.com',
                    'phone': '+91 9876543203',
                    'specialization': 'Kaya Chikitsa',
                    'qualification': 'BAMS',
                    'experience': 8,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Tuesday', 'Thursday', 'Saturday'],
                    'available_sessions': ['10:00-13:00', '15:00-18:00']
                }
            ]
        },
        {
            'centre_id': 'CEN002',
            'name': 'Prakruti Ayurveda Hospital',
            'email': 'care@prakrutiayurveda.com',
            'phone': '+91 9876543204',
            'address': '456 MG Road, Pune',
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
                    'doctor_id': 'DOC003',
                    'name': 'Dr. Amit Deshpande',
                    'email': 'dr.amit@prakrutiayurveda.com',
                    'phone': '+91 9876543205',
                    'specialization': 'Rasayana Therapy',
                    'qualification': 'MD (Ayurveda)',
                    'experience': 15,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Monday', 'Wednesday', 'Friday'],
                    'available_sessions': ['09:00-12:00', '14:00-17:00']
                },
                {
                    'doctor_id': 'DOC004',
                    'name': 'Dr. Meera Joshi',
                    'email': 'dr.meera@prakrutiayurveda.com',
                    'phone': '+91 9876543206',
                    'specialization': 'Stree Roga',
                    'qualification': 'BAMS',
                    'experience': 10,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Tuesday', 'Thursday', 'Saturday'],
                    'available_sessions': ['10:00-13:00', '15:00-18:00']
                }
            ]
        },
        {
            'centre_id': 'CEN003',
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
                    'doctor_id': 'DOC005',
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
                    'doctor_id': 'DOC006',
                    'name': 'Dr. Ananya Iyer',
                    'email': 'dr.ananya@swasthyaayur.com',
                    'phone': '+91 9876543209',
                    'specialization': 'Kaumarabhritya',
                    'qualification': 'MD (Ay.)',
                    'experience': 7,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Tuesday', 'Thursday', 'Saturday'],
                    'available_sessions': ['10:00-13:00', '15:00-18:00']
                }
            ]
        },
        {
            'centre_id': 'CEN004',
            'name': 'Dhanvantari Ayurveda',
            'email': 'info@dhanvantariayur.com',
            'phone': '+91 9876543210',
            'address': '321 Temple Road',
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
                    'doctor_id': 'DOC007',
                    'name': 'Dr. Karthik Sundaram',
                    'email': 'dr.karthik@dhanvantariayur.com',
                    'phone': '+91 9876543211',
                    'specialization': 'Kayachikitsa',
                    'qualification': 'MD (Ay.)',
                    'experience': 11,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Monday', 'Wednesday', 'Friday'],
                    'available_sessions': ['09:00-12:00', '14:00-17:00']
                },
                {
                    'doctor_id': 'DOC008',
                    'name': 'Dr. Nandini Venkatesh',
                    'email': 'dr.nandini@dhanvantariayur.com',
                    'phone': '+91 9876543212',
                    'specialization': 'Manas Roga',
                    'qualification': 'MD (Ay.)',
                    'experience': 6,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Tuesday', 'Thursday', 'Saturday'],
                    'available_sessions': ['10:00-13:00', '15:00-18:00']
                }
            ]
        },
        {
            'centre_id': 'CEN005',
            'name': 'AyurSouk Herbal Center',
            'email': 'hello@ayursouk.com',
            'phone': '+91 9876543213',
            'address': '567 Park Street',
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
                    'doctor_id': 'DOC009',
                    'name': 'Dr. Debashish Banerjee',
                    'email': 'dr.debashish@ayursouk.com',
                    'phone': '+91 9876543214',
                    'specialization': 'Panchakarma',
                    'qualification': 'MD (Ay.)',
                    'experience': 13,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Monday', 'Wednesday', 'Friday'],
                    'available_sessions': ['09:00-12:00', '14:00-17:00']
                },
                {
                    'doctor_id': 'DOC010',
                    'name': 'Dr. Indrani Das',
                    'email': 'dr.indrani@ayursouk.com',
                    'phone': '+91 9876543215',
                    'specialization': 'Dravyaguna',
                    'qualification': 'MD (Ay.)',
                    'experience': 8,
                    'password': 'doctor123',
                    'status': 'active',
                    'working_days': ['Tuesday', 'Thursday', 'Saturday'],
                    'available_sessions': ['10:00-13:00', '15:00-18:00']
                }
            ]
        }
    ]
    
    # Create centres and doctors
    for centre_data in centres_data:
        # Extract doctors before removing from centre data
        doctors = centre_data.pop('doctors')
        
        # Create centre
        print(f"Creating centre: {centre_data['name']}")
        centre_model.create(centre_data)
        
        # Create doctors for this centre
        for doctor_data in doctors:
            doctor_data['centre_id'] = centre_data['centre_id']
            print(f"  Adding doctor: {doctor_data['name']}")
            doctor_model.create(doctor_data)
    
    print("\nSample login credentials:")
    print("Centres:")
    for centre in centres_data:
        print(f"  Email: {centre['email']}, Password: {centre['password']}")
        for doctor in doctors:
            print(f"  Doctor: {doctor['email']}, Password: {doctor['password']}")

def main():
    print("Starting database update...")
    
    # Clear existing data
    clear_existing_data()
    
    # Create new sample data
    create_sample_centres()
    
    print("\nDatabase update completed successfully!")

if __name__ == "__main__":
    main()
