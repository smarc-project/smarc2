from setuptools import find_packages, setup
import glob, os

package_name = 'sam_diving_controller'

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
    maintainer='David Doerner',
    maintainer_email='ddorner@kth.se',
    description='Full active and static diving controller',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'action_server_node = sam_diving_controller.ActionserverControllerNode:main',
            'action_client_node = sam_diving_controller.ActionClientNode:main',
            'manual_diving = sam_diving_controller.Node:main',
            'action_server_diving = sam_diving_controller.Node:action_server',
            'test_view = sam_diving_controller.SAMDiveView:test_view',
            'setpoint = sam_diving_controller.SetpointNode:main'
        ],
    },
)
