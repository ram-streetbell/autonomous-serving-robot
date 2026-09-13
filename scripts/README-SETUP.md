# New Ubuntu Setup

1. Clone the repository.
2. Run `bash scripts/install.sh` from a normal user account.
3. Run `python3 scripts/commissioning_check.py`.
4. Run `bash scripts/start_robot_setup.sh` to open the graphical Setup & Test application.
5. Keep the robot in a mechanically safe state while commissioning. The software does not automatically enable the motor controller.
6. Verify Hall/tach wiring and the required 0-5 V speed-interface electrical stage before enabling the drive.

This release is intended for commissioning and bench testing. Restaurant navigation and physical serving behavior require calibration and real-world testing on the target robot.
