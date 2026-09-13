from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='serving_robot', executable='motor_bridge', name='motor_bridge', output='screen', parameters=[{
            'wheel_radius_m': 0.0762,
            'wheel_separation_m': 0.38,
            'max_linear_mps': 0.35,
            'max_angular_rps': 0.9,
            'cmd_timeout_s': 0.5,
        }]),
        Node(package='serving_robot', executable='odometry', name='odometry', output='screen', parameters=[{
            'wheel_radius_m': 0.0762,
            'wheel_separation_m': 0.38,
        }]),
        Node(package='serving_robot', executable='diagnostics', name='diagnostics', output='screen'),
    ])
