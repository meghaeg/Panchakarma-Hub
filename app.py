from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
import os
import requests
from datetime import datetime, timedelta
import secrets
import logging
import json
from dotenv import load_dotenv

# Load env before importing our modules (so services can read credentials at import time)
load_dotenv()

# Import our modules
from utils import get_db_connection
from models import *
from routes import *
from email_service import send_email

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

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
        logging.debug(f"Proxy received: {request.json}")

        response = requests.post(
            'http://127.0.0.1:5000/api/chat',   # backend server.py
            json=request.json,
            headers={'Content-Type': 'application/json'}
        )

        logging.debug(f"Backend status: {response.status_code}, response: {response.text}")

        # Forward backend response + status code
        return jsonify(response.json()), response.status_code

    except requests.exceptions.ConnectionError:
        logging.error("Backend server not reachable on port 5000")
        return jsonify({'error': 'Backend server not reachable on port 5000'}), 502

    except Exception as e:
        logging.exception("Error in chat_proxy")
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

@app.route('/api/centres')
def api_centres():
    """Return structured list of NABH centres.
    Data is loaded from a JSON file if available, otherwise parsed from
    a bundled text resource created from the provided list.
    """
    try:
        data = load_centres_data()
        return jsonify({'success': True, 'count': len(data), 'data': data})
    except Exception as e:
        app.logger.exception('Error loading centres data')
        return jsonify({'success': False, 'message': str(e)}), 500

def load_centres_data():
    """Load centres data from JSON or parse from text fallback."""
    base = os.path.join(app.root_path, 'static', 'data')
    json_path = os.path.join(base, 'nabh_centres.json')
    txt_path = os.path.join(base, 'nabh_centres_part1.txt')

    # Prefer JSON if present
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    return data
            except Exception:
                pass

    # Fallback to parsing provided text list
    if os.path.exists(base):
        # Merge all parts in lexical order
        parts = [
            os.path.join(base, f)
            for f in os.listdir(base)
            if f.startswith('nabh_centres_part') and f.endswith('.txt')
        ]
        parts.sort()
        merged = []
        for p in parts:
            merged.extend(parse_centres_txt(p))
        if merged:
            return merged

    # Minimal hardcoded fallback
    return [
        {
            'id': 1,
            'reference_no': 'PC-2017-0001',
            'name': 'Swapnadeep Ayurveda, Kharghar, Maharashtra, India',
            'acc_no': 'PC-2017-0001',
            'valid_from': '15 Nov 2017',
            'valid_upto': '14 Nov 2020',
            'remarks': 'Application closed'
        }
    ]

def parse_centres_txt(path: str):
    """
    Parse the raw list text into structured items.
    Expected pattern per item:
      <S.N>
      <Reference No>
      <Name>
      <Acc. No>
      <Valid From>
      <Valid Upto>
      [Remarks?]
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [ln.strip() for ln in f if ln.strip()]
    except FileNotFoundError:
        return []

    data = []
    i = 0
    # Skip header if present
    if lines and lines[0].startswith('S.N'):
        i = 1

    while i < len(lines):
        # Seek the next serial number (pure digits)
        if not lines[i].isdigit():
            i += 1
            continue
        try:
            sn = int(lines[i]); i += 1
            ref = lines[i]; i += 1
            name = lines[i]; i += 1
            acc = lines[i]; i += 1
            valid_from = lines[i]; i += 1
            valid_upto = lines[i]; i += 1
        except Exception:
            break

        remarks = ''
        if i < len(lines):
            nxt = lines[i]
            # If next token starts a new record (digits) or a reference id (PC-), no remarks
            if not (nxt.isdigit() or nxt.startswith('PC-')):
                remarks = nxt
                i += 1

        data.append({
            'id': sn,
            'reference_no': ref,
            'name': name,
            'acc_no': acc,
            'valid_from': valid_from,
            'valid_upto': valid_upto,
            'remarks': remarks
        })

    return data

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
