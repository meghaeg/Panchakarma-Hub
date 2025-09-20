# 🎤 Alexa Voice Assistant Integration

## Overview

This integration adds voice-controlled management capabilities to the Panchakarma Management System using Amazon Alexa. Center staff can now use voice commands to manage doctors, assign patients, and handle bed allocation through their Alexa-enabled devices.

## ✨ Features

### 🩺 Doctor Management
- **Add Certified Doctors**: "Alexa, add Dr. [Name] to the center if certified"
- **Verification**: Only certified doctors can be added
- **Real-time Updates**: Dashboard updates immediately when doctors are added

### 👥 Patient Assignment
- **Smart Assignment**: "Alexa, assign a doctor to patient [Name]"
- **Schedule Checking**: Automatically checks doctor availability
- **Flexible Options**: Can specify particular doctor or let system choose

### 🛏️ Bed Management
- **Availability Check**: "Alexa, check available beds for this week"
- **Room Allocation**: "Alexa, allocate a VIP room for patient [Name]"
- **Room Types**: General Ward, Normal Room, VIP Room, Special Room, Panchakarma Therapy

### 📊 Real-time Dashboard
- **Live Updates**: WebSocket integration provides instant updates
- **Visual Notifications**: Toast notifications for all voice actions
- **Statistics**: Real-time statistics and occupancy rates

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Alexa Device  │───▶│  AWS Lambda      │───▶│  MongoDB Atlas  │
│   (Voice Input) │    │  (Intent Handler)│    │  (Database)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  WebSocket       │
                       │  Server          │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Flask App       │
                       │  (Dashboard)     │
                       └──────────────────┘
```

## 📁 File Structure

```
alexa-skill/
├── skill.json                 # Alexa skill configuration
└── lambda/
    ├── index.js              # Lambda function code
    └── package.json          # Node.js dependencies

websocket_server.py           # WebSocket server for real-time updates
alexa_api.py                  # Flask API endpoints for Alexa integration
templates/centre/
└── alexa_dashboard.html      # Enhanced dashboard with WebSocket integration
static/js/
└── websocket-client.js       # Client-side WebSocket handling

test_alexa_integration.py     # Comprehensive test suite
deploy_alexa.sh              # Deployment script
ALEXA_SETUP_GUIDE.md         # Detailed setup instructions
```

## 🚀 Quick Start

### 1. Prerequisites
- AWS Account with Lambda access
- MongoDB Atlas cluster
- Node.js 14+
- Python 3.8+
- Alexa-enabled device

### 2. Installation
```bash
# Clone and setup
git clone <repository>
cd panchakarma-aws

# Install dependencies
pip install -r requirements.txt
pip install -r websocket_requirements.txt

# Setup Lambda dependencies
cd alexa-skill/lambda
npm install
cd ../..

# Run deployment script
chmod +x deploy_alexa.sh
./deploy_alexa.sh
```

### 3. Configuration
```bash
# Copy environment file
cp env.example .env

# Edit with your credentials
nano .env
```

### 4. Start Services
```bash
# Terminal 1: Flask application
python app.py

# Terminal 2: WebSocket server
python websocket_server.py

# Terminal 3: Test the integration
python test_alexa_integration.py
```

### 5. Access Dashboard
Navigate to: `http://localhost:5001/alexa-dashboard`

## 🎯 Voice Commands

### Doctor Management
```
"Alexa, add Dr. Meera to the center if certified"
"Alexa, add a new certified doctor named Ramesh"
"Alexa, add doctor John if certified"
```

### Patient Assignment
```
"Alexa, assign a doctor to patient Kavya"
"Alexa, assign Dr. Ramesh to patient Rohan according to schedule"
"Alexa, assign available doctor to patient Sarah"
```

### Bed Management
```
"Alexa, check available beds for this week"
"Alexa, check bed availability for today"
"Alexa, how many beds are available for tomorrow"
```

### Room Allocation
```
"Alexa, allocate a VIP room for patient Anu"
"Alexa, allocate general ward room for patient Ramesh"
"Alexa, assign normal room to patient Sarah"
```

### Centre Status
```
"Alexa, what is the centre status"
"Alexa, show me centre statistics"
"Alexa, give me centre overview"
```

## 🔧 API Endpoints

### Dashboard Statistics
```http
GET /api/dashboard-stats
```
Returns comprehensive dashboard statistics including doctors, appointments, and beds.

