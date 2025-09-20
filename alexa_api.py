"""
API endpoints for Alexa integration and real-time dashboard updates
"""
from flask import Blueprint, jsonify, request
from models import Doctor, Appointment, Bed, Centre, Patient
from datetime import datetime, timedelta
import logging

alexa_bp = Blueprint('alexa', __name__, url_prefix='/api')

@alexa_bp.route('/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    try:
        # Get database connection
        doctor_model = Doctor()
        appointment_model = Appointment()
        bed_model = Bed()
        
        # Get doctor statistics
        total_doctors = doctor_model.db.doctors.count_documents({'status': 'active'})
        new_doctors_today = doctor_model.db.doctors.count_documents({
            'created_at': {
                '$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            }
        })
        
        # Get appointment statistics
        total_appointments = appointment_model.db.appointments.count_documents({})
        today_appointments = appointment_model.db.appointments.count_documents({
            'appointment_date': {
                '$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                '$lt': datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
            }
        })
        pending_appointments = appointment_model.db.appointments.count_documents({
            'status': 'pending_approval'
        })
        
        # Get bed statistics
        total_beds = bed_model.db.beds.count_documents({})
        available_beds = bed_model.db.beds.count_documents({'status': 'available'})
        occupied_beds = bed_model.db.beds.count_documents({'status': 'occupied'})
        occupancy_rate = round((occupied_beds / total_beds * 100) if total_beds > 0 else 0, 2)
        
        return jsonify({
            'success': True,
            'data': {
                'doctors': {
                    'total': total_doctors,
                    'active': total_doctors,
                    'new_today': new_doctors_today
                },
                'appointments': {
                    'total': total_appointments,
                    'today': today_appointments,
                    'pending': pending_appointments
                },
                'beds': {
                    'total': total_beds,
                    'available': available_beds,
                    'occupied': occupied_beds,
                    'occupancy_rate': occupancy_rate
                }
            }
        })
    except Exception as e:
        logging.error(f"Error getting dashboard stats: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@alexa_bp.route('/doctor-stats', methods=['GET'])
def get_doctor_stats():
    """Get doctor statistics"""
    try:
        doctor_model = Doctor()
        total = doctor_model.db.doctors.count_documents({'status': 'active'})
        active = doctor_model.db.doctors.count_documents({'status': 'active'})
        
        return jsonify({
            'success': True,
            'total': total,
            'active': active
        })
    except Exception as e:
        logging.error(f"Error getting doctor stats: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@alexa_bp.route('/appointment-stats', methods=['GET'])
def get_appointment_stats():
    """Get appointment statistics"""
    try:
        appointment_model = Appointment()
        total = appointment_model.db.appointments.count_documents({})
        today = appointment_model.db.appointments.count_documents({
            'appointment_date': {
                '$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                '$lt': datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
            }
        })
        pending = appointment_model.db.appointments.count_documents({
            'status': 'pending_approval'
        })
        
        return jsonify({
            'success': True,
            'total': total,
            'today': today,
            'pending': pending
        })
    except Exception as e:
        logging.error(f"Error getting appointment stats: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@alexa_bp.route('/bed-statistics', methods=['GET'])
def get_bed_statistics():
    """Get bed statistics"""
    try:
        centre_id = request.args.get('centre_id', 'CENTRE001')  # Default for demo
        
        bed_model = Bed()
        total = bed_model.db.beds.count_documents({'centre_id': centre_id})
        available = bed_model.db.beds.count_documents({
            'centre_id': centre_id,
            'status': 'available'
        })
        occupied = bed_model.db.beds.count_documents({
            'centre_id': centre_id,
            'status': 'occupied'
        })
        occupancy_rate = round((occupied / total * 100) if total > 0 else 0, 2)
        
        return jsonify({
            'success': True,
            'total': total,
            'available': available,
            'occupied': occupied,
            'occupancy_rate': occupancy_rate
        })
    except Exception as e:
        logging.error(f"Error getting bed statistics: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@alexa_bp.route('/beds', methods=['GET'])
def get_beds():
    """Get all beds for a centre"""
    try:
        centre_id = request.args.get('centre_id', 'CENTRE001')  # Default for demo
        status = request.args.get('status')
        
        query = {'centre_id': centre_id}
        if status:
            query['status'] = status
        
        bed_model = Bed()
        beds = list(bed_model.db.beds.find(query).sort([('room_number', 1), ('bed_id', 1)]))
        
        # Convert ObjectId to string for JSON serialization
        for bed in beds:
            bed['_id'] = str(bed['_id'])
            if bed.get('created_at'):
                bed['created_at'] = bed['created_at'].isoformat()
            if bed.get('updated_at'):
                bed['updated_at'] = bed['updated_at'].isoformat()
            if bed.get('check_in_date'):
                bed['check_in_date'] = bed['check_in_date'].isoformat()
            if bed.get('check_out_date'):
                bed['check_out_date'] = bed['check_out_date'].isoformat()
        
        return jsonify({
            'success': True,
            'beds': beds
        })
    except Exception as e:
        logging.error(f"Error getting beds: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@alexa_bp.route('/recent-activities', methods=['GET'])
def get_recent_activities():
    """Get recent activities for the dashboard"""
    try:
        activities = []
        
        # Recent doctor additions (last 24 hours)
        doctor_model = Doctor()
        recent_doctors = list(doctor_model.db.doctors.find({
            'created_at': {
                '$gte': datetime.now() - timedelta(hours=24)
            }
        }).sort('created_at', -1).limit(5))
        
        for doctor in recent_doctors:
            activities.append({
                'type': 'doctor_added',
                'message': f"New doctor {doctor['name']} added",
                'timestamp': doctor['created_at'].isoformat(),
                'details': {
                    'specialization': doctor.get('specialization', 'Unknown'),
                    'doctor_id': doctor.get('doctor_id')
                }
            })
        
        # Recent appointments (last 24 hours)
        appointment_model = Appointment()
        recent_appointments = list(appointment_model.db.appointments.find({
            'created_at': {
                '$gte': datetime.now() - timedelta(hours=24)
            }
        }).sort('created_at', -1).limit(5))
        
        for appointment in recent_appointments:
            # Get patient and doctor names
            patient_model = Patient()
            patient = patient_model.db.patients.find_one(
                {'patient_id': appointment['patient_id']}, 
                {'name': 1}
            )
            doctor_model = Doctor()
            doctor = doctor_model.db.doctors.find_one(
                {'doctor_id': appointment['doctor_id']}, 
                {'name': 1}
            )
            
            activities.append({
                'type': 'appointment_created',
                'message': f"Appointment created for {patient['name'] if patient else 'Unknown'} with {doctor['name'] if doctor else 'Unknown'}",
                'timestamp': appointment['created_at'].isoformat(),
                'details': {
                    'status': appointment.get('status', 'Unknown'),
                    'appointment_id': appointment.get('appointment_id')
                }
            })
        
        # Recent bed changes (last 24 hours)
        recent_bed_changes = list(Bed().db.beds.find({
            'updated_at': {
                '$gte': datetime.now() - timedelta(hours=24)
            }
        }).sort('updated_at', -1).limit(5))
        
        for bed in recent_bed_changes:
            if bed['status'] == 'occupied' and bed.get('current_patient_name'):
                activities.append({
                    'type': 'bed_allocated',
                    'message': f"Bed {bed['room_number']} allocated to {bed['current_patient_name']}",
                    'timestamp': bed['updated_at'].isoformat(),
                    'details': {
                        'bed_id': bed['bed_id'],
                        'room_number': bed['room_number']
                    }
                })
        
        # Sort activities by timestamp (most recent first)
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'success': True,
            'activities': activities[:10]  # Return only the 10 most recent
        })
    except Exception as e:
        logging.error(f"Error getting recent activities: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@alexa_bp.route('/alexa-webhook', methods=['POST'])
def alexa_webhook():
    """Webhook endpoint for Alexa Lambda function to send updates"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Process the webhook data
        webhook_type = data.get('type')
        webhook_data = data.get('data', {})
        
        # Log the webhook for debugging
        logging.info(f"Received Alexa webhook: {webhook_type} - {webhook_data}")
        
        # Here you could trigger WebSocket updates or other real-time notifications
        # For now, we'll just log it and return success
        
        return jsonify({
            'success': True,
            'message': 'Webhook processed successfully'
        })
    except Exception as e:
        logging.error(f"Error processing Alexa webhook: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@alexa_bp.route('/add-doctor', methods=['POST'])
def add_doctor():
    """Add a new doctor to the database"""
    try:
        data = request.get_json()
        doctor_name = data.get('name', '').strip()
        specialization = data.get('specialization', 'General Medicine')
        
        if not doctor_name:
            return jsonify({'success': False, 'message': 'Doctor name is required'}), 400
        
        # Get database connection
        doctor_model = Doctor()
        
        # Check if doctor already exists
        existing_doctor = doctor_model.db.doctors.find_one({'name': {'$regex': f'^{doctor_name}$', '$options': 'i'}})
        if existing_doctor:
            return jsonify({
                'success': False, 
                'message': f'Doctor {doctor_name} already exists in the system',
                'doctor_id': existing_doctor.get('doctor_id')
            }), 409
        
        # Generate unique doctor ID
        import uuid
        doctor_id = f"DOC{str(uuid.uuid4())[:8].upper()}"
        
        # Create new doctor
        doctor_data = {
            'doctor_id': doctor_id,
            'name': doctor_name,
            'specialization': specialization,
            'status': 'active',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'centre_id': 'CENTRE001'  # Default centre
        }
        
        # Insert into database
        result = doctor_model.db.doctors.insert_one(doctor_data)
        
        if result.inserted_id:
            return jsonify({
                'success': True,
                'message': f'Successfully added Dr. {doctor_name} to the center',
                'doctor_id': doctor_id,
                'specialization': specialization,
                'status': 'active'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to add doctor to database'}), 500
            
    except Exception as e:
        logging.error(f"Error adding doctor: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@alexa_bp.route('/allocate-room', methods=['POST'])
def allocate_room():
    """Allocate a room for a patient"""
    try:
        data = request.get_json()
        patient_name = data.get('patient_name', '').strip()
        room_type = data.get('room_type', 'VIP Room')
        
        if not patient_name:
            return jsonify({'success': False, 'message': 'Patient name is required'}), 400
        
        # Get database connection
        bed_model = Bed()
        
        # Find an available bed
        available_bed = bed_model.db.beds.find_one({'status': 'available'})
        
        if not available_bed:
            return jsonify({
                'success': False, 
                'message': 'No available beds at the moment'
            }), 409
        
        # Update bed status
        bed_id = available_bed['bed_id']
        room_number = available_bed['room_number']
        
        update_result = bed_model.db.beds.update_one(
            {'bed_id': bed_id},
            {
                '$set': {
                    'status': 'occupied',
                    'current_patient_name': patient_name,
                    'check_in_date': datetime.now(),
                    'updated_at': datetime.now()
                }
            }
        )
        
        if update_result.modified_count > 0:
            return jsonify({
                'success': True,
                'message': f'Successfully allocated room for patient {patient_name}',
                'room_number': room_number,
                'bed_id': bed_id,
                'room_type': room_type,
                'status': 'allocated',
                'patient_name': patient_name
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to allocate room'}), 500
            
    except Exception as e:
        logging.error(f"Error allocating room: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@alexa_bp.route('/test-alexa-connection', methods=['GET'])
def test_alexa_connection():
    """Test endpoint to verify Alexa integration is working"""
    try:
        # Test database connection
        doctor_model = Doctor()
        appointment_model = Appointment()
        bed_model = Bed()
        
        doctor_count = doctor_model.db.doctors.count_documents({})
        appointment_count = appointment_model.db.appointments.count_documents({})
        bed_count = bed_model.db.beds.count_documents({})
        
        return jsonify({
            'success': True,
            'message': 'Alexa integration is working',
            'database_status': 'connected',
            'counts': {
                'doctors': doctor_count,
                'appointments': appointment_count,
                'beds': bed_count
            }
        })
    except Exception as e:
        logging.error(f"Error testing Alexa connection: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'database_status': 'disconnected'
        }), 500
