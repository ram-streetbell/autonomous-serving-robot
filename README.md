# Autonomous Serving Robot

A Linux/Raspberry Pi software stack for converting the existing differential-drive platform into an autonomous indoor serving robot.

## Current release

**v0.3.0 — Hardware Interface Ready**

The software stack now includes the complete ROS 2 control/navigation path plus a fail-safe ESP32 serial interface and tachometer odometry. The remaining step before a physical v1.0.0 release is commissioning the actual wiring and sensors on the robot.

## Included

- ROS 2 differential-drive bring-up
- Wheel-command kinematics and command timeout watchdog
- Robot URDF and TF structure
- SLAM Toolbox mapping launch
- Nav2 configuration and autonomy launch
- Named table/base serving missions
- JSON serving command interface with cancel/return
- Tablet browser control through rosbridge
- Linux control panel
- ESP32 serial motor interface
- Tachometer-based odometry
- One-command Ubuntu installer
- Unit tests and GitHub Actions checks
- Hardware commissioning documentation

## Hardware boundary

Target hardware is the existing robot with two BLDC Hall motors, Zbotic AI0179 controllers, ESP32, 2D LiDAR and IMU. The Zbotic controller uses a 0–5 V `VR` speed input, direction, enable, tachometer and Hall signals.

The ESP32 firmware deliberately ships with GPIO assignments disabled. A verified DAC or suitable filtered/level-shifted interface is required for the Zbotic `VR` input. Do not connect Raspberry Pi or ESP32 GPIO directly to an unverified 5 V signal.

## Quick start

```bash
git clone https://github.com/ram-streetbell/autonomous-serving-robot.git
cd autonomous-serving-robot
chmod +x scripts/install.sh
./scripts/install.sh
source ~/.robot_env
ros2 launch serving_robot bringup.launch.py
```

## Tablet control

Start rosbridge:

```bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

Open `tablet/index.html` on a tablet connected to the same network and set the Ubuntu machine address in the page. The interface supports manual motion, stop, table selection, return-to-base and status display.

## Mapping

Start the LiDAR driver, confirm `/scan`, and confirm the `odom -> base_link` TF chain. Then run:

```bash
ros2 launch slam_toolbox online_async_launch.py
```

Drive slowly under supervision and save the occupancy-grid map.

## Autonomous serving

After the map and physical parameters are verified:

```bash
ros2 launch serving_robot autonomy.launch.py map:=/path/to/map.yaml
```

Send a serving request:

```bash
ros2 topic pub --once /serving/command std_msgs/msg/String "{data: '{\"go\":\"table_1\"}'}"
```

Return to the kitchen/base:

```bash
ros2 topic pub --once /serving/command std_msgs/msg/String "{data: '{\"action\":\"return\"}'}"
```

Cancel the current mission:

```bash
ros2 topic pub --once /serving/command std_msgs/msg/String "{data: '{\"action\":\"cancel\"}'}"
```

Replace example waypoint coordinates with measured restaurant positions.

## Hardware bring-up

Program `firmware/esp32_motor_interface/esp32_motor_interface.ino`, verify `READY,DISABLED`, then configure the verified GPIO/interface wiring. Start the ROS hardware stack with:

```bash
ros2 launch serving_robot hardware.launch.py serial_port:=/dev/ttyUSB0 pulses_per_wheel_rev:=1.0
```

The default ESP32 configuration keeps motor outputs disabled. Determine the actual tachometer pulses per wheel revolution before enabling closed-loop odometry.

## Safety

Use a physical emergency-stop/enable path. First tests must be performed with drive wheels lifted. Keep motor power disconnected while checking signal levels and Hall wiring. Never assume Hall wire order or signal voltage. Do not enable autonomous navigation until manual stop, command timeout, tach feedback, LiDAR obstacle detection and odometry have all been verified.

## v1.0.0 completion gate

The repository software is ready for robot commissioning, but a physical v1.0.0 release requires these real-world checks:

1. Verify Zbotic wiring and Hall sequence for both motors.
2. Verify the 0–5 V speed interface electrically before connecting it.
3. Verify enable/direction and physical emergency stop.
4. Confirm tachometer pulses and set pulses-per-wheel-revolution.
5. Verify LiDAR `/scan` and sensor frame transforms.
6. Verify IMU topic/frame and orientation.
7. Calibrate wheel radius and wheel separation from measured motion.
8. Build and save a real restaurant map.
9. Test autonomous navigation at low speed with supervised obstacle checks.
10. Tune table approach poses and return-to-base behavior.
11. Run repeated serving missions before calling the robot v1.0.0.

## Project layout

```text
config/                         Robot parameters
launch/                         Mapping helpers
serving_robot/config/           Nav2 and robot parameters
serving_robot/launch/           ROS 2 launch files
serving_robot/serving_robot/    ROS 2 nodes
serving_robot/urdf/             Robot description
firmware/                       ESP32 low-level interface
scripts/                        Installer and Linux control panel
tablet/                         Browser control UI
docs/                           Hardware and release documentation
tests/                          Unit tests
.github/workflows/              Automated checks
```