### Bed Management
```http
GET /api/bed-statistics?centre_id=CENTRE001
GET /api/beds?centre_id=CENTRE001&status=available
```

### Recent Activities
```http
GET /api/recent-activities
```
Returns recent system activities for real-time updates.

### Connection Test
```http
GET /api/test-alexa-connection
```
Tests the overall system connectivity.

## 🧪 Testing

### Automated Testing
```bash
python test_alexa_integration.py
```

### Manual Testing
1. **Voice Commands**: Use actual Alexa device or simulator
2. **WebSocket**: Check browser console for connection status
3. **API**: Use curl or Postman to test endpoints
4. **Dashboard**: Verify real-time updates appear

### Test Coverage
- ✅ Flask API endpoints
- ✅ WebSocket connection
- ✅ Database connectivity
- ✅ Lambda function simulation
- ✅ Dashboard page loading

## 🔒 Security

### MongoDB Security
- Connection string authentication
- IP whitelisting
- SSL/TLS encryption

### AWS Security
- IAM roles with minimal permissions
- Environment variable encryption
- VPC configuration (optional)

### WebSocket Security
- Authentication tokens (production)
- Rate limiting
- CORS configuration

## 📊 Monitoring

### CloudWatch Metrics
- Lambda invocations and errors
- Function duration and memory usage
- Custom metrics for Alexa usage

### Application Monitoring
- WebSocket connection status
- Database query performance
- Real-time update frequency

### Logging
- Structured logging with timestamps
- Error tracking and alerting
- Performance metrics

## 🚀 Production Deployment

### 1. Environment Setup
```bash
# Production environment variables
MONGODB_URI=mongodb+srv://prod-username:password@cluster.mongodb.net/
DB_NAME=panchakarma_prod
WS_HOST=0.0.0.0
WS_PORT=8765
```

### 2. Scaling Considerations
- **Lambda**: Use provisioned concurrency for consistent performance
- **WebSocket**: Deploy multiple instances behind load balancer
- **Database**: Use MongoDB Atlas with auto-scaling

### 3. Monitoring Setup
- CloudWatch alarms for Lambda errors
- Health checks for WebSocket server
- Database performance monitoring

## 🐛 Troubleshooting

### Common Issues

#### Lambda Function
- **Timeout**: Increase timeout to 30 seconds
- **Memory**: Increase to 256 MB minimum
- **Dependencies**: Ensure all packages are in deployment zip

#### WebSocket Server
- **Port conflicts**: Check if port 8765 is available
- **Firewall**: Ensure port is open
- **MongoDB**: Verify connection string

#### Alexa Skill
- **Intent recognition**: Check interaction model
- **Endpoint**: Verify Lambda ARN
- **Permissions**: Ensure Lambda has Alexa trigger permission

### Debug Mode
```python
# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Locations
- **Lambda**: AWS CloudWatch Logs
- **WebSocket**: Console output
- **Flask**: Application logs

## 📈 Performance Optimization

### Lambda Optimization
- Use connection pooling for MongoDB
- Implement caching for frequently accessed data
- Optimize cold start times

### WebSocket Optimization
- Implement message queuing
- Use compression for large payloads
- Monitor connection limits

### Database Optimization
- Create appropriate indexes
- Use aggregation pipelines efficiently
- Monitor query performance

## 🔄 Updates and Maintenance

### Regular Tasks
- Monitor error rates and performance
- Update dependencies regularly
- Review and rotate credentials
- Test voice commands after updates

### Version Control
- Tag releases with semantic versioning
- Maintain changelog
- Test in staging before production

## 📞 Support

### Documentation
- [ALEXA_SETUP_GUIDE.md](ALEXA_SETUP_GUIDE.md) - Detailed setup instructions
- [API Documentation](api_docs.md) - Complete API reference
- [Troubleshooting Guide](troubleshooting.md) - Common issues and solutions

### Getting Help
1. Check the troubleshooting section
2. Review logs for error messages
3. Test individual components
4. Contact system administrator

## 🎉 Success Metrics

Your Alexa integration is working correctly when:
- ✅ All voice commands are recognized and processed
- ✅ Database operations complete successfully
- ✅ Real-time updates appear on dashboard
- ✅ WebSocket connection remains stable
- ✅ Error handling works properly
- ✅ Performance meets requirements

---

**Built with ❤️ for Panchakarma Management System**

*This integration brings the power of voice control to healthcare management, making it easier for medical staff to focus on patient care while efficiently managing administrative tasks.*
