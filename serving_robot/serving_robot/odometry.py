import math
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster

class OdometryNode(Node):
    def __init__(self):
        super().__init__('odometry')
        self.declare_parameter('wheel_radius_m', 0.0762)
        self.declare_parameter('wheel_separation_m', 0.38)
        self.r = float(self.get_parameter('wheel_radius_m').value)
        self.track = float(self.get_parameter('wheel_separation_m').value)
        self.left = 0.0
        self.right = 0.0
        self.x = self.y = self.yaw = 0.0
        self.last = time.monotonic()
        self.create_subscription(Twist, '/motor/left_target', self.left_cb, 10)
        self.create_subscription(Twist, '/motor/right_target', self.right_cb, 10)
        self.pub = self.create_publisher(Odometry, '/odom', 20)
        self.tf = TransformBroadcaster(self)
        self.create_timer(0.02, self.tick)

    def left_cb(self, msg): self.left = msg.angular.z
    def right_cb(self, msg): self.right = msg.angular.z

    def tick(self):
        now = time.monotonic(); dt = min(now - self.last, 0.1); self.last = now
        vl = self.left * self.r; vr = self.right * self.r
        v = (vl + vr) / 2.0; w = (vr - vl) / self.track
        self.x += v * math.cos(self.yaw) * dt
        self.y += v * math.sin(self.yaw) * dt
        self.yaw += w * dt
        stamp = self.get_clock().now().to_msg()
        od = Odometry(); od.header.stamp = stamp; od.header.frame_id = 'odom'; od.child_frame_id = 'base_link'
        od.pose.pose.position.x = self.x; od.pose.pose.position.y = self.y
        od.pose.pose.orientation.z = math.sin(self.yaw / 2); od.pose.pose.orientation.w = math.cos(self.yaw / 2)
        od.twist.twist.linear.x = v; od.twist.twist.angular.z = w
        self.pub.publish(od)
        t = TransformStamped(); t.header.stamp = stamp; t.header.frame_id = 'odom'; t.child_frame_id = 'base_link'
        t.transform.translation.x = self.x; t.transform.translation.y = self.y
        t.transform.rotation = od.pose.pose.orientation
        self.tf.sendTransform(t)

def main(args=None):
    rclpy.init(args=args); node = OdometryNode()
    try: rclpy.spin(node)
    finally: node.destroy_node(); rclpy.shutdown()

if __name__ == '__main__': main()
