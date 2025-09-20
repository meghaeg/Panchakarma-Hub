#!/usr/bin/env python3
"""
Simple WebSocket server for testing
"""
import asyncio
import websockets
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def websocket_handler(websocket, path):
    """Handle WebSocket connections"""
    logger.info(f"Client connected: {websocket.remote_address}")
    try:
        # Send welcome message
        welcome_message = {
            'type': 'welcome',
            'message': 'Connected to Panchakarma WebSocket server',
            'timestamp': datetime.now().isoformat()
        }
        await websocket.send(json.dumps(welcome_message))
        logger.info("Welcome message sent")
        
        # Keep connection alive and handle messages
        async for message in websocket:
            try:
                data = json.loads(message)
                logger.info(f"Received message: {data}")
                
                # Echo back the message
                response = {
                    'type': 'echo',
                    'original': data,
                    'timestamp': datetime.now().isoformat()
                }
                await websocket.send(json.dumps(response))
                
            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info(f"Client {websocket.remote_address} disconnected")

async def main():
    """Start the WebSocket server"""
    logger.info("Starting simple WebSocket server on localhost:8765")
    
    try:
        async with websockets.serve(websocket_handler, "localhost", 8765):
            logger.info("WebSocket server started successfully")
            logger.info("Press Ctrl+C to stop the server")
            await asyncio.Future()  # Run forever
    except Exception as e:
        logger.error(f"Failed to start WebSocket server: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("WebSocket server stopped by user")
    except Exception as e:
        logger.error(f"WebSocket server error: {e}")
