#!/usr/bin/env python3
"""
Simple database connection test
"""
import os
from dotenv import load_dotenv
from utils import get_db_connection

# Load environment variables
load_dotenv()

def test_db_connection():
    """Test database connection"""
    try:
        print("🔍 Testing database connection...")
        
        # Test basic connection
        db = get_db_connection()
        print("✅ Database connection successful")
        
        # Test collections
        collections = db.list_collection_names()
        print(f"📊 Available collections: {collections}")
        
        # Test doctor collection
        doctor_count = db.doctors.count_documents({})
        print(f"👨‍⚕️ Total doctors: {doctor_count}")
        
        # Test appointment collection
        appointment_count = db.appointments.count_documents({})
        print(f"📅 Total appointments: {appointment_count}")
        
        # Test bed collection
        bed_count = db.beds.count_documents({})
        print(f"🛏️ Total beds: {bed_count}")
        
        print("✅ All database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_db_connection()
