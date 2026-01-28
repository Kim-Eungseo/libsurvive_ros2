#!/usr/bin/env python3
"""
TF Listener using rosbridge (port 9090)

Usage:
    python3 tf_listener.py
"""
import roslibpy
import time


# 마지막으로 받은 TF 데이터 저장
latest_tf = {}
latest_tf_static = {}


def main():
    # rosbridge에 연결
    client = roslibpy.Ros(host='localhost', port=9090)
    client.run()
    
    print(f'Connected to rosbridge: {client.is_connected}')
    
    if not client.is_connected:
        print('Failed to connect. Is rosbridge running on port 9090?')
        return
    
    # TF 토픽 구독 (데이터만 저장)
    def tf_callback(msg):
        for transform in msg['transforms']:
            frame = transform['child_frame_id']
            latest_tf[frame] = transform
    
    tf_listener = roslibpy.Topic(client, '/tf', 'tf2_msgs/TFMessage')
    tf_listener.subscribe(tf_callback)
    print('Subscribed to /tf topic. Waiting for data...\n')
    
    # tf_static도 구독 (라이트하우스 위치 등)
    def tf_static_callback(msg):
        for transform in msg['transforms']:
            frame = transform['child_frame_id']
            latest_tf_static[frame] = transform
    
    tf_static_listener = roslibpy.Topic(client, '/tf_static', 'tf2_msgs/TFMessage')
    tf_static_listener.subscribe(tf_static_callback)
    
    try:
        while client.is_connected:
            # 2초마다 출력
            time.sleep(2)
            
            # TF Static 출력
            if latest_tf_static:
                print('=== TF Static ===')
                for frame, transform in latest_tf_static.items():
                    parent = transform['header']['frame_id']
                    t = transform['transform']['translation']
                    print(f'  [{frame}] <- [{parent}]: ({t["x"]:.4f}, {t["y"]:.4f}, {t["z"]:.4f})')
                print()
            
            # TF 출력
            if latest_tf:
                print('=== TF (Dynamic) ===')
                for frame, transform in latest_tf.items():
                    parent = transform['header']['frame_id']
                    t = transform['transform']['translation']
                    r = transform['transform']['rotation']
                    print(f'[{frame}] <- [{parent}]')
                    print(f'  pos: x={t["x"]:.4f}, y={t["y"]:.4f}, z={t["z"]:.4f}')
                    print(f'  rot: x={r["x"]:.4f}, y={r["y"]:.4f}, z={r["z"]:.4f}, w={r["w"]:.4f}')
                print()
            
            print('-' * 50)
            
    except KeyboardInterrupt:
        print('\nShutting down...')
    
    tf_listener.unsubscribe()
    tf_static_listener.unsubscribe()
    client.terminate()
    print('Disconnected.')


if __name__ == '__main__':
    main()
