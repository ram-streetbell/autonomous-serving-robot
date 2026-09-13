from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params = PathJoinSubstitution([FindPackageShare('serving_robot'), 'config', 'nav2_params.yaml'])
    nav2 = PathJoinSubstitution([FindPackageShare('nav2_bringup'), 'launch', 'bringup_launch.py'])
    map_file = LaunchConfiguration('map')
    return LaunchDescription([
        DeclareLaunchArgument('map', default_value='', description='Saved occupancy-grid YAML map'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2),
            launch_arguments={'map': map_file, 'params_file': params, 'use_sim_time': 'false'}.items(),
        ),
    ])
