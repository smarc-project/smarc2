from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'sam_diving_controller'

resource_files = glob("resource/*.onnx")

setup(

    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (f"share/{package_name}/resource", resource_files),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='David Doerner',
    maintainer_email='ddorner@kth.se',
    description='Full active and static diving controller',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            #'action_server_node = sam_diving_controller.ActionserverControllerNode:main',
            #'action_client_node = sam_diving_controller.ActionClientNode:main',
            #'manual_diving = sam_diving_controller.Node:main',
            #'action_server_diving = sam_diving_controller.Node:action_server',
            #'mpc_trajectory_tracking = sam_diving_controller.Node:mpc_trajectory_tracking',
            #'setpoint = sam_diving_controller.SetpointNode:main',
            #'joy_depth = sam_diving_controller.JoyNode:joy_depth',
            #'nmpc_diving = sam_diving_controller.Node:nmpc_action_server',
            #'sim_sam = sam_diving_controller.Node:sim_sam',
            "diving_main = sam_diving_controller.entrypoints:main",
            "diving_sim_sam = sam_diving_controller.entrypoints:sim_sam",
            "diving_joy_depth = sam_diving_controller.entrypoints:joy_depth",
            "pid_wp_following = sam_diving_controller.entrypoints:pid_wp_following",
            "pid_trajectory_tracking = sam_diving_controller.entrypoints:pid_trajectory_tracking",
            "mpc_wp_following = sam_diving_controller.entrypoints:mpc_wp_following",
            "mpc_trajectory_tracking = sam_diving_controller.entrypoints:mpc_trajectory_tracking",
        ],
    },
)
