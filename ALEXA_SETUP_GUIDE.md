# Alexa Voice Assistant Integration Setup Guide

This guide will help you set up the Alexa voice assistant integration for the Panchakarma Management System.

## 🎯 Overview

The Alexa integration provides voice-controlled management for:
- **Doctor Management**: Add certified doctors to the center
- **Patient Assignment**: Assign doctors to patients based on schedule
- **Bed Management**: Check availability and allocate rooms
- **Real-time Updates**: Live dashboard updates via WebSocket

## 📋 Prerequisites

- AWS Account with Lambda and Alexa Skills Kit access
- MongoDB Atlas cluster
- Node.js (v14 or higher)
- Python 3.8+
- Flask application running

## 🚀 Step-by-Step Setup

### 1. AWS Lambda Function Setup

#### 1.1 Create Lambda Function
1. Go to AWS Lambda Console
2. Click "Create function"
3. Choose "Author from scratch"
4. Name: `panchakarma-alexa-handler`
5. Runtime: Node.js 18.x
6. Architecture: x86_64

#### 1.2 Upload Code
1. Download the `lambda-deployment.zip` file created by the deployment script
2. In Lambda console, go to "Code" tab
3. Click "Upload from" → ".zip file"
4. Upload the `lambda-deployment.zip` file

#### 1.3 Configure Environment Variables
In Lambda console, go to "Configuration" → "Environment variables":
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=panchakarma_db
```

#### 1.4 Set Function Settings
- **Timeout**: 30 seconds
- **Memory**: 256 MB
- **Handler**: index.handler

#### 1.5 Test the Function
Create a test event:
```json
{
  "version": "1.0",
  "session": {
    "sessionId": "amzn1.echo-api.session.test",
    "application": {
      "applicationId": "amzn1.ask.skill.test"
    }
  },
  "request": {
    "type": "LaunchRequest",
    "requestId": "amzn1.echo-api.request.test"
  }
}
```

### 2. Alexa Skill Setup

#### 2.1 Create Alexa Skill
1. Go to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Click "Create Skill"
3. Skill name: `Panchakarma Manager`
4. Default language: English (US)
5. Choose "Custom" model
6. Choose "Provision your own" for hosting

#### 2.2 Configure Interaction Model
1. Go to "Build" tab
2. Click "JSON Editor"
3. Copy and paste the contents of `alexa-skill/skill.json`
4. Click "Save Model"
5. Click "Build Model"

#### 2.3 Configure Endpoint
1. Go to "Endpoint" tab
2. Select "AWS Lambda ARN"
3. Paste your Lambda function ARN
4. Select appropriate regions
5. Click "Save Endpoints"

#### 2.4 Test the Skill
1. Go to "Test" tab
2. Enable testing for "Development"
3. Try these test utterances:
   - "Alexa, open panchakarma manager"
   - "Alexa, add Dr. John to the center if certified"
   - "Alexa, check available beds for this week"
   - "Alexa, allocate a VIP room for patient Sarah"

### 3. WebSocket Server Setup

#### 3.1 Install Dependencies
```bash
pip install -r websocket_requirements.txt
```

#### 3.2 Configure Environment
Update `.env` file:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=panchakarma_db
WS_HOST=localhost
WS_PORT=8765
```

#### 3.3 Start WebSocket Server
```bash
python websocket_server.py
```

#### 3.4 Set Up as Service (Linux)
```bash
sudo systemctl start panchakarma-websocket
sudo systemctl enable panchakarma-websocket
```

### 4. Flask Application Integration

#### 4.1 Install Additional Dependencies
```bash
pip install -r requirements.txt
```

#### 4.2 Start Flask Application
```bash
python app.py
```

#### 4.3 Access Alexa Dashboard
Navigate to: `http://localhost:5001/alexa-dashboard`

## 🧪 Testing Guide

### Voice Commands Testing

#### Doctor Management
```
"Alexa, add Dr. Meera to the center if certified"
"Alexa, add a new certified doctor named Ramesh"
"Alexa, add doctor John if certified"
```

