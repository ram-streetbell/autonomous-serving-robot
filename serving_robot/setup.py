from setuptools import setup
from glob import glob

package_name = 'serving_robot'

setup(
    name=package_name,
    version='0.3.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/urdf', glob('urdf/*')),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'motor_bridge = serving_robot.motor_bridge:main',
            'esp32_bridge = serving_robot.esp32_bridge:main',
            'odometry = serving_robot.odometry:main',
            'diagnostics = serving_robot.diagnostics:main',
            'mission_manager = serving_robot.mission_manager:main',
            'waypoint_server = serving_robot.waypoint_server:main',
        ],
    },
)
