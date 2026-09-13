from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('serial_port', default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('pulses_per_wheel_rev', default_value='1.0'),
        Node(package='serving_robot', executable='motor_bridge', name='motor_bridge', output='screen'),
        Node(package='serving_robot', executable='esp32_bridge', name='esp32_bridge', output='screen', parameters=[{
            'port': LaunchConfiguration('serial_port'),
            'enabled_on_start': False,
        }]),
        Node(package='serving_robot', executable='encoder_odometry', name='encoder_odometry', output='screen', parameters=[{
            'pulses_per_wheel_rev': LaunchConfiguration('pulses_per_wheel_rev'),
        }]),
        Node(package='serving_robot', executable='diagnostics', name='diagnostics', output='screen'),
        Node(package='serving_robot', executable='waypoint_server', name='waypoint_server', output='screen'),
    ])
