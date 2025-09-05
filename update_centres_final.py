"""
Script to update centres and doctors in the database using the application's models.
This ensures we're using the exact same methods as the main application.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Centre, Doctor

def clear_existing_data():
    """Remove all existing centres and doctors"""
    db = get_db_connection()
    
    # Drop collections
    db.centres.drop()
    db.doctors.drop()
    
    # Recreate indexes if needed
    db.centres.create_index("centre_id", unique=True)
    db.doctors.create_index("doctor_id", unique=True)
    
    print("✅ Cleared existing centres and doctors")

def create_sample_centres():
    """Create sample centres with doctors using the application's models"""
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
            'approved_at': datetime.utcnow(),
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
            'approved_at': datetime.utcnow(),
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
            'address': '789 Residency Road, Bangalore',
            'city': 'Bangalore',
            'state': 'Karnataka',
            'pincode': '560025',
            'nabh_accredited': False,
            'license_number': 'KA/AYU/2025/003',
            'password': 'centre123',
            'status': 'approved',
            'approved_by': 'ADMIN001',
            'approved_at': datetime.utcnow(),
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
            'address': '321 Temple Road, Chennai',
            'city': 'Chennai',
            'state': 'Tamil Nadu',
            'pincode': '600004',
            'nabh_accredited': True,
            'license_number': 'TN/AYU/2025/004',
            'password': 'centre123',
            'status': 'approved',
            'approved_by': 'ADMIN001',
            'approved_at': datetime.utcnow(),
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
            'address': '567 Park Street, Kolkata',
            'city': 'Kolkata',
            'state': 'West Bengal',
            'pincode': '700017',
            'nabh_accredited': True,
            'license_number': 'WB/AYU/2025/005',
            'password': 'centre123',
            'status': 'approved',
            'approved_by': 'ADMIN001',
            'approved_at': datetime.utcnow(),
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
    created_centres = 0
    created_doctors = 0
    
    for centre_data in centres_data:
        # Extract doctors before removing from centre data
        doctors = centre_data.pop('doctors')
        
        # Create centre
        print(f"\n🏥 Creating centre: {centre_data['name']}")
        if centre_model.create(centre_data):
            created_centres += 1
            print(f"   ✅ Centre created successfully")
        else:
            print(f"   ❌ Failed to create centre")
            continue
        
        # Create doctors for this centre
        for doctor_data in doctors:
            doctor_data['centre_id'] = centre_data['centre_id']
            print(f"   👨‍⚕️ Adding doctor: {doctor_data['name']}")
            if doctor_model.create(doctor_data):
                created_doctors += 1
                print(f"      ✅ Doctor added successfully")
            else:
                print(f"      ❌ Failed to add doctor")
    
    print(f"\n✅ Successfully created {created_centres} centres and {created_doctors} doctors")

def get_db_connection():
    """Get database connection using the same method as in utils.py"""
    from pymongo import MongoClient
    
    # Connection string from utils.py
    atlas_connection = "mongodb+srv://meghaeg27_db_user:Megha2711%24@cluster0.hz2o1hb.mongodb.net/panchakarma_portal?retryWrites=true&w=majority"
    
    try:
        client = MongoClient(atlas_connection, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        return client.panchakarma_portal
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None

def main():
    print("🚀 Starting database update...")
    
    # Clear existing data
    if input("⚠️  Clear existing centres and doctors? (y/n): ").lower() == 'y':
        clear_existing_data()
    
    # Create new sample data
    if input("\nCreate new sample centres and doctors? (y/n): ").lower() == 'y':
        create_sample_centres()
    
    print("\n✨ Database update completed!")

if __name__ == "__main__":
    main()
