from setuptools import setup
from glob import glob

package_name = 'serving_robot'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'motor_bridge = serving_robot.motor_bridge:main',
            'odometry = serving_robot.odometry:main',
            'diagnostics = serving_robot.diagnostics:main',
        ],
    },
)
