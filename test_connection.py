"""Simple script to test MongoDB connection"""

import pymongo
from pymongo import MongoClient

def test_connection():
    try:
        # Connection string from utils.py
        atlas_connection = "mongodb+srv://meghaeg27_db_user:Megha2711%24@cluster0.hz2o1hb.mongodb.net/panchakarma_portal?retryWrites=true&w=majority"
        
        print("🔌 Attempting to connect to MongoDB...")
        client = MongoClient(atlas_connection, serverSelectionTimeoutMS=5000)
        
        # The ismaster command is cheap and does not require auth
        client.admin.command('ismaster')
        print("✅ Successfully connected to MongoDB!")
        
        # List all databases
        print("\n📂 Available databases:")
        for db_name in client.list_database_names():
            print(f"- {db_name}")
            
            # List collections for each database
            db = client[db_name]
            collections = db.list_collection_names()
            if collections:
                print(f"  Collections in {db_name}:")
                for col in collections:
                    count = db[col].count_documents({})
                    print(f"  - {col}: {count} documents")
        
        return True
        
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print("❌ Could not connect to MongoDB server. Connection timed out.")
        print(f"Error details: {err}")
        return False
    except pymongo.errors.ConnectionFailure as err:
        print(f"❌ Could not connect to MongoDB: {err}")
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing MongoDB connection...")
    test_connection()
