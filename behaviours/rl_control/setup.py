from setuptools import find_packages, setup
import glob, os

package_name = 'rl_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob.glob('config/*')),
        (os.path.join('share', package_name, 'launch'), glob.glob('launch/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Mart Kartasev',
    maintainer_email='kartasev@kth.se',
    description='RL Based waypoint follower',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'action_server_node = rl_control.RLMissionActionServer:main',
            'action_client_node = rl_control.RLControlClientNode:main',
            'rl_control_node = rl_control.Node:main',
        ],
    },
)
