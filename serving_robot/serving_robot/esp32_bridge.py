import threading
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String


class ESP32Bridge(Node):
    """Serial bridge between ROS wheel targets and the fail-safe ESP32 interface."""
    def __init__(self):
        super().__init__('esp32_bridge')
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baud', 115200)
        self.declare_parameter('max_wheel_rad_s', 6.0)
        self.declare_parameter('enabled_on_start', False)
        self.port = str(self.get_parameter('port').value)
        self.baud = int(self.get_parameter('baud').value)
        self.max_w = max(0.1, float(self.get_parameter('max_wheel_rad_s').value))
        self.enabled = bool(self.get_parameter('enabled_on_start').value)
        self.seq = 0
        self.last_target = time.monotonic()
        self.serial = None
        self.lock = threading.Lock()
        self.left_sub = self.create_subscription(Twist, '/motor/left_target', self.left_cb, 10)
        self.right_sub = self.create_subscription(Twist, '/motor/right_target', self.right_cb, 10)
        self.status_pub = self.create_publisher(String, '/motor/status', 10)
        self.left = self.right = 0.0
        try:
            import serial
            self.serial = serial.Serial(self.port, self.baud, timeout=0.05)
            self.get_logger().info('ESP32 serial connected: %s', self.port)
        except Exception as exc:
            self.get_logger().warning('ESP32 serial unavailable (%s). Bridge remains disabled.', exc)
        self.create_timer(0.05, self.send)
        self.create_timer(0.02, self.read)

    def left_cb(self, msg):
        self.left = float(msg.angular.z)
        self.last_target = time.monotonic()

    def right_cb(self, msg):
        self.right = float(msg.angular.z)
        self.last_target = time.monotonic()

    def send(self):
        if self.serial is None:
            return
        if time.monotonic() - self.last_target > 0.5:
            self.left = self.right = 0.0
            self.enabled = False
        l = max(-1.0, min(1.0, self.left / self.max_w))
        r = max(-1.0, min(1.0, self.right / self.max_w))
        self.seq = (self.seq + 1) & 0xFFFFFFFF
        line = f'CMD,{l:.4f},{r:.4f},{1 if self.enabled else 0},{self.seq}\n'
        try:
            with self.lock:
                self.serial.write(line.encode('ascii'))
        except Exception as exc:
            self.enabled = False
            self.get_logger().error('ESP32 write failed: %s', exc)

    def read(self):
        if self.serial is None:
            return
        try:
            while self.serial.in_waiting:
                line = self.serial.readline().decode('ascii', errors='ignore').strip()
                if line.startswith('TEL,'):
                    msg = String(); msg.data = line; self.status_pub.publish(msg)
        except Exception as exc:
            self.get_logger().error('ESP32 read failed: %s', exc)


def main(args=None):
    rclpy.init(args=args)
    node = ESP32Bridge()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
