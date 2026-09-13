from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    urdf = PathJoinSubstitution([FindPackageShare('serving_robot'), 'urdf', 'serving_robot.urdf'])
    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': open('/dev/null').read()}],
        )
    ])