**Expected Response**: Confirmation of doctor addition with doctor ID

#### Patient Assignment
```
"Alexa, assign a doctor to patient Kavya"
"Alexa, assign Dr. Ramesh to patient Rohan according to schedule"
"Alexa, assign available doctor to patient Sarah"
```

**Expected Response**: Confirmation of doctor assignment with appointment details

#### Bed Management
```
"Alexa, check available beds for this week"
"Alexa, check bed availability for today"
"Alexa, how many beds are available for tomorrow"
```

**Expected Response**: List of available beds by type and count

#### Room Allocation
```
"Alexa, allocate a VIP room for patient Anu"
"Alexa, allocate general ward room for patient Ramesh"
"Alexa, assign normal room to patient Sarah"
```

**Expected Response**: Confirmation of room allocation with bed details

#### Centre Status
```
"Alexa, what is the centre status"
"Alexa, show me centre statistics"
"Alexa, give me centre overview"
```

**Expected Response**: Summary of centre statistics

### WebSocket Testing

#### 1. Connection Test
Open browser console on the Alexa dashboard and check for:
```
WebSocket connected
```

#### 2. Real-time Updates Test
1. Add a doctor via Alexa
2. Check dashboard for real-time notification
3. Verify statistics update automatically

#### 3. API Testing
Test the API endpoints:
```bash
# Test dashboard stats
curl http://localhost:5001/api/dashboard-stats

# Test bed statistics
curl http://localhost:5001/api/bed-statistics

# Test recent activities
curl http://localhost:5001/api/recent-activities
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Lambda Function Errors
- **Issue**: "Cannot find module 'mongodb'"
- **Solution**: Ensure all dependencies are in the deployment package

- **Issue**: "MongoDB connection failed"
- **Solution**: Check MONGODB_URI environment variable

#### 2. Alexa Skill Issues
- **Issue**: "Skill not responding"
- **Solution**: Check Lambda function ARN and permissions

- **Issue**: "Intent not recognized"
- **Solution**: Verify interaction model is built and deployed

#### 3. WebSocket Connection Issues
- **Issue**: "WebSocket connection failed"
- **Solution**: Check if WebSocket server is running on port 8765

- **Issue**: "No real-time updates"
- **Solution**: Verify MongoDB change streams are working

### Debug Mode

Enable debug logging by setting:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Logs Location

- **Lambda Logs**: AWS CloudWatch Logs
- **WebSocket Logs**: Console output
- **Flask Logs**: Application console

## 📊 Monitoring and Analytics

### CloudWatch Metrics
Monitor Lambda function:
- Invocations
- Duration
- Errors
- Throttles

### Custom Metrics
Track Alexa usage:
- Intent invocations
- Success/failure rates
- Response times

## 🔒 Security Considerations

### MongoDB Security
- Use MongoDB Atlas with IP whitelisting
- Enable authentication
- Use connection string with credentials

### AWS Security
- Use IAM roles with minimal permissions
- Enable VPC if required
- Monitor CloudTrail logs

### WebSocket Security
- Implement authentication for WebSocket connections
- Use WSS (WebSocket Secure) in production
- Rate limit connections

## 🚀 Production Deployment

### 1. Environment Setup
- Use production MongoDB cluster
- Set up proper monitoring
- Configure backup strategies

### 2. Scaling
- Use Lambda provisioned concurrency for consistent performance
- Set up auto-scaling for WebSocket server
- Use load balancer for multiple instances

### 3. Monitoring
- Set up CloudWatch alarms
- Implement health checks
- Monitor error rates and response times

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error messages
3. Test individual components separately
4. Contact system administrator

## 🎉 Success Criteria

Your Alexa integration is working correctly when:
- ✅ All voice commands are recognized
- ✅ Database operations complete successfully
- ✅ Real-time updates appear on dashboard
- ✅ WebSocket connection remains stable
- ✅ Error handling works properly

---

**Note**: This integration requires proper AWS and MongoDB setup. Ensure all credentials and permissions are configured correctly before testing.
