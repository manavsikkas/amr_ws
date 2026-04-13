# AMR Safety Guard System

An autonomous mobile robot (AMR) safety system that patrols an industrial environment, detects humans in danger zones using YOLOv8, and triggers an emergency stop.

## System Architecture

```
Gazebo Simulation (Laptop)          Jetson Orin Nano
├── Industrial world                ├── USB Webcam
├── Custom AMR robot (URDF)         ├── YOLOv8n person detection
├── SLAM-generated map              ├── ROS2 Humble (Docker)
├── Nav2 autonomous patrol          └── amr_perception package
├── Keepout zones (danger areas)
├── Zone monitor
└── Emergency stop node
```

## Features

- **Autonomous Patrol** — robot follows a 4-waypoint rectangular path continuously
- **Keepout Zones** — Nav2 costmap filter blocks the robot from entering defined danger areas
- **Zone Monitor** — detects when the robot enters a danger zone via odometry
- **Person Detection** — YOLOv8n detects humans in real-time from webcam feed
- **Emergency Stop** — robot halts for 5 seconds on person detection, then resumes patrol
- **Missed Waypoint Logging** — identifies whether a missed waypoint was blocked by path or danger zone

## Stack

| Component | Technology |
|---|---|
| Simulation | Gazebo Harmonic |
| Navigation | ROS2 Jazzy + Nav2 |
| Mapping | SLAM Toolbox |
| Perception | YOLOv8n + cv_bridge |
| Compute (perception) | NVIDIA Jetson Orin Nano |
| Robot OS (Jetson) | ROS2 Humble (Docker) |
| GPU Inference | CUDA 12.6 + PyTorch 2.4 |

## Package Structure

```
amr_safety_guard/
├── amr_safety_guard/
│   ├── patrol_node.py        # Autonomous waypoint patrol (Nav2 action client)
│   ├── zone_monitor.py       # Danger zone detection via /odom
│   ├── emergency_stop.py     # Stops robot 5s on person detection
│   ├── person_detector.py    # YOLOv8 inference on camera feed
│   └── webcam_publisher.py   # Publishes webcam frames to ROS2
├── launch/
│   ├── navigation.launch.py  # Full system launch
│   ├── simulation.launch.py  # Gazebo + robot spawn
│   ├── slam.launch.py        # SLAM mapping
│   └── rsp.launch.py         # Robot state publisher
├── config/
│   ├── nav2_params.yaml
│   └── mapper_params_online_async.yaml
├── maps/                     # SLAM-generated industrial map + keepout mask
├── urdf/                     # Custom AMR robot URDF/xacro
└── worlds/                   # Industrial Gazebo world

jetson/
└── Dockerfile.perception     # Jetson container: PyTorch + ROS2 Humble + YOLOv8
```

## Running the Simulation

```bash
# Build
cd ~/amr_ws
colcon build --packages-select amr_safety_guard
source install/setup.bash

# Launch full system
ros2 launch amr_safety_guard navigation.launch.py

# Manually trigger emergency stop (for testing)
ros2 topic pub /person_detected std_msgs/msg/String "data: 'Human detected: 0.95'" --once
```

## Jetson Setup (Perception)

```bash
# Build perception container
docker build --network host -t amr_perception:latest -f jetson/Dockerfile.perception .

# Run with GPU + webcam
docker run -it --rm --runtime nvidia --network host \
  --device /dev/video0 \
  -v ~/amr_ws:/workspace \
  amr_perception:latest bash

# Inside container
colcon build --packages-select amr_perception
source install/setup.bash
ros2 run amr_perception person_detector
```

## Hardware

- Gaming laptop (WSL2 Ubuntu 24.04) — simulation and navigation
- NVIDIA Jetson Orin Nano — real-time person detection
- USB webcam — camera input for YOLOv8
- Arduino Uno + L298N — hardware emergency stop (ongoing)