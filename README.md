# Autonomous Serving Robot

A Linux/Raspberry Pi software stack for converting the existing differential-drive platform into an autonomous indoor serving robot.

## Target hardware

- Raspberry Pi or Ubuntu Linux computer
- Two BLDC Hall motors
- Zbotic AI0179 12–36 V / 500 W Hall BLDC controller per motor
- 2D LiDAR publishing `sensor_msgs/LaserScan`
- IMU publishing `sensor_msgs/Imu`
- Optional ESP32 for low-level GPIO, DAC and level shifting

The Zbotic AI0179 exposes `VR` (0–5 V speed), `ZF` (direction), `EL` (enable), `M` (tachometer pulse), and Hall inputs. Do not connect Raspberry Pi GPIO directly to a 5 V signal. Use appropriate interface circuitry and verify wiring before applying power.

## Current release

**v0.2.0 — Autonomous Navigation Foundation**

Included in this release:

- ROS 2 differential-drive bring-up
- Wheel-command kinematics and safety watchdog
- Odometry framework
- Robot URDF and TF structure
- LiDAR/IMU diagnostics
- SLAM Toolbox mapping launch
- Nav2 configuration and autonomy launch
- Table/base waypoint mission manager
- JSON serving command interface
- Tablet browser control UI through rosbridge
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

For tablet control, start rosbridge:

```bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

Then open `tablet/index.html` from a device that can reach the Ubuntu machine. The tablet page can send manual `/cmd_vel` commands and serving waypoint commands.

## Mapping

With a compatible LiDAR publishing `/scan` and a valid odometry/TF chain:

```bash
ros2 launch slam_toolbox online_async_launch.py
```

Drive slowly under supervision and save the map with ROS 2 map-server tools.

## Autonomous navigation

After a map has been saved and the robot dimensions/sensors have been verified:

```bash
ros2 launch serving_robot autonomy.launch.py map:=/path/to/map.yaml
```

The serving waypoint interface accepts JSON on `/serving/command`:

```bash
ros2 topic pub --once /serving/command std_msgs/msg/String "{data: '{\"go\":\"table_1\"}'}"
```

Default example waypoints are `table_1`, `table_2`, and `base`. Replace them with measured restaurant coordinates before real operation.

## Architecture

```text
LiDAR + IMU -> ROS 2 -> SLAM/Nav2 -> map + path
                              |
cmd_vel -> motor bridge -> low-level interface -> Zbotic -> BLDC/Hall wheels
                              |
                           odometry
                              |
Tablet -> rosbridge -> /cmd_vel and /serving/command
```

## Safety

Start with the wheels off the ground. Keep the physical motor-enable path disabled until the controller, Hall wiring and signal levels are verified. The current motor bridge deliberately operates as a safe software simulation interface and does not directly energize the motors.

## Hardware-gated completion

The software foundation is substantially built, but physical autonomy is not marked complete until the actual motor interface, Hall/tach feedback, LiDAR, IMU, wheel dimensions and electrical safety path are verified on the robot and tested under supervision.
