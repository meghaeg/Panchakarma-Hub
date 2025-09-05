#!/usr/bin/env python3
"""
Update Centres and Doctors in the database
This script deletes all existing centres and doctors, then adds 5 new centres with 2 doctors each
"""

from models import Centre, Doctor, get_db_connection
from datetime import datetime
import random

def delete_all_centres_and_doctors():
    """Delete all existing centres and doctors from the database"""
    db = get_db_connection()
    
    # Delete all appointments first (to maintain referential integrity)
    db.appointments.delete_many({})
    
    # Delete all doctors
    db.doctors.delete_many({})
    
    # Delete all centres
    result = db.centres.delete_many({})
    
    print(f"Deleted {result.deleted_count} centres and all associated doctors and appointments")

def generate_centre_id(index):
    """Generate a unique centre ID"""
    return f"CEN{datetime.now().strftime('%Y%m%d')}{index:03d}"

def generate_doctor_id(index):
    """Generate a unique doctor ID"""
    return f"DOC{datetime.now().strftime('%Y%m%d')}{index:03d}"

def create_centres_and_doctors():
    """Create 5 new centres with 2 doctors each"""
    centre = Centre()
    doctor = Doctor()
    
    # Sample data for 5 centres with their respective doctors
    centres_data = [
        {
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
            'doctors': [
                {
                    'name': 'Dr. Rajesh Sharma',
                    'email': 'dr.rajesh@ayurvedawellness.com',
                    'phone': '+91 9876543202',
                    'specialization': 'Panchakarma Therapy',
                    'qualification': 'MD (Ayurveda), Panchakarma Specialist',
                    'experience': 12,
                    'password': 'doctor123'
                },
                {
                    'name': 'Dr. Priya Patel',
                    'email': 'dr.priya@ayurvedawellness.com',
                    'phone': '+91 9876543203',
                    'specialization': 'Kaya Chikitsa',
                    'qualification': 'BAMS, PG Diploma in Panchakarma',
                    'experience': 8,
                    'password': 'doctor123'
                }
            ]
        },
        {
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
            'doctors': [
                {
                    'name': 'Dr. Amit Deshpande',
                    'email': 'dr.amit@prakrutiayurveda.com',
                    'phone': '+91 9876543205',
                    'specialization': 'Rasayana Therapy',
                    'qualification': 'MD (Ayurveda), PhD in Rasayana',
                    'experience': 15,
                    'password': 'doctor123'
                },
                {
                    'name': 'Dr. Meera Joshi',
                    'email': 'dr.meera@prakrutiayurveda.com',
                    'phone': '+91 9876543206',
                    'specialization': 'Stree Roga & Prasuti Tantra',
                    'qualification': 'BAMS, MS (Ay. Samhita)',
                    'experience': 10,
                    'password': 'doctor123'
                }
            ]
        },
        {
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
            'doctors': [
                {
                    'name': 'Dr. Arjun Reddy',
                    'email': 'dr.arjun@swasthyaayur.com',
                    'phone': '+91 9876543208',
                    'specialization': 'Shalya Tantra',
                    'qualification': 'MS (Ay. Surgery)',
                    'experience': 9,
                    'password': 'doctor123'
                },
                {
                    'name': 'Dr. Ananya Iyer',
                    'email': 'dr.ananya@swasthyaayur.com',
                    'phone': '+91 9876543209',
                    'specialization': 'Kaumarabhritya',
                    'qualification': 'MD (Ay. Kaumarabhritya)',
                    'experience': 7,
                    'password': 'doctor123'
                }
            ]
        },
        {
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
            'doctors': [
                {
                    'name': 'Dr. Karthik Sundaram',
                    'email': 'dr.karthik@dhanvantariayur.com',
                    'phone': '+91 9876543211',
                    'specialization': 'Kayachikitsa',
                    'qualification': 'MD (Ay. Kayachikitsa)',
                    'experience': 11,
                    'password': 'doctor123'
                },
                {
                    'name': 'Dr. Nandini Venkatesh',
                    'email': 'dr.nandini@dhanvantariayur.com',
                    'phone': '+91 9876543212',
                    'specialization': 'Manas Roga',
                    'qualification': 'MD (Ay. Manas Roga)',
                    'experience': 6,
                    'password': 'doctor123'
                }
            ]
        },
        {
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
            'doctors': [
                {
                    'name': 'Dr. Debashish Banerjee',
                    'email': 'dr.debashish@ayursouk.com',
                    'phone': '+91 9876543214',
                    'specialization': 'Panchakarma & Marma',
                    'qualification': 'MD (Ay. Panchakarma)',
                    'experience': 13,
                    'password': 'doctor123'
                },
                {
                    'name': 'Dr. Indrani Das',
                    'email': 'dr.indrani@ayursouk.com',
                    'phone': '+91 9876543215',
                    'specialization': 'Dravyaguna',
                    'qualification': 'MD (Ay. Dravyaguna)',
                    'experience': 8,
                    'password': 'doctor123'
                }
            ]
        }
    ]
    
    # Create centres and doctors
    created_centres = []
    created_doctors = []
    
    for i, centre_data in enumerate(centres_data, 1):
        # Create centre
        centre_id = generate_centre_id(i)
        centre_info = {
            'centre_id': centre_id,
            'name': centre_data['name'],
            'email': centre_data['email'],
            'phone': centre_data['phone'],
            'address': centre_data['address'],
            'city': centre_data['city'],
            'state': centre_data['state'],
            'pincode': centre_data['pincode'],
            'nabh_accredited': centre_data['nabh_accredited'],
            'license_number': centre_data['license_number'],
            'password': centre_data['password'],
            'status': 'approved',
            'approved_by': 'ADMIN001',
            'approved_at': datetime.now()
        }
        
        # Create centre in database
        centre.create(centre_info)
        created_centres.append(centre_id)
        
        # Create doctors for this centre
        for j, doc_data in enumerate(centre_data['doctors'], 1):
            doctor_id = generate_doctor_id((i-1)*2 + j)
            doctor_info = {
                'doctor_id': doctor_id,
                'centre_id': centre_id,
                'name': doc_data['name'],
                'email': doc_data['email'],
                'phone': doc_data['phone'],
                'specialization': doc_data['specialization'],
                'qualification': doc_data['qualification'],
                'experience': doc_data['experience'],
                'password': doc_data['password'],
                'status': 'active',
                'working_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
                'available_sessions': ['09:00-12:00', '14:00-17:00']
            }
            
            # Create doctor in database
            doctor.create(doctor_info)
            created_doctors.append(doctor_id)
    
    print(f"Successfully created {len(created_centres)} centres and {len(created_doctors)} doctors")
    return created_centres, created_doctors

if __name__ == "__main__":
    print("Starting database update...")
    
    # Delete all existing data
    print("Removing existing data...")
    delete_all_centres_and_doctors()
    
    # Create new centres and doctors
    print("Creating new centres and doctors...")
    centres, doctors = create_centres_and_doctors()
    
    print("\nUpdate completed successfully!")
    print(f"- Total centres created: {len(centres)}")
    print(f"- Total doctors created: {len(doctors)}")
