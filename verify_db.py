"""Simple script to verify MongoDB connection and print collections"""

import pymongo
from pymongo import MongoClient

def main():
    print("🔍 Verifying MongoDB connection...")
    
    try:
        # Connection string from utils.py
        uri = "mongodb+srv://meghaeg27_db_user:Megha2711%24@cluster0.hz2o1hb.mongodb.net/panchakarma_portal?retryWrites=true&w=majority"
        
        # Connect with a short timeout
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        
        # Get database
        db = client.get_database('panchakarma_portal')
        
        # List collections
        collections = db.list_collection_names()
        print("\n📂 Collections in database:")
        for col in collections:
            count = db[col].count_documents({})
            print(f"- {col}: {count} documents")
        
        # If collections exist, print some sample data
        if 'centres' in collections:
            print("\n🏥 Sample Centres:")
            for doc in db.centres.find().limit(2):
                print(f"- {doc.get('name')} (ID: {doc.get('_id')})")
        
        if 'doctors' in collections:
            print("\n👨‍⚕️ Sample Doctors:")
            for doc in db.doctors.find().limit(2):
                print(f"- {doc.get('name')} (Centre: {doc.get('centre_id')})")
        
        return 0
        
    except pymongo.errors.ServerSelectionTimeoutError:
        print("❌ Could not connect to MongoDB: Server selection timeout")
        print("\nPossible issues:")
        print("1. No internet connection")
        print("2. MongoDB Atlas cluster is not running")
        print("3. Your IP is not whitelisted in MongoDB Atlas")
        return 1
    except pymongo.errors.OperationFailure as e:
        print(f"❌ Authentication failed: {e}")
        print("\nCheck your MongoDB Atlas username and password")
        return 1
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
