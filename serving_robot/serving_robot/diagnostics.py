import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Imu

class Diagnostics(Node):
    def __init__(self):
        super().__init__('diagnostics')
        self.scan_seen = False
        self.imu_seen = False
        self.create_subscription(LaserScan, '/scan', self.scan_cb, 10)
        self.create_subscription(Imu, '/imu/data', self.imu_cb, 10)
        self.create_timer(2.0, self.report)

    def scan_cb(self, _): self.scan_seen = True
    def imu_cb(self, _): self.imu_seen = True

    def report(self):
        self.get_logger().info(f'LiDAR: {"OK" if self.scan_seen else "WAITING"} | IMU: {"OK" if self.imu_seen else "WAITING"}')

def main(args=None):
    rclpy.init(args=args); node = Diagnostics()
    try: rclpy.spin(node)
    finally: node.destroy_node(); rclpy.shutdown()

if __name__ == '__main__': main()
