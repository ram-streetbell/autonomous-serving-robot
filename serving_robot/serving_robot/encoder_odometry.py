import math
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped


class EncoderOdometry(Node):
    """Convert ESP32 cumulative tach counts into differential-drive odometry."""
    def __init__(self):
        super().__init__('encoder_odometry')
        self.declare_parameter('wheel_radius_m', 0.0762)
        self.declare_parameter('wheel_separation_m', 0.38)
        self.declare_parameter('pulses_per_wheel_rev', 1.0)
        self.r = float(self.get_parameter('wheel_radius_m').value)
        self.track = float(self.get_parameter('wheel_separation_m').value)
        self.ppr = max(1e-6, float(self.get_parameter('pulses_per_wheel_rev').value))
        self.x = self.y = self.yaw = 0.0
        self.prev_l = self.prev_r = None
        self.prev_t = time.monotonic()
        self.last_l = self.last_r = 0
        self.pub = self.create_publisher(Odometry, '/odom', 20)
        self.tf = TransformBroadcaster(self)
        self.create_subscription(String, '/motor/status', self.status_cb, 20)

    def status_cb(self, msg):
        parts = msg.data.split(',')
        if len(parts) < 5 or parts[0] != 'TEL':
            return
        try:
            left, right = int(parts[1]), int(parts[2])
        except ValueError:
            return
        now = time.monotonic()
        if self.prev_l is None:
            self.prev_l, self.prev_r, self.prev_t = left, right, now
            return
        dt = max(1e-3, now - self.prev_t)
        dl = (left - self.prev_l) / self.ppr * 2.0 * math.pi * self.r
        dr = (right - self.prev_r) / self.ppr * 2.0 * math.pi * self.r
        ds = (dl + dr) / 2.0
        dyaw = (dr - dl) / self.track
        self.x += ds * math.cos(self.yaw + dyaw / 2.0)
        self.y += ds * math.sin(self.yaw + dyaw / 2.0)
        self.yaw += dyaw
        vl, vr = dl / dt, dr / dt
        v, w = (vl + vr) / 2.0, (vr - vl) / self.track
        self.prev_l, self.prev_r, self.prev_t = left, right, now
        stamp = self.get_clock().now().to_msg()
        od = Odometry()
        od.header.stamp = stamp; od.header.frame_id = 'odom'; od.child_frame_id = 'base_link'
        od.pose.pose.position.x = self.x; od.pose.pose.position.y = self.y
        od.pose.pose.orientation.z = math.sin(self.yaw / 2.0); od.pose.pose.orientation.w = math.cos(self.yaw / 2.0)
        od.twist.twist.linear.x = v; od.twist.twist.angular.z = w
        self.pub.publish(od)
        tf = TransformStamped(); tf.header.stamp = stamp; tf.header.frame_id = 'odom'; tf.child_frame_id = 'base_link'
        tf.transform.translation.x = self.x; tf.transform.translation.y = self.y
        tf.transform.rotation = od.pose.pose.orientation
        self.tf.sendTransform(tf)


def main(args=None):
    rclpy.init(args=args)
    node = EncoderOdometry()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node(); rclpy.shutdown()


if __name__ == '__main__': main()
