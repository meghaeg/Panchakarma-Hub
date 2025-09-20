import base64
import os
from datetime import datetime, timedelta
import requests
from bson import ObjectId
from flask import Flask, jsonify, request
from pymongo import MongoClient

# === Your original Zoom integration code, unchanged ===

ZOOM_ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID', '')
ZOOM_CLIENT_ID = os.getenv('ZOOM_CLIENT_ID', '')
ZOOM_CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET', '')


def _get_access_token() -> str:
    """Fetch Server-to-Server OAuth access token from Zoom.

    Requires env vars: ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET
    """
    if not (ZOOM_ACCOUNT_ID and ZOOM_CLIENT_ID and ZOOM_CLIENT_SECRET):
        raise RuntimeError('Zoom credentials are not configured in environment variables')

    token_url = 'https://zoom.us/oauth/token'
    auth_header = base64.b64encode(f"{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}".encode('utf-8')).decode('utf-8')
    params = {
        'grant_type': 'account_credentials',
        'account_id': ZOOM_ACCOUNT_ID
    }
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    resp = requests.post(token_url, params=params, headers=headers, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    return data.get('access_token')


def create_zoom_meeting(topic: str, start_time_iso: str, duration_minutes: int = 15, timezone: str = 'Asia/Kolkata', agenda: str = '') -> dict:
    """Create a Scheduled Zoom meeting via S2S OAuth.

    Returns a dict with essential fields: id, start_url, join_url, password.
    """
    token = _get_access_token()
    url = 'https://api.zoom.us/v2/users/me/meetings'
    payload = {
        'topic': topic,
        'type': 2,  # scheduled
        'start_time': start_time_iso,
        'duration': duration_minutes,
        'timezone': timezone,
        'agenda': agenda,
        'settings': {
            'host_video': False,
            'participant_video': False,
            'waiting_room': True,
            'join_before_host': False,
            'approval_type': 2,  # no registration
            'audio': 'voip',
        }
    }
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    return {
        'id': data.get('id'),
        'start_url': data.get('start_url'),
        'join_url': data.get('join_url'),
        'password': data.get('password')
    }


def build_iso_time_for_today(slot_time: str, timezone: str = 'Asia/Kolkata') -> str:
    """Build ISO8601 start_time for today's date and given HH:MM slot in IST by default."""
    today = datetime.now()
    hour, minute = [int(x) for x in slot_time.split(':')]
    local_dt = today.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return local_dt.strftime('%Y-%m-%dT%H:%M:%S')


def end_zoom_meeting(meeting_id: int) -> bool:
    """End a running Zoom meeting using Zoom's 'update meeting status' API."""
    token = _get_access_token()
    url = f'https://api.zoom.us/v2/meetings/{meeting_id}/status'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {'action': 'end'}
    resp = requests.put(url, json=payload, headers=headers, timeout=20)
    return resp.status_code in (200, 204)


# === MongoDB setup (example) ===
app = Flask(__name__)
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017'))
db = client['your_database_name']  # change to your DB


# === New helper to fix ObjectId JSON serialization ===
def serialize_mongo_doc(doc: dict) -> dict:
    """Convert ObjectId fields in a MongoDB document to strings for JSON serialization."""
    return {
        key: str(value) if isinstance(value, ObjectId) else value
        for key, value in doc.items()
    }


# === Example API route to book a Zoom meeting and save to Mongo ===
@app.route('/api/book_meeting', methods=['POST'])
def book_meeting():
    data = request.json
    slot = data.get('slot_time')
    if not slot:
        return jsonify({'error': 'Missing slot_time parameter'}), 400

    topic = "Dermatology Consultation"
    start_time = build_iso_time_for_today(slot)

    try:
        zoom_data = create_zoom_meeting(topic, start_time)
    except Exception as e:
        return jsonify({'error': f'Zoom API error: {str(e)}'}), 500

    meeting_doc = {
        'topic': topic,
        'start_time': start_time,
        'zoom': zoom_data
    }

    inserted = db.bookings.insert_one(meeting_doc)
    meeting_doc['_id'] = inserted.inserted_id

    return jsonify(serialize_mongo_doc(meeting_doc))


if __name__ == '__main__':
    app.run(debug=True)
