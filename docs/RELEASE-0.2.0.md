# v0.2.0 — Autonomous Navigation Foundation

This release advances the project from a basic ROS 2 bring-up to an autonomy-ready software foundation.

## Added

- Nav2 configuration for indoor differential-drive navigation
- Autonomous navigation launch entry point
- Robot URDF with configurable base, wheel, LiDAR and IMU frames
- Table/base waypoint mission manager
- `/serving/command` JSON command interface
- `/serving/status` mission status topic
- Tablet-friendly browser control page using rosbridge
- Installer support for Tkinter and rosbridge
- Expanded ROS 2 package dependencies

## Example serving command

Publish a command to send the robot to a configured waypoint:

```bash
ros2 topic pub --once /serving/command std_msgs/msg/String "{data: '{\"go\":\"table_1\"}'}"
```

## Important limitation

This is **not** a claim of completed physical autonomy. The motor bridge still deliberately stops at a safe software interface until the actual Zbotic electrical interface, Hall wiring, tachometer behavior, LiDAR and IMU are verified on the robot. Navigation parameters and the URDF dimensions must also be tuned from measured hardware.

## Next hardware-gated milestone

Connect the verified low-level motor interface, add real wheel feedback, validate TF and sensors, then perform slow supervised mapping and Nav2 tests.
