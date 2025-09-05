"""Script to check MongoDB connection and collections"""

from pymongo import MongoClient
from datetime import datetime

def check_database():
    """Check MongoDB connection and collections"""
    try:
        # Use the same connection string as in utils.py
        atlas_connection = "mongodb+srv://meghaeg27_db_user:Megha2711%24@cluster0.hz2o1hb.mongodb.net/panchakarma_portal?retryWrites=true&w=majority"
        
        # Connect to MongoDB
        client = MongoClient(atlas_connection, serverSelectionTimeoutMS=5000)
        
        # Verify connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas")
        
        # Get database
        db = client.get_database('panchakarma_portal')
        
        # List all collections
        collections = db.list_collection_names()
        print("\n📂 Collections in database:")
        for col in collections:
            count = db[col].count_documents({})
            print(f"- {col}: {count} documents")
        
        # Show sample documents
        if 'centres' in collections:
            print("\n🏥 Centres:")
            for centre in db.centres.find():
                print(f"- {centre.get('name')} (ID: {centre.get('_id')})")
        
        if 'doctors' in collections:
            print("\n👨‍⚕️ Doctors:")
            for doctor in db.doctors.find():
                print(f"- {doctor.get('name')} (Centre: {doctor.get('centre_id')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking database connection...")
    check_database()
