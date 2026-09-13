import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient

class MissionManager(Node):
    """Simple serving mission manager: send the robot to named table waypoints."""
    def __init__(self):
        super().__init__('mission_manager')
        self.declare_parameter('frame_id', 'map')
        self.declare_parameter('waypoints', {
            'table_1': [1.0, 0.0, 0.0],
            'table_2': [2.0, 0.0, 1.57],
            'base': [0.0, 0.0, 0.0],
        })
        self.frame_id = self.get_parameter('frame_id').value
        self.waypoints = self.get_parameter('waypoints').value
        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.get_logger().info('Mission manager ready. Waypoints: %s', list(self.waypoints.keys()))

    def go(self, name):
        if name not in self.waypoints:
            self.get_logger().error('Unknown waypoint: %s', name)
            return False
        if not self.client.wait_for_server(timeout_sec=3.0):
            self.get_logger().error('Nav2 navigate_to_pose action is not available')
            return False
        x, y, yaw = [float(v) for v in self.waypoints[name]]
        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = self.frame_id
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal.pose.pose.orientation.w = math.cos(yaw / 2.0)
        self.get_logger().info('Sending robot to %s (%.2f, %.2f, %.2f rad)', name, x, y, yaw)
        future = self.client.send_goal_async(goal)
        future.add_done_callback(self._goal_response)
        return True

    def _goal_response(self, future):
        handle = future.result()
        if not handle.accepted:
            self.get_logger().error('Navigation goal rejected')
            return
        self.get_logger().info('Navigation goal accepted')
        result_future = handle.get_result_async()
        result_future.add_done_callback(self._result)

    def _result(self, future):
        self.get_logger().info('Navigation goal finished with status %s', future.result().status)

def main(args=None):
    rclpy.init(args=args)
    node = MissionManager()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
