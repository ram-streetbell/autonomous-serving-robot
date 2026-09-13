import json
import math
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose


class MissionManager(Node):
    """Serving mission controller with named waypoints and cancel support."""
    def __init__(self):
        super().__init__('mission_manager')
        self.declare_parameter('frame_id', 'map')
        self.declare_parameter('waypoints_json', '{"table_1":[1.0,0.0,0.0],"table_2":[2.0,0.0,1.57],"base":[0.0,0.0,0.0]}')
        self.frame_id = str(self.get_parameter('frame_id').value)
        raw = str(self.get_parameter('waypoints_json').value)
        try:
            parsed = json.loads(raw)
            self.waypoints = {str(k): [float(v) for v in value] for k, value in parsed.items()}
            if any(len(v) != 3 for v in self.waypoints.values()):
                raise ValueError('each waypoint must be [x,y,yaw]')
        except Exception as exc:
            self.get_logger().error('Invalid waypoints_json: %s', exc)
            self.waypoints = {}
        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.goal_handle = None
        self.get_logger().info('Mission manager ready: %s', list(self.waypoints))

    def go(self, name):
        if name not in self.waypoints:
            self.get_logger().error('Unknown waypoint: %s', name)
            return False
        if not self.client.wait_for_server(timeout_sec=3.0):
            self.get_logger().error('Nav2 navigate_to_pose is unavailable')
            return False
        x, y, yaw = self.waypoints[name]
        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = self.frame_id
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal.pose.pose.orientation.w = math.cos(yaw / 2.0)
        self._active_name = name
        future = self.client.send_goal_async(goal)
        future.add_done_callback(self._goal_response)
        return True

    def cancel(self):
        if self.goal_handle is None:
            return False
        self.goal_handle.cancel_goal_async()
        self.goal_handle = None
        return True

    def _goal_response(self, future):
        try:
            handle = future.result()
        except Exception as exc:
            self.get_logger().error('Goal error: %s', exc)
            return
        if not handle.accepted:
            self.get_logger().error('Navigation goal rejected')
            return
        self.goal_handle = handle
        self.get_logger().info('Serving mission accepted: %s', self._active_name)
        result_future = handle.get_result_async()
        result_future.add_done_callback(self._result)

    def _result(self, future):
        status = future.result().status
        self.get_logger().info('Serving mission %s finished with status %s', self._active_name, status)
        self.goal_handle = None


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
