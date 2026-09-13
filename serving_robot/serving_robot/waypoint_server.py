import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from .mission_manager import MissionManager


class WaypointServer(MissionManager):
    """JSON command interface for tablet/manual serving control."""
    def __init__(self):
        super().__init__()
        self.command_sub = self.create_subscription(String, '/serving/command', self.command_cb, 10)
        self.status_pub = self.create_publisher(String, '/serving/status', 10)
        self.publish_status('ready')

    def publish_status(self, state, **extra):
        payload = {'state': state}
        payload.update(extra)
        msg = String(); msg.data = json.dumps(payload); self.status_pub.publish(msg)

    def command_cb(self, msg):
        try:
            data = json.loads(msg.data)
            action = str(data.get('action', '')).strip().lower()
            target = str(data.get('go', data.get('target', ''))).strip()
            if action == 'cancel' or action == 'stop':
                self.cancel()
                self.publish_status('cancelled')
                return
            if action in ('return', 'home'):
                target = 'base'
            if not target:
                raise ValueError('missing go/target')
            ok = self.go(target)
            self.publish_status('accepted' if ok else 'rejected', target=target)
        except Exception as exc:
            self.publish_status('error', error=str(exc))


def main(args=None):
    rclpy.init(args=args)
    node = WaypointServer()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
