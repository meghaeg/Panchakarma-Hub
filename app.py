from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
import os
import requests
from datetime import datetime, timedelta
import secrets

# Import our modules
from utils import get_db_connection
from models import *
from routes import *
from email_service import send_email

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(centre_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def landing():
    """Landing page with Panchakarma benefits and NABH centres"""
    return render_template('landing.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms_of_service.html')

@app.route('/api/chat', methods=['POST'])
def chat_proxy():
    """Proxy endpoint for the Ayurveda chatbot"""
    try:
        # Forward the request to the chatbot backend
        response = requests.post(
            'http://127.0.0.1:5000/chat',
            json=request.json,
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """Role-based dashboard redirect"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    role = session.get('role')
    if role == 'patient':
        return redirect(url_for('patient.dashboard'))
    elif role == 'centre':
        return redirect(url_for('centre.dashboard'))
    elif role == 'doctor':
        return redirect(url_for('doctor.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
