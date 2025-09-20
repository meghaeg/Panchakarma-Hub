#!/usr/bin/env python3
"""
Basic WebSocket test without complex server
"""
import asyncio
import websockets
import json

async def test_basic_websocket():
    """Test basic WebSocket functionality"""
    try:
        print("🔍 Testing basic WebSocket functionality...")
        
        # Create a simple echo server
        async def echo_handler(websocket, path):
            print(f"Client connected: {websocket.remote_address}")
            try:
                async for message in websocket:
                    print(f"Received: {message}")
                    await websocket.send(f"Echo: {message}")
            except websockets.exceptions.ConnectionClosed:
                print("Client disconnected")
        
        # Start server
        print("Starting echo server on localhost:8765...")
        async with websockets.serve(echo_handler, "localhost", 8765):
            print("✅ WebSocket server started successfully")
            print("Server is running. Press Ctrl+C to stop.")
            
            # Keep running
            await asyncio.Future()
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(test_basic_websocket())
    except KeyboardInterrupt:
        print("\n✅ WebSocket server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
