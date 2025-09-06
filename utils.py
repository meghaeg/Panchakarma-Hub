import pymongo
from pymongo import MongoClient
from datetime import datetime
import os

# MongoDB connection string
MONGO_URI = "mongodb+srv://meghaeg27_db_user:Megha2711%24@cluster0.hz2o1hb.mongodb.net/?retryWrites=true&w=majority"

def get_db_connection():
    """Get MongoDB connection - using new Atlas credentials"""
    # Use the new MongoDB Atlas connection
    atlas_connection = "mongodb+srv://meghaeg27_db_user:Megha2711%24@cluster0.hz2o1hb.mongodb.net/panchakarma_portal?retryWrites=true&w=majority"
    
    try:
        client = MongoClient(atlas_connection, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("Connected to MongoDB Atlas successfully (mode: Atlas)")
        return client.panchakarma_portal
    except Exception as e:
        print(f"Atlas connection failed: {e}")
        # Use in-memory database as fallback
        print("Using in-memory database fallback (mode: InMemoryDB)")
        return InMemoryDB()

class InMemoryDB:
    """Simple in-memory database for fallback"""
    def __init__(self):
        self.data = {
            'patients': [],
            'centres': [],
            'doctors': [],
            'admins': [],
            'appointments': [],
            'detox_appointments': [],
            'progress_tracking': [],
            'feedback': []
        }
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Initialize with sample data"""
        import bcrypt
        
        # Sample admin
        admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        self.data['admins'].append({
            'admin_id': 'ADM001',
            'name': 'Ministry Admin',
            'email': 'admin@ayush.gov.in',
            'password': admin_password,
            'role': 'super_admin'
        })
        
        # Sample patient
        patient_password = bcrypt.hashpw('patient123'.encode('utf-8'), bcrypt.gensalt())
        self.data['patients'].append({
            'patient_id': 'PAT001',
            'aadhar': '123456789012',
            'name': 'Arjun Patel',
            'age': 35,
            'email': 'arjun.patel@email.com',
            'phone': '9876543210',
            'password': patient_password,
            'address': 'Mumbai, Maharashtra',
            'blood_group': 'B+',
            'health_issues': 'Stress, Joint Pain',
            'medications': 'None',
            'dob': '1988-05-15'
        })
        
        # Sample centre
        centre_password = bcrypt.hashpw('centre123'.encode('utf-8'), bcrypt.gensalt())
        self.data['centres'].append({
            'centre_id': 'CEN001',
            'name': 'Kerala Ayurveda Centre',
            'email': 'info@keralaayurveda.com',
            'phone': '9123456789',
            'password': centre_password,
            'address': 'Kochi, Kerala',
            'city': 'Kochi',
            'state': 'Kerala',
            'pincode': '682001',
            'license_number': 'KER001',
            'nabh_accredited': True,
            'status': 'approved'
        })
        
        # Sample doctor
        doctor_password = bcrypt.hashpw('doctor123'.encode('utf-8'), bcrypt.gensalt())
        self.data['doctors'].append({
            'doctor_id': 'DOC001',
            'centre_id': 'CEN001',
            'name': 'Dr. Rajesh Kumar',
            'email': 'dr.rajesh@keralaayurveda.com',
            'phone': '9876543211',
            'password': doctor_password,
            'specialization': 'Panchakarma Specialist',
            'experience': 15,
            'qualification': 'BAMS, MD (Ayurveda)',
            'license_number': 'DOC001KER',
            'status': 'active'
        })
    
    def __getattr__(self, name):
        """Return collection-like object"""
        if name in self.data:
            return InMemoryCollection(self.data[name])
        raise AttributeError(f"Collection '{name}' not found")

class InMemoryCollection:
    """Collection-like interface for in-memory data"""
    def __init__(self, data):
        self.data = data
    
    def find_one(self, query):
        """Find one document matching query"""
        for item in self.data:
            if all(item.get(k) == v for k, v in query.items()):
                return item
        return None
    
    def find(self, query=None):
        """Find documents matching query"""
        if query is None:
            return self.data
        return [item for item in self.data if all(item.get(k) == v for k, v in query.items())]
    
    def insert_one(self, document):
        """Insert one document"""
        self.data.append(document)
        return type('InsertResult', (), {'inserted_id': len(self.data), 'acknowledged': True})()
    
    def count_documents(self, query=None):
        """Count documents"""
        if query is None:
            return len(self.data)
        return len(self.find(query))

def generate_appointment_id():
    """Generate unique appointment ID"""
    return f"APT{datetime.now().strftime('%Y%m%d%H%M%S')}"

def generate_patient_id():
    """Generate unique patient ID"""
    return f"PAT{datetime.now().strftime('%Y%m%d%H%M%S')}"

def generate_doctor_id():
    """Generate unique doctor ID"""
    return f"DOC{datetime.now().strftime('%Y%m%d%H%M%S')}"

def generate_centre_id():
    """Generate unique centre ID"""
    return f"CEN{datetime.now().strftime('%Y%m%d%H%M%S')}"

def generate_detox_appointment_id():
    """Generate unique detox appointment ID"""
    return f"DETOX{datetime.now().strftime('%Y%m%d%H%M%S')}"

def generate_progress_id():
    """Generate unique progress tracking ID"""
    return f"PROG{datetime.now().strftime('%Y%m%d%H%M%S')}"

def validate_aadhar(aadhar):
    """Validate Aadhar number format"""
    if not aadhar or len(aadhar) != 12:
        return False
    return aadhar.isdigit()

def format_date(date_str):
    """Format date string to datetime object"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except:
        return None
