# Hardware integration

## Zbotic AI0179

The selected controller is the Zbotic DC 12–36 V 500 W Hall BLDC controller.

Published control-side signals:

| Signal | Published function |
|---|---|
| GND | control ground |
| VR | 0–5 V speed command |
| ZF | direction command |
| M | tachometer pulse output |
| EL | enable command |
| Hall 5V | Hall supply |
| Ha/Hb/Hc | Hall signals |
| Hall GND | Hall ground |

The supplier lists 12–36 V operation, <=15 A operating current and <=500 W drive power. It also warns that Hall wire order can vary between motors and that an incorrect Hall sequence can cause abnormal operation or excessive current.

## Required interface boundary

The Linux computer should not be treated as a direct 5 V analog-output device. The final motor interface should use a suitable DAC/isolated interface or a dedicated microcontroller interface that has been electrically verified.

The ROS layer therefore exposes a clean wheel-command interface first. Hardware-specific output is kept behind the motor bridge so the navigation stack does not depend on the electrical interface.

## Commissioning order

1. Test each motor/controller pair with wheels lifted.
2. Verify Hall order and direction.
3. Verify the speed command range with a meter/oscilloscope.
4. Verify enable behavior.
5. Verify tachometer feedback.
6. Calibrate wheel radius and wheel separation.
7. Run LiDAR and IMU diagnostics.
8. Create a map at low speed.
9. Enable autonomous navigation only after localization is stable.
