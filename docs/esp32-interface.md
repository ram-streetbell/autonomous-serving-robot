# ESP32 motor interface

The repository includes fail-safe ESP32 firmware and a ROS 2 serial bridge.

## Protocol

At 115200 baud the ROS bridge sends `CMD,left,right,enable,sequence`. Left and right are normalized wheel commands from -1 to +1. The ESP32 disables outputs after 500 ms without a command.

Telemetry is `TEL,left_tach,right_tach,enabled,sequence`.

## Electrical boundary

The Zbotic AI0179 uses a 0–5 V VR speed input. ESP32 GPIO is not assumed to be a 5 V analog source. GPIO assignments therefore remain disabled until the actual interface circuit is verified. Use an appropriate DAC or suitable filtered PWM and level shifting/isolation as required by the exact controller.

Verify logic thresholds, Hall voltage, tach voltage, common ground/isolation, and the physical emergency-disable path before motor power is applied.

## Commissioning

1. Flash the firmware with outputs disabled.
2. Confirm `READY,DISABLED` on serial.
3. Set GPIO constants only after documenting the wiring.
4. Test the interface without motor power.
5. Test each controller with wheels lifted.
6. Confirm direction and emergency disable.
7. Measure tach pulses and determine pulses per wheel revolution.
8. Pass that value to `hardware.launch.py`.
9. Tune wheel radius, track width and Nav2 limits only after real feedback is working.
