from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'evolo_move_path'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='niklas',
    maintainer_email='nrol@kth.se',
    description='Evolo path following',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Classical algorithms
            'move_path_server_dubins_curves = evolo_move_path.evolo_move_path_server_dubins_curves:main',
            'move_path_server_simple = evolo_move_path.evolo_move_path_simple:main',
        ],
    },
)