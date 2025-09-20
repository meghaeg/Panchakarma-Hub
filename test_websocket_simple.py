#!/usr/bin/env python3
"""
Simple WebSocket server test
"""
import asyncio
import websockets
import json

async def test_websocket():
    """Test WebSocket connection"""
    try:
        print("🔍 Testing WebSocket connection...")
        
        async with websockets.connect("ws://localhost:8765") as websocket:
            print("✅ WebSocket connected successfully")
            
            # Wait for any messages
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📨 Received message: {data.get('type', 'unknown')}")
                print("✅ WebSocket communication working")
            except asyncio.TimeoutError:
                print("⚠️  No message received within 5 seconds (this is normal)")
                print("✅ WebSocket connection established")
            
    except ConnectionRefusedError:
        print("❌ WebSocket server is not running")
        print("   Start it with: python websocket_server.py")
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
