#!/usr/bin/env python3
"""Test script to debug login issues"""

import sys
import traceback

def test_database_connection():
    """Test database connectivity"""
    try:
        from utils import get_db_connection
        db = get_db_connection()
        print("✓ Database connection successful")
        
        collections = db.list_collection_names()
        print(f"Collections found: {collections}")
        
        # Check if we have sample data
        patient_count = db.patients.count_documents({})
        admin_count = db.admins.count_documents({})
        centre_count = db.centres.count_documents({})
        doctor_count = db.doctors.count_documents({})
        
        print(f"Data counts - Patients: {patient_count}, Admins: {admin_count}, Centres: {centre_count}, Doctors: {doctor_count}")
        
        return db
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        traceback.print_exc()
        return None

def test_patient_login():
    """Test patient authentication"""
    try:
        from models import Patient
        patient = Patient()
        
        # Test finding patient by Aadhar
        user = patient.find_by_aadhar('123456789012')
        if user:
            print(f"✓ Patient found: {user['name']}")
            
            # Test password check
            password_valid = patient.check_password('patient123', user['password'])
            print(f"Password check result: {password_valid}")
            
            return True
        else:
            print("✗ Patient not found with Aadhar 123456789012")
            return False
            
    except Exception as e:
        print(f"✗ Patient login test failed: {e}")
        traceback.print_exc()
        return False

def test_admin_login():
    """Test admin authentication"""
    try:
        from models import Admin
        admin = Admin()
        
        user = admin.find_by_email('admin@ayush.gov.in')
        if user:
            print(f"✓ Admin found: {user['name']}")
            
            password_valid = admin.check_password('admin123', user['password'])
            print(f"Admin password check result: {password_valid}")
            
            return True
        else:
            print("✗ Admin not found")
            return False
            
    except Exception as e:
        print(f"✗ Admin login test failed: {e}")
        traceback.print_exc()
        return False

def create_sample_data_if_missing():
    """Create sample data if collections are empty"""
    try:
        from seed_data import create_sample_data
        print("Creating sample data...")
        create_sample_data()
        print("✓ Sample data created successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to create sample data: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Panchakarma Portal Login Debug ===")
    
    # Test database connection
    db = test_database_connection()
    if not db:
        sys.exit(1)
    
    # Check if we need to create sample data
    if db.patients.count_documents({}) == 0:
        print("\nNo sample data found. Creating...")
        if not create_sample_data_if_missing():
            sys.exit(1)
    
    print("\n=== Testing Authentication ===")
    
    # Test patient login
    print("\n--- Patient Login Test ---")
    test_patient_login()
    
    # Test admin login
    print("\n--- Admin Login Test ---")
    test_admin_login()
    
    print("\n=== Debug Complete ===")
