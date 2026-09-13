import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from .mission_manager import MissionManager

class WaypointServer(MissionManager):
    """Accept JSON commands on /serving/command, e.g. {\"go\":\"table_1\"}."""
    def __init__(self):
        super().__init__()
        self.create_subscription(String, '/serving/command', self.command_cb, 10)
        self.status_pub = self.create_publisher(String, '/serving/status', 10)

    def command_cb(self, msg):
        try:
            data = json.loads(msg.data)
            target = str(data.get('go', '')).strip()
            if not target:
                raise ValueError('missing go')
            ok = self.go(target)
            status = {'accepted': ok, 'target': target}
        except Exception as exc:
            status = {'accepted': False, 'error': str(exc)}
        out = String(); out.data = json.dumps(status); self.status_pub.publish(out)

def main(args=None):
    rclpy.init(args=args)
    node = WaypointServer()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node(); rclpy.shutdown()

if __name__ == '__main__': main()
