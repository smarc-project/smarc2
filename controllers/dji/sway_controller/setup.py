import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'sway_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        (os.path.join('share', package_name, 'launch'), glob('launch/*launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='aleba',
    maintainer_email='alebas@kth.se',
    description='Path parametrization, ZVD input shaping, and LQG control for payload swing damping',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'hook_kalman_filter_node = sway_controller.Kalman_Filter.hook_kalman_filter_node:main',
            'estimate_length_and_damping_node = sway_controller.Kalman_Filter.estimate_length_and_damping_node:main',
        ],
    },
)
