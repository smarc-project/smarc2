from setuptools import find_packages, setup
import glob, os

package_name = 'basic_depth_pitch_control'

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
    description='Basic depth and pitch keeping',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'action_server_node = basic_depth_pitch_control.ActionserverControllerNode:main',
            'action_client_node = basic_depth_pitch_control.ActionClientNode:main',
            'diving = basic_depth_pitch_control.Node:main',
            'test_view = basic_depth_pitch_control.SAMDiveView:test_view'
        ],
    },
)
