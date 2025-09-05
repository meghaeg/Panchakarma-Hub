#!/usr/bin/env python3
"""Simple script to check MongoDB connection and collections"""

import sys
import pymongo
from pymongo import MongoClient

def main():
    print("🔍 Checking MongoDB connection...")
    
    try:
        # Connection string from utils.py
        uri = "mongodb+srv://meghaeg27_db_user:Megha2711%24@cluster0.hz2o1hb.mongodb.net/panchakarma_portal?retryWrites=true&w=majority"
        
        print("Connecting to MongoDB...")
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        print("Pinging MongoDB...")
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        
        # Get database
        db = client.get_database('panchakarma_portal')
        
        # List collections
        print("\n📂 Collections:")
        for collection_name in db.list_collection_names():
            print(f"- {collection_name}")
        
        # Show counts
        if 'centres' in db.list_collection_names():
            count = db.centres.count_documents({})
            print(f"\n🏥 Centres: {count} documents")
            
            # Show first few centres
            print("\nSample centres:")
            for doc in db.centres.find().limit(2):
                print(f"- {doc.get('name')} (ID: {doc.get('_id')})")
        
        if 'doctors' in db.list_collection_names():
            count = db.doctors.count_documents({})
            print(f"\n👨‍⚕️ Doctors: {count} documents")
            
            # Show first few doctors
            print("\nSample doctors:")
            for doc in db.doctors.find().limit(2):
                print(f"- {doc.get('name')} (Centre: {doc.get('centre_id')})")
        
        return 0
        
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(f"❌ Could not connect to MongoDB: {err}")
        print("\nPossible solutions:")
        print("1. Check your internet connection")
        print("2. Verify the MongoDB Atlas cluster is running")
        print("3. Check if your IP is whitelisted in MongoDB Atlas")
        return 1
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
