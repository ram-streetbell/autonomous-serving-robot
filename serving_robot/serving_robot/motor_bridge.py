import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class MotorBridge(Node):
    def __init__(self):
        super().__init__('motor_bridge')
        self.declare_parameter('wheel_radius_m', 0.0762)
        self.declare_parameter('wheel_separation_m', 0.38)
        self.declare_parameter('max_linear_mps', 0.35)
        self.declare_parameter('max_angular_rps', 0.9)
        self.declare_parameter('cmd_timeout_s', 0.5)
        self.r = float(self.get_parameter('wheel_radius_m').value)
        self.track = float(self.get_parameter('wheel_separation_m').value)
        self.vmax = float(self.get_parameter('max_linear_mps').value)
        self.wmax = float(self.get_parameter('max_angular_rps').value)
        self.timeout = float(self.get_parameter('cmd_timeout_s').value)
        self.last_cmd = time.monotonic()
        self.left = 0.0
        self.right = 0.0
        self.create_subscription(Twist, '/cmd_vel', self.cmd_cb, 10)
        self.left_pub = self.create_publisher(Twist, '/motor/left_target', 10)
        self.right_pub = self.create_publisher(Twist, '/motor/right_target', 10)
        self.create_timer(0.05, self.watchdog)
        self.get_logger().info('Motor bridge started in safe simulation mode')

    def cmd_cb(self, msg):
        v = max(-self.vmax, min(self.vmax, msg.linear.x))
        w = max(-self.wmax, min(self.wmax, msg.angular.z))
        self.left = (v - w * self.track / 2.0) / self.r
        self.right = (v + w * self.track / 2.0) / self.r
        self.last_cmd = time.monotonic()
        self.publish_targets()

    def publish_targets(self):
        left = Twist(); right = Twist()
        left.angular.z = self.left
        right.angular.z = self.right
        self.left_pub.publish(left)
        self.right_pub.publish(right)

    def watchdog(self):
        if time.monotonic() - self.last_cmd > self.timeout:
            self.left = 0.0
            self.right = 0.0
            self.publish_targets()

def main(args=None):
    rclpy.init(args=args)
    node = MotorBridge()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
