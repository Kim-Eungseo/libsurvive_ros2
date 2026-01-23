# 🌍 방 좌표계 설정 가이드

## 문제 상황

libsurvive는 베이스 스테이션 위치를 자동으로 계산하지만:
- ❌ `libsurvive_world` 프레임의 **방향이 임의로** 설정됨
- ❌ 방의 실제 좌표계(예: 북쪽, 정면)와 **일치하지 않음**
- ❌ 트래커 초기 위치/방향에 따라 매번 달라질 수 있음

## ✅ 해결: Static Transform 설정

`world` 프레임 → `libsurvive_world` 프레임 변환을 추가하여 방 좌표계에 맞춥니다.

---

## 🎯 방법 1: Launch Argument 사용 (권장)

### 기본 사용 (회전 없음)

```bash
docker compose up -d
# world 프레임이 libsurvive_world와 동일
```

### 90도 회전 (예: Y축 기준)

```bash
# docker-compose.yml의 command 수정 또는
# 컨테이너 내에서:
docker compose exec libsurvive_ros2 bash -c \
  "source /home/ros/ros2_ws/install/setup.bash && \
   ros2 launch libsurvive_ros2 libsurvive_ros2.launch.py \
   foxbridge:=true world_yaw:=1.5708"
# 1.5708 radians = 90 degrees
```

### 커스텀 좌표계 설정

```bash
# 예: 방 정면을 libsurvive의 +X 방향으로 맞추기
ros2 launch libsurvive_ros2 libsurvive_ros2.launch.py \
  foxbridge:=true \
  world_x:=0.0 \
  world_y:=0.0 \
  world_z:=0.0 \
  world_roll:=0.0 \
  world_pitch:=0.0 \
  world_yaw:=1.5708  # 90도 회전
```

---

## 🔧 방법 2: docker-compose.yml 수정

원하는 좌표계를 기본값으로 설정:

### 1. docker-compose.yml 편집

```yaml
services:
  libsurvive_ros2:
    # ... 기존 설정 ...
    command: >
      ros2 launch libsurvive_ros2 libsurvive_ros2.launch.py
      foxbridge:=true
      composable:=false
      world_frame:=world
      world_yaw:=1.5708
```

### 2. 컨테이너 재시작

```bash
docker compose down
docker compose up -d
```

---

## 📐 좌표계 정렬 방법

### 1단계: 현재 libsurvive_world 방향 확인

Foxglove Studio에서:
```
https://studio.foxglove.dev/?ds=foxglove-websocket&ds.url=ws://localhost:8765
```

1. 3D 패널 추가
2. TF 표시 활성화
3. `libsurvive_world` 축 확인:
   - 빨강: +X
   - 초록: +Y
   - 파랑: +Z

### 2단계: 방 좌표계 정의

```
예시: 방 정면을 +Y로 설정하고 싶다면
       
방 레이아웃:
┌──────────────────┐
│                  │
│  방 정면 (+Y)    │
│       ↑          │
│       │          │
│       O──→ +X    │
│      /           │
│    +Z            │
└──────────────────┘
```

### 3단계: 필요한 회전 계산

libsurvive_world에서 방 좌표계로 변환하는 회전 계산:

**Yaw (Z축 회전):**
- 0°: 변화 없음
- 90° (1.5708 rad): 반시계방향 90도
- 180° (3.1416 rad): 180도 회전
- -90° (-1.5708 rad): 시계방향 90도

**Roll, Pitch:**
- 대부분 0으로 유지
- 바닥이 기울어진 경우에만 조정

---

## 🎮 실시간 테스트

### 방법 1: 별도 터미널에서 테스트

```bash
# 현재 실행 중인 상태에서 추가 publish
docker compose exec libsurvive_ros2 bash -c \
  "source /home/ros/ros2_ws/install/setup.bash && \
   ros2 run tf2_ros static_transform_publisher \
   0 0 0 0 0 1.5708 world libsurvive_world"
```

