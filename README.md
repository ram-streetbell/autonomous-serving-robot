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

## Included

- ROS 2 differential-drive bring-up
- Wheel-command kinematics and odometry
- Zbotic integration boundary
- LiDAR/IMU diagnostics
- SLAM Toolbox mapping launch
- Nav2 integration entry point
- Linux control panel
- One-command Ubuntu installer
- Hardware commissioning documentation

## Quick start

```bash
git clone https://github.com/ram-streetbell/autonomous-serving-robot.git
cd autonomous-serving-robot
chmod +x scripts/install.sh
./scripts/install.sh
```

Run the base stack:

```bash
source ~/.robot_env
ros2 launch serving_robot bringup.launch.py
```

Open the simple Linux control panel in another terminal:

```bash
python3 scripts/control_gui.py
```

## Mapping

With a compatible LiDAR publishing `/scan` and a valid odometry/TF chain:

```bash
ros2 launch slam_toolbox online_async_launch.py
```

Drive slowly with the control panel and save the resulting map using the standard ROS 2 map-server tools.

## Architecture

```text
LiDAR + IMU -> ROS 2 -> SLAM -> map
                     |
cmd_vel -> motor bridge -> wheel targets -> Zbotic -> BLDC/Hall wheels
                     |
                  odometry
```

## Safety

Start with the wheels off the ground. Keep the physical motor-enable path disabled until the controller, Hall wiring and signal levels are verified. The software starts in a non-hardware-driving simulation mode and the command watchdog returns wheel targets to zero when commands time out.

## Current implementation boundary

The software side is now organized as the complete ROS 2 foundation, but final physical motor actuation cannot be honestly marked complete until the exact interface hardware, Hall order, motor pole/pulse relationship, LiDAR model and IMU model on the robot are verified. The Zbotic supplier specifically warns that Hall wire order can vary between motors and incorrect sequencing can cause abnormal operation or excessive current.

## Project layout

```text
config/                 Robot parameters
launch/                 ROS 2 launch files
serving_robot/          Python ROS 2 package
scripts/                Installer and Linux control panel
docs/                   Hardware integration notes
.github/workflows/      Automated syntax checks
```
