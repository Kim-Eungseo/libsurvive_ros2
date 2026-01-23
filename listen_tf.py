#!/usr/bin/env python3
"""
Foxglove WebSocket으로 /tf 토픽을 구독하는 간단한 예제
"""
import asyncio
import json
import websockets

async def listen_tf():
    uri = "ws://localhost:8765"
    
    async with websockets.connect(uri) as websocket:
        # Foxglove WebSocket 프로토콜: 구독 요청
        subscribe_msg = {
            "op": "subscribe",
            "subscriptions": [
                {
                    "id": 1,
                    "topic": "/tf"
                }
            ]
        }
        
        await websocket.send(json.dumps(subscribe_msg))
        print(f"Connected to {uri}")
        print("Listening to /tf topic...")
        print("-" * 60)
        
        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                if data.get("op") == "message":
                    # TF 데이터 파싱
                    msg_data = data.get("message", {})
                    transforms = msg_data.get("transforms", [])
                    
                    for tf in transforms:
                        frame_id = tf.get("header", {}).get("frame_id")
                        child_frame = tf.get("child_frame_id")
                        translation = tf.get("transform", {}).get("translation", {})
                        
                        print(f"Frame: {frame_id} -> {child_frame}")
                        print(f"  Position: x={translation.get('x', 0):.4f}, "
                              f"y={translation.get('y', 0):.4f}, "
                              f"z={translation.get('z', 0):.4f}")
                        print("-" * 60)
                        
        except KeyboardInterrupt:
            print("\nStopping...")

if __name__ == "__main__":
    print("Foxglove WebSocket TF Listener")
    print("Press Ctrl+C to stop")
    asyncio.run(listen_tf())
