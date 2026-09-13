# Autonomous Serving Robot

A Linux/Raspberry Pi software stack for converting the existing differential-drive RC-style platform into an autonomous mapping and navigation robot.

## Target hardware

- Raspberry Pi or Ubuntu Linux computer
- Two 6-inch BLDC hoverboard-style Hall motors
- One Zbotic AI0179 12–36 V / 500 W Hall BLDC controller per motor
- 2D LiDAR supported by ROS 2 `sensor_msgs/LaserScan`
- IMU supported by ROS 2 `sensor_msgs/Imu`
- Optional ESP32 for low-level GPIO/level shifting

The Zbotic AI0179 exposes `VR` (0–5 V speed), `ZF` (direction), `EL` (enable), `M` (tachometer pulse), and Hall inputs. Its published specification is 12–36 V, <=15 A and <=500 W. **Do not connect Raspberry Pi GPIO directly to a 5 V signal.** Use appropriate level shifting/isolation and verify the actual board wiring before applying power.

## What this repository provides

- ROS 2 robot bring-up structure
- Differential-drive kinematics and odometry node
- Configurable Zbotic motor-controller interface
- LiDAR/IMU topic diagnostics
- SLAM Toolbox launch configuration
- Nav2 launch/configuration entry points
- Safe startup and emergency-stop behavior
- A lightweight Linux control GUI/API
- Hardware and software self-test scripts
- One-command installation path

## Architecture

```text
                 +----------------------+
                 | Linux / Raspberry Pi |
                 |     ROS 2            |
                 +----------+-----------+
                            |
             +--------------+--------------+
             |              |              |
          LiDAR           IMU        Robot controller
             |              |              |
             +-------+------+              |
                     |                     |
                   SLAM                 cmd_vel
                     |                     |
                    Map              motor_bridge
                     |                     |
                 Nav2 planner              |
                     |                     |
                  cmd_vel                  |
                     +----------+----------+
                                |
                    +-----------+-----------+
                    |                       |
              Left Zbotic             Right Zbotic
                    |                       |
              Left BLDC/Hall          Right BLDC/Hall
```

## Quick start

On Ubuntu 22.04/24.04:

```bash
git clone https://github.com/ram-streetbell/autonomous-serving-robot.git
cd autonomous-serving-robot
chmod +x scripts/install.sh
./scripts/install.sh
```

Then configure `config/robot.yaml` and run:

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
source ~/autonomous_serving_robot_ws/install/setup.bash
ros2 launch serving_robot bringup.launch.py
```

## Safety

Start with wheels off the ground. Keep the hardware enable line disabled until the controller and sensor wiring has been verified. The software defaults to zero velocity and contains a watchdog that stops motion when command messages time out.

## Current implementation boundary

The software is deliberately hardware-configurable. Exact Hall wire order, motor pole/pulse relationship, controller signal voltage behavior, LiDAR model and IMU model must be verified on the physical robot before autonomous driving. The Zbotic product page itself warns that Hall wire order can vary between motor manufacturers and incorrect wiring can cause abnormal startup or excessive current.

## Project layout

```text
config/                 Robot parameters
launch/                 ROS 2 launch files
serving_robot/          Python ROS 2 nodes
scripts/                Installer and hardware diagnostics
systemd/                Optional auto-start service
docs/                   Hardware/software notes
```
