#!/bin/bash
set -e

# 캘리브레이션 디렉토리 생성
mkdir -p /root/.config/libsurvive

# RECALIBRATE 환경변수가 true면 캘리브레이션 파일 삭제
if [ "$RECALIBRATE" = "true" ]; then
    echo "🔄 Forcing recalibration - removing old calibration data..."
    rm -f /root/.config/libsurvive/config.json
else
    if [ -f /root/.config/libsurvive/config.json ]; then
        echo "✅ Using existing calibration data"
    else
        echo "📍 No calibration found - starting new calibration..."
    fi
fi

# ROS2 환경 설정
source /home/ros/ros2_ws/install/setup.bash

# 전달된 명령어 실행
exec "$@"
