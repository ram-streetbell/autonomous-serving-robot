from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    share = get_package_share_directory('slam_toolbox')
    path = os.path.join(share, 'launch', 'online_async_launch.py')
    return LaunchDescription([IncludeLaunchDescription(PythonLaunchDescriptionSource(path))])
