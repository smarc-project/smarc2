import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'evolo_obstacle_avoidance'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Mattias',
    maintainer_email='mtrende@kth.se',
    description='Obstacle avoidance using CBFs for Evolo',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'cbf_avoidance = evolo_obstacle_avoidance.obstacle_avoidance:main',
        ],
    },
)
