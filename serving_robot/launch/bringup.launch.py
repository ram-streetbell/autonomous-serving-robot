from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    description_launch = PathJoinSubstitution([
        FindPackageShare('serving_robot'), 'launch', 'robot_description.launch.py'
    ])
    return LaunchDescription([
        IncludeLaunchDescription(PythonLaunchDescriptionSource(description_launch)),
        Node(package='serving_robot', executable='motor_bridge', name='motor_bridge', output='screen', parameters=[{
            'wheel_radius_m': 0.0762, 'wheel_separation_m': 0.38,
            'max_linear_mps': 0.35, 'max_angular_rps': 0.9, 'cmd_timeout_s': 0.5,
        }]),
        Node(package='serving_robot', executable='odometry', name='odometry', output='screen', parameters=[{
            'wheel_radius_m': 0.0762, 'wheel_separation_m': 0.38,
        }]),
        Node(package='serving_robot', executable='diagnostics', name='diagnostics', output='screen'),
        Node(package='serving_robot', executable='waypoint_server', name='waypoint_server', output='screen'),
    ])
