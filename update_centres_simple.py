from pymongo import MongoClient
from datetime import datetime

def update_database():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['panchakarma']
    
    # Clear existing data
    print("Clearing existing data...")
    db.centers.delete_many({})
    db.doctors.delete_many({})
    db.appointments.delete_many({})
    
    # Sample data for 5 centers with 2 doctors each
    centers = [
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
            'approved_at': datetime.now()
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
            'approved_at': datetime.now()
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
            'approved_at': datetime.now()
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
            'approved_at': datetime.now()
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
            'approved_at': datetime.now()
        }
    ]
    
    # Sample doctors (2 per center)
    doctors = [
        # Doctors for CEN001
        {
            'doctor_id': 'DOC001',
            'centre_id': 'CEN001',
            'name': 'Dr. Rajesh Sharma',
            'email': 'dr.rajesh@ayurvedawellness.com',
            'phone': '+91 9876543202',
            'specialization': 'Panchakarma Therapy',
            'qualification': 'MD (Ayurveda)',
            'experience': 12,
            'password': 'doctor123',
            'status': 'active',
            'working_days': ['Mon', 'Wed', 'Fri'],
            'available_sessions': ['09:00-12:00', '14:00-17:00']
        },
        {
            'doctor_id': 'DOC002',
            'centre_id': 'CEN001',
            'name': 'Dr. Priya Patel',
            'email': 'dr.priya@ayurvedawellness.com',
            'phone': '+91 9876543203',
            'specialization': 'Kaya Chikitsa',
            'qualification': 'BAMS',
            'experience': 8,
            'password': 'doctor123',
            'status': 'active',
            'working_days': ['Tue', 'Thu', 'Sat'],
            'available_sessions': ['10:00-13:00', '15:00-18:00']
        },
        # Doctors for CEN002
        {
            'doctor_id': 'DOC003',
            'centre_id': 'CEN002',
            'name': 'Dr. Amit Deshpande',
            'email': 'dr.amit@prakrutiayurveda.com',
            'phone': '+91 9876543205',
            'specialization': 'Rasayana Therapy',
            'qualification': 'MD (Ayurveda)',
            'experience': 15,
            'password': 'doctor123',
            'status': 'active',
            'working_days': ['Mon', 'Wed', 'Fri'],
            'available_sessions': ['09:00-12:00', '14:00-17:00']
        },
        {
            'doctor_id': 'DOC004',
            'centre_id': 'CEN002',
            'name': 'Dr. Meera Joshi',
            'email': 'dr.meera@prakrutiayurveda.com',
            'phone': '+91 9876543206',
            'specialization': 'Stree Roga',
            'qualification': 'BAMS',
            'experience': 10,
            'password': 'doctor123',
            'status': 'active',
            'working_days': ['Tue', 'Thu', 'Sat'],
            'available_sessions': ['10:00-13:00', '15:00-18:00']
        },
        # Add doctors for remaining centers...
        {
            'doctor_id': 'DOC005',
            'centre_id': 'CEN003',
            'name': 'Dr. Arjun Reddy',
            'email': 'dr.arjun@swasthyaayur.com',
            'phone': '+91 9876543208',
            'specialization': 'Shalya Tantra',
            'qualification': 'MS (Ay. Surgery)',
            'experience': 9,
            'password': 'doctor123',
            'status': 'active',
            'working_days': ['Mon', 'Wed', 'Fri'],
            'available_sessions': ['09:00-12:00', '14:00-17:00']
        },
        {
            'doctor_id': 'DOC006',
            'centre_id': 'CEN003',
            'name': 'Dr. Ananya Iyer',
            'email': 'dr.ananya@swasthyaayur.com',
            'phone': '+91 9876543209',
            'specialization': 'Kaumarabhritya',
            'qualification': 'MD (Ay.)',
            'experience': 7,
            'password': 'doctor123',
            'status': 'active',
            'working_days': ['Tue', 'Thu', 'Sat'],
            'available_sessions': ['10:00-13:00', '15:00-18:00']
        },
        {
            'doctor_id': 'DOC007',
            'centre_id': 'CEN004',
            'name': 'Dr. Karthik Sundaram',
            'email': 'dr.karthik@dhanvantariayur.com',
            'phone': '+91 9876543211',
            'specialization': 'Kayachikitsa',
            'qualification': 'MD (Ay.)',
            'experience': 11,
            'password': 'doctor123',
            'status': 'active',
            'working_days': ['Mon', 'Wed', 'Fri'],
            'available_sessions': ['09:00-12:00', '14:00-17:00']
        },
        {
            'doctor_id': 'DOC008',
            'centre_id': 'CEN004',
            'name': 'Dr. Nandini Venkatesh',
            'email': 'dr.nandini@dhanvantariayur.com',
            'phone': '+91 9876543212',
            'specialization': 'Manas Roga',
            'qualification': 'MD (Ay.)',
            'experience': 6,
            'password': 'doctor123',
            'status': 'active',
            'working_days': ['Tue', 'Thu', 'Sat'],
            'available_sessions': ['10:00-13:00', '15:00-18:00']
        },
        {
            'doctor_id': 'DOC009',
            'centre_id': 'CEN005',
            'name': 'Dr. Debashish Banerjee',
            'email': 'dr.debashish@ayursouk.com',
            'phone': '+91 9876543214',
            'specialization': 'Panchakarma',
            'qualification': 'MD (Ay.)',
            'experience': 13,
            'password': 'doctor123',
            'status': 'active',
            'working_days': ['Mon', 'Wed', 'Fri'],
            'available_sessions': ['09:00-12:00', '14:00-17:00']
        },
        {
            'doctor_id': 'DOC010',
            'centre_id': 'CEN005',
            'name': 'Dr. Indrani Das',
            'email': 'dr.indrani@ayursouk.com',
            'phone': '+91 9876543215',
            'specialization': 'Dravyaguna',
            'qualification': 'MD (Ay.)',
            'experience': 8,
            'password': 'doctor123',
            'status': 'active',
            'working_days': ['Tue', 'Thu', 'Sat'],
            'available_sessions': ['10:00-13:00', '15:00-18:00']
        }
    ]
    
    # Insert centers
    print("Inserting centers...")
    result = db.centers.insert_many(centers)
    print(f"Inserted {len(result.inserted_ids)} centers")
    
    # Insert doctors
    print("Inserting doctors...")
    result = db.doctors.insert_many(doctors)
    print(f"Inserted {len(result.inserted_ids)} doctors")
    
    print("\nDatabase update completed successfully!")
    print("\nSample login credentials:")
    print("Centers:")
    for center in centers:
        print(f"  Email: {center['email']}, Password: {center['password']}")
    
    print("\nDoctors:")
    for doctor in doctors:
        print(f"  Email: {doctor['email']}, Password: {doctor['password']}")

if __name__ == "__main__":
    update_database()
