"""Script to manually insert test data into MongoDB"""

from pymongo import MongoClient
from datetime import datetime
import bcrypt

def get_hashed_password(password):
    """Hash a password for storing in the database"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def connect_to_mongodb():
    """Connect to MongoDB and return the database object"""
    try:
        # Connection string from utils.py
        atlas_connection = "mongodb+srv://meghaeg27_db_user:Megha2711%24@cluster0.hz2o1hb.mongodb.net/panchakarma_portal?retryWrites=true&w=majority"
        client = MongoClient(atlas_connection, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB")
        return client.panchakarma_portal
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return None

def insert_sample_data():
    """Insert sample centres and doctors into the database"""
    db = connect_to_mongodb()
    if not db:
        return

    # Clear existing data
    db.centres.delete_many({})
    db.doctors.delete_many({})
    print("\n🧹 Cleared existing centres and doctors")

    # Sample centre data
    centres = [
        {
            'centre_id': 'CEN001',
            'name': 'AyurVeda Wellness Center',
            'email': 'info@ayurvedawellness.com',
            'phone': '+91 9876543201',
            'password': get_hashed_password('centre123'),
            'status': 'approved',
            'approved_by': 'ADMIN001',
            'approved_at': datetime.utcnow()
        },
        {
            'centre_id': 'CEN002',
            'name': 'Prakruti Ayurveda Hospital',
            'email': 'care@prakrutiayurveda.com',
            'phone': '+91 9876543204',
            'password': get_hashed_password('centre123'),
            'status': 'approved',
            'approved_by': 'ADMIN001',
            'approved_at': datetime.utcnow()
        }
    ]

    # Sample doctor data
    doctors = [
        {
            'doctor_id': 'DOC001',
            'centre_id': 'CEN001',
            'name': 'Dr. Rajesh Sharma',
            'email': 'dr.rajesh@ayurvedawellness.com',
            'phone': '+91 9876543202',
            'password': get_hashed_password('doctor123'),
            'status': 'active'
        },
        {
            'doctor_id': 'DOC002',
            'centre_id': 'CEN001',
            'name': 'Dr. Priya Patel',
            'email': 'dr.priya@ayurvedawellness.com',
            'phone': '+91 9876543203',
            'password': get_hashed_password('doctor123'),
            'status': 'active'
        },
        {
            'doctor_id': 'DOC003',
            'centre_id': 'CEN002',
            'name': 'Dr. Amit Deshpande',
            'email': 'dr.amit@prakrutiayurveda.com',
            'phone': '+91 9876543205',
            'password': get_hashed_password('doctor123'),
            'status': 'active'
        },
        {
            'doctor_id': 'DOC004',
            'centre_id': 'CEN002',
            'name': 'Dr. Meera Joshi',
            'email': 'dr.meera@prakrutiayurveda.com',
            'phone': '+91 9876543206',
            'password': get_hashed_password('doctor123'),
            'status': 'active'
        }
    ]

    # Insert data
    result_centres = db.centres.insert_many(centres)
    result_doctors = db.doctors.insert_many(doctors)

    print(f"\n✅ Inserted {len(result_centres.inserted_ids)} centres and {len(result_doctors.inserted_ids)} doctors")
    print("\nSample login credentials:")
    print("Centres:")
    for centre in centres:
        print(f"  Email: {centre['email']}, Password: centre123")
    
    print("\nDoctors:")
    for doctor in doctors:
        print(f"  Email: {doctor['email']}, Password: doctor123")

if __name__ == "__main__":
    print("🚀 Starting manual data insertion...")
    insert_sample_data()
