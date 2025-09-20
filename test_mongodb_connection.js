// Test MongoDB connection for Lambda
const { MongoClient } = require('mongodb');

// Your actual MongoDB connection string
const MONGODB_URI = 'mongodb+srv://meghaeg27_db_user:Megha2711%24@cluster0.hz2o1hb.mongodb.net/panchakarma_portal?retryWrites=true&w=majority';
const DB_NAME = 'panchakarma_portal';

async function testConnection() {
    try {
        console.log('Testing MongoDB connection...');
        
        const client = new MongoClient(MONGODB_URI, {
            serverSelectionTimeoutMS: 5000,
            connectTimeoutMS: 5000,
            socketTimeoutMS: 5000,
        });
        
        await client.connect();
        console.log('✅ Connected to MongoDB successfully!');
        
        const db = client.db(DB_NAME);
        const collections = await db.listCollections().toArray();
        console.log('📊 Available collections:', collections.map(c => c.name));
        
        // Test a simple query
        const doctorCount = await db.collection('doctors').countDocuments();
        console.log(`👨‍⚕️ Total doctors: ${doctorCount}`);
        
        await client.close();
        console.log('✅ Connection test completed successfully!');
        
    } catch (error) {
        console.error('❌ MongoDB connection failed:', error.message);
        console.error('Please check your connection string and credentials.');
    }
}

// Run the test
testConnection();
