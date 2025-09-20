#!/bin/bash

# Deployment script for Alexa integration
echo "🚀 Deploying Alexa Integration for Panchakarma Management System"

# Check if required tools are installed
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting." >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm is required but not installed. Aborting." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed. Aborting." >&2; exit 1; }

echo "✅ Prerequisites check passed"

# Install Lambda dependencies
echo "📦 Installing Lambda dependencies..."
cd alexa-skill/lambda
npm install
cd ../..

# Install WebSocket server dependencies
echo "📦 Installing WebSocket server dependencies..."
pip install -r websocket_requirements.txt

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cat > .env << EOF
# MongoDB Configuration
MONGODB_URI=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/
DB_NAME=panchakarma_db

# WebSocket Server Configuration
WS_HOST=localhost
WS_PORT=8765

# Alexa Configuration
ALEXA_SKILL_ID=your-skill-id
LAMBDA_FUNCTION_ARN=your-lambda-arn
EOF
    echo "⚠️  Please update .env file with your actual MongoDB and AWS credentials"
fi

# Create deployment package for Lambda
echo "📦 Creating Lambda deployment package..."
cd alexa-skill/lambda
zip -r ../../lambda-deployment.zip .
cd ../..

echo "✅ Lambda deployment package created: lambda-deployment.zip"

# Create systemd service for WebSocket server
echo "🔧 Creating systemd service for WebSocket server..."
sudo tee /etc/systemd/system/panchakarma-websocket.service > /dev/null << EOF
[Unit]
Description=Panchakarma WebSocket Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$(pwd)
Environment=PATH=$(which python3)
ExecStart=$(which python3) websocket_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd service created"

# Instructions for manual steps
echo ""
echo "🎯 Manual Steps Required:"
echo ""
echo "1. AWS Lambda Setup:"
echo "   - Upload lambda-deployment.zip to AWS Lambda"
echo "   - Set environment variables: MONGODB_URI, DB_NAME"
echo "   - Set timeout to 30 seconds"
echo "   - Set memory to 256 MB"
echo ""
echo "2. Alexa Skill Setup:"
echo "   - Create new Alexa skill in AWS Developer Console"
echo "   - Upload skill.json as the interaction model"
echo "   - Set Lambda function ARN as the endpoint"
echo "   - Test the skill with sample utterances"
echo ""
echo "3. WebSocket Server:"
echo "   - Update .env file with your MongoDB credentials"
echo "   - Start the service: sudo systemctl start panchakarma-websocket"
echo "   - Enable auto-start: sudo systemctl enable panchakarma-websocket"
echo ""
echo "4. Flask Application:"
echo "   - Install additional requirements: pip install -r requirements.txt"
echo "   - Start the Flask app: python app.py"
echo ""
echo "5. Testing:"
echo "   - Access Alexa dashboard: http://localhost:5001/alexa-dashboard"
echo "   - Test WebSocket connection: http://localhost:8765"
echo "   - Test Alexa skill with voice commands"
echo ""
echo "🎉 Deployment preparation complete!"
echo ""
echo "📚 For detailed setup instructions, see ALEXA_SETUP_GUIDE.md"
