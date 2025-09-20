"""
WebSocket server for real-time dashboard updates
Integrates with Alexa Lambda functions to provide live updates
"""
import asyncio
import websockets
import json
import logging
from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import threading
import time
from typing import Dict, Set, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self, mongodb_uri: str, db_name: str):
        self.mongodb_uri = mongodb_uri
        self.db_name = db_name
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.db: Database = None
        self.change_streams: Dict[str, Any] = {}
        self.running = False
        
    async def connect_to_mongodb(self):
        """Connect to MongoDB and setup change streams"""
        try:
            client = MongoClient(self.mongodb_uri)
            self.db = client[self.db_name]
            logger.info(f"Connected to MongoDB database: {self.db_name}")
            
            # Setup change streams for real-time updates
            await self.setup_change_streams()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def setup_change_streams(self):
        """Setup MongoDB change streams for real-time updates"""
        try:
            # Watch for changes in doctors collection
            doctors_stream = self.db.doctors.watch([
                {'$match': {'operationType': {'$in': ['insert', 'update', 'delete']}}}
            ])
            self.change_streams['doctors'] = doctors_stream
            
            # Watch for changes in appointments collection
            appointments_stream = self.db.appointments.watch([
                {'$match': {'operationType': {'$in': ['insert', 'update', 'delete']}}}
            ])
            self.change_streams['appointments'] = appointments_stream
            
            # Watch for changes in beds collection
            beds_stream = self.db.beds.watch([
                {'$match': {'operationType': {'$in': ['insert', 'update', 'delete']}}}
            ])
            self.change_streams['beds'] = beds_stream
            
            logger.info("Change streams setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup change streams: {e}")
            raise
    
    async def register_client(self, websocket, path):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        try:
            # Send initial data to the client
            await self.send_initial_data(websocket)
            
            # Keep connection alive
            await websocket.wait_closed()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
    
    async def send_initial_data(self, websocket):
        """Send initial dashboard data to a new client"""
        try:
            # Get current statistics
            stats = await self.get_dashboard_stats()
            
            message = {
                'type': 'initial_data',
                'data': stats,
                'timestamp': datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(message))
            
        except Exception as e:
            logger.error(f"Error sending initial data: {e}")
    
    async def get_dashboard_stats(self):
        """Get current dashboard statistics"""
        try:
            # Get doctor statistics
            total_doctors = self.db.doctors.count_documents({'status': 'active'})
            recent_doctors = list(self.db.doctors.find(
                {'status': 'active'}, 
                {'name': 1, 'specialization': 1, 'created_at': 1}
            ).sort('created_at', -1).limit(5))
            
            # Get appointment statistics
            total_appointments = self.db.appointments.count_documents({})
            today_appointments = self.db.appointments.count_documents({
                'appointment_date': {
                    '$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                    '$lt': datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
                }
            })
            
            # Get bed statistics
            total_beds = self.db.beds.count_documents({})
            available_beds = self.db.beds.count_documents({'status': 'available'})
            occupied_beds = self.db.beds.count_documents({'status': 'occupied'})
            
            # Get recent activities
            recent_activities = []
            
            # Recent doctor additions
            recent_doctor_additions = list(self.db.doctors.find(
                {'created_at': {'$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}},
                {'name': 1, 'created_at': 1, 'specialization': 1}
            ).sort('created_at', -1).limit(3))
            
            for doc in recent_doctor_additions:
                recent_activities.append({
                    'type': 'doctor_added',
                    'message': f"New doctor {doc['name']} added",
                    'timestamp': doc['created_at'].isoformat(),
                    'details': {
                        'specialization': doc.get('specialization', 'Unknown'),
                        'doctor_id': doc.get('_id')
                    }
                })
            
            # Recent appointments
            recent_appointments = list(self.db.appointments.find(
                {'created_at': {'$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}},
                {'patient_id': 1, 'doctor_id': 1, 'created_at': 1, 'status': 1}
            ).sort('created_at', -1).limit(3))
            
            for apt in recent_appointments:
                # Get patient and doctor names
                patient = self.db.patients.find_one({'patient_id': apt['patient_id']}, {'name': 1})
                doctor = self.db.doctors.find_one({'doctor_id': apt['doctor_id']}, {'name': 1})
                
                recent_activities.append({
                    'type': 'appointment_created',
                    'message': f"Appointment created for {patient['name'] if patient else 'Unknown'} with {doctor['name'] if doctor else 'Unknown'}",
                    'timestamp': apt['created_at'].isoformat(),
                    'details': {
                        'status': apt.get('status', 'Unknown'),
                        'appointment_id': apt.get('_id')
                    }
                })
            
            # Recent bed allocations
            recent_bed_changes = list(self.db.beds.find(
                {'updated_at': {'$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}},
                {'bed_id': 1, 'room_number': 1, 'status': 1, 'current_patient_name': 1, 'updated_at': 1}
            ).sort('updated_at', -1).limit(3))
            
            for bed in recent_bed_changes:
                if bed['status'] == 'occupied' and bed.get('current_patient_name'):
                    recent_activities.append({
                        'type': 'bed_allocated',
                        'message': f"Bed {bed['room_number']} allocated to {bed['current_patient_name']}",
                        'timestamp': bed['updated_at'].isoformat(),
                        'details': {
                            'bed_id': bed['bed_id'],
                            'room_number': bed['room_number']
                        }
                    })
            
            return {
                'doctors': {
                    'total': total_doctors,
                    'recent': recent_doctors
                },
                'appointments': {
                    'total': total_appointments,
                    'today': today_appointments
                },
                'beds': {
                    'total': total_beds,
                    'available': available_beds,
                    'occupied': occupied_beds,
                    'occupancy_rate': round((occupied_beds / total_beds * 100) if total_beds > 0 else 0, 2)
                },
                'recent_activities': recent_activities
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {}
    
    async def broadcast_update(self, update_type: str, data: Any):
        """Broadcast update to all connected clients"""
        if not self.clients:
            return
        
        message = {
            'type': 'update',
            'update_type': update_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to all connected clients
        disconnected_clients = set()
        for client in self.clients:
            try:
                await client.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"Error sending update to client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected_clients
    
    async def process_change_stream(self, collection_name: str, change_stream):
        """Process changes from MongoDB change stream"""
        try:
            async for change in change_stream:
                logger.info(f"Change detected in {collection_name}: {change['operationType']}")
                
                # Process different types of changes
                if change['operationType'] == 'insert':
                    await self.handle_insert(collection_name, change)
                elif change['operationType'] == 'update':
                    await self.handle_update(collection_name, change)
                elif change['operationType'] == 'delete':
                    await self.handle_delete(collection_name, change)
                    
        except Exception as e:
            logger.error(f"Error processing change stream for {collection_name}: {e}")
    
    async def handle_insert(self, collection_name: str, change):
        """Handle insert operations"""
        if collection_name == 'doctors':
            doc = change['fullDocument']
            await self.broadcast_update('doctor_added', {
                'doctor_id': doc.get('doctor_id'),
                'name': doc.get('name'),
                'specialization': doc.get('specialization'),
                'centre_id': doc.get('centre_id')
            })
        
        elif collection_name == 'appointments':
            doc = change['fullDocument']
            await self.broadcast_update('appointment_created', {
                'appointment_id': doc.get('appointment_id'),
                'patient_id': doc.get('patient_id'),
                'doctor_id': doc.get('doctor_id'),
                'status': doc.get('status')
            })
        
        elif collection_name == 'beds':
            doc = change['fullDocument']
            await self.broadcast_update('bed_added', {
                'bed_id': doc.get('bed_id'),
                'room_number': doc.get('room_number'),
                'bed_type': doc.get('bed_type')
            })
    
    async def handle_update(self, collection_name: str, change):
        """Handle update operations"""
        if collection_name == 'beds':
            doc_id = change['documentKey']['_id']
            updated_fields = change.get('updateDescription', {}).get('updatedFields', {})
            
            if 'status' in updated_fields:
                bed = self.db.beds.find_one({'_id': doc_id})
                if bed:
                    await self.broadcast_update('bed_status_changed', {
                        'bed_id': bed.get('bed_id'),
                        'room_number': bed.get('room_number'),
                        'status': bed.get('status'),
                        'patient_name': bed.get('current_patient_name')
                    })
        
        elif collection_name == 'appointments':
            doc_id = change['documentKey']['_id']
            updated_fields = change.get('updateDescription', {}).get('updatedFields', {})
            
            if 'status' in updated_fields:
                appointment = self.db.appointments.find_one({'_id': doc_id})
                if appointment:
                    await self.broadcast_update('appointment_status_changed', {
                        'appointment_id': appointment.get('appointment_id'),
                        'status': appointment.get('status'),
                        'patient_id': appointment.get('patient_id'),
                        'doctor_id': appointment.get('doctor_id')
                    })
    
    async def handle_delete(self, collection_name: str, change):
        """Handle delete operations"""
        if collection_name == 'doctors':
            await self.broadcast_update('doctor_removed', {
                'doctor_id': change.get('documentKey', {}).get('_id')
            })
        
        elif collection_name == 'appointments':
            await self.broadcast_update('appointment_cancelled', {
                'appointment_id': change.get('documentKey', {}).get('_id')
            })
    
    async def start_change_stream_processing(self):
        """Start processing change streams in background"""
        tasks = []
        for collection_name, change_stream in self.change_streams.items():
            task = asyncio.create_task(
                self.process_change_stream(collection_name, change_stream)
            )
            tasks.append(task)
        
        # Wait for all tasks to complete (they run indefinitely)
        await asyncio.gather(*tasks)
    
    async def start_server(self, host='localhost', port=8765):
        """Start the WebSocket server"""
        try:
            await self.connect_to_mongodb()
            
            # Start change stream processing in background
            asyncio.create_task(self.start_change_stream_processing())
            
            # Start WebSocket server
            logger.info(f"Starting WebSocket server on {host}:{port}")
            async with websockets.serve(self.register_client, host, port):
                self.running = True
                logger.info("WebSocket server started successfully")
                await asyncio.Future()  # Run forever
                
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            raise

def main():
    """Main function to start the WebSocket server"""
    try:
        # Test the connection first using the same method as Flask app
        from utils import get_db_connection
        db = get_db_connection()
        logger.info(f"Connected to MongoDB database: {db.name}")
        
        # For now, let's use a simple approach - just test if we can connect
        # and then start the WebSocket server without MongoDB change streams
        logger.info("Starting WebSocket server in simple mode...")
        
        # Start a simple WebSocket server without MongoDB change streams
        async def simple_websocket_handler(websocket, path):
            logger.info(f"Client connected: {websocket.remote_address}")
            try:
                # Send a welcome message
                await websocket.send(json.dumps({
                    'type': 'welcome',
                    'message': 'Connected to Panchakarma WebSocket server',
                    'timestamp': datetime.now().isoformat()
                }))
                
                # Keep connection alive
                await websocket.wait_closed()
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                logger.info(f"Client disconnected: {websocket.remote_address}")
        
        async def start_simple_server():
            logger.info("Starting simple WebSocket server on localhost:8765")
            async with websockets.serve(simple_websocket_handler, "localhost", 8765):
                logger.info("WebSocket server started successfully")
                await asyncio.Future()  # Run forever
        
        asyncio.run(start_simple_server())
        
    except KeyboardInterrupt:
        logger.info("WebSocket server stopped by user")
    except Exception as e:
        logger.error(f"WebSocket server error: {e}")

if __name__ == "__main__":
    main()