Foxglove에서 실시간으로 확인하며 각도 조정

### 방법 2: rqt_tf_tree로 확인

```bash
docker compose exec libsurvive_ros2 bash -c \
  "source /home/ros/ros2_ws/install/setup.bash && \
   ros2 run tf2_tools view_frames"
# frames.pdf 생성됨
```

---

## 📊 Launch Arguments 전체 목록

| Argument | Default | 설명 |
|----------|---------|------|
| `world_frame` | `world` | 부모 프레임 이름 |
| `world_x` | `0.0` | X 이동 (미터) |
| `world_y` | `0.0` | Y 이동 (미터) |
| `world_z` | `0.0` | Z 이동 (미터) |
| `world_roll` | `0.0` | Roll 회전 (라디안) |
| `world_pitch` | `0.0` | Pitch 회전 (라디안) |
| `world_yaw` | `0.0` | Yaw 회전 (라디안) |

---

## 💡 팁

### 각도 변환 (도 → 라디안)

```python
# Python으로 계산
import math
degrees = 90
radians = math.radians(degrees)
print(radians)  # 1.5707963267948966
```

### 자주 사용하는 각도

- 0° = 0.0 rad
- 45° = 0.7854 rad
- 90° = 1.5708 rad
- 180° = 3.1416 rad
- 270° = 4.7124 rad
- -90° = -1.5708 rad

### TF 트리 확인

```bash
# 실시간 TF 관계 확인
docker compose exec libsurvive_ros2 bash -c \
  "source /home/ros/ros2_ws/install/setup.bash && \
   ros2 run tf2_ros tf2_echo world libsurvive_world"
```

---

## 🎯 예시: 일반적인 설정

### 예시 1: 방 정면이 libsurvive +Y

```yaml
# docker-compose.yml
command: >
  ros2 launch libsurvive_ros2 libsurvive_ros2.launch.py
  foxbridge:=true
  world_yaw:=0.0  # 회전 없음
```

### 예시 2: 방 정면이 libsurvive +X

```yaml
# docker-compose.yml
command: >
  ros2 launch libsurvive_ros2 libsurvive_ros2.launch.py
  foxbridge:=true
  world_yaw:=-1.5708  # -90도 회전
```

### 예시 3: 바닥이 아닌 벽 기준

```yaml
# docker-compose.yml
command: >
  ros2 launch libsurvive_ros2 libsurvive_ros2.launch.py
  foxbridge:=true
  world_pitch:=1.5708  # 90도 기울임
```

---

## ✅ 최종 확인

좌표계가 올바르게 설정되었는지 확인:

1. **Foxglove Studio** 3D 뷰에서 축 방향 확인
2. **트래커 움직임** 방향과 표시된 축이 일치하는지 확인
3. **world → libsurvive_world → 트래커** TF 체인 확인

```bash
# TF 체인 확인
docker compose exec libsurvive_ros2 bash -c \
  "source /home/ros/ros2_ws/install/setup.bash && \
   ros2 run tf2_tools view_frames && \
   cat frames.gv"
```

---

## 📁 설정 저장

올바른 좌표계를 찾았다면 `docker-compose.yml`에 저장:

```yaml
services:
  libsurvive_ros2:
    build: .
    network_mode: host
    devices:
      - /dev/bus/usb:/dev/bus/usb
    privileged: true
    user: root
    volumes:
      - ./calibration:/root/.config/libsurvive
      - ./entrypoint_recalibrate.sh:/entrypoint_recalibrate.sh:ro
    entrypoint: /entrypoint_recalibrate.sh
    working_dir: /home/ros/ros2_ws
    command: >
      ros2 launch libsurvive_ros2 libsurvive_ros2.launch.py
      foxbridge:=true
      composable:=false
      world_yaw:=1.5708
    environment:
      - RECALIBRATE=${RECALIBRATE:-false}
```

이제 `docker compose up -d`로 항상 올바른 좌표계로 시작됩니다! 🎉
