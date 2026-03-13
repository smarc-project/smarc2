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
    description='Evolo path following with potential fields and action server',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Client
            'move_path_client = evolo_move_path.client:main',
            # Classical algorithms
            'move_path_server_coordinate = evolo_move_path.evolo_move_path_server_coordinate:main',
            'move_path_server_potential_field = evolo_move_path.evolo_move_path_server_potential_field:main',
            'move_path_server_a_star = evolo_move_path.evolo_move_path_server_a_star:main',
            'move_path_server_dubins_curves = evolo_move_path.evolo_move_path_server_dubins_curves:main',
            'move_path_server_dubins_curves_vectorized = evolo_move_path.evolo_move_path_server_dubins_curves_vectorized:main',
            'move_path_server_dubins_curves_new_method = evolo_move_path.evolo_move_path_server_dubins_curves_new_version:main',
            'move_path_server_dubins_curves_lateral_normal = evolo_move_path.evolo_move_path_server_dubins_curves_lateral_normal:main',
            'move_path_server_dubins_curves_mpc = evolo_move_path.evolo_move_path_server_dubins_curves_mpc:main',
            # Discretized algorithms
            'move_path_server_discrete_point = evolo_move_path.evolo_move_path_server_discrete_point:main',
            'move_path_server_potential_field_discrete = evolo_move_path.evolo_move_path_server_potential_field_discrete:main',
            # Other controller 
            'move_path_server_potential_field_mpc = evolo_move_path.evolo_move_path_server_potential_field_mpc:main',
            # Camera
            'move_path_server_dubins_camera = evolo_move_path.evolo_move_path_server_dubins_camera:main',
            'move_path_server_dubins_camera_yolo = evolo_move_path.evolo_move_path_server_dubins_camera_yolo:main',
            # File on the camera's chip
            # 'move_path_server_dubins_camera = evolo_move_path.evolo_move_path_server_dubins_camera:main',
            'move_path_server_geofence =  evolo_move_path.geofence_checker_evolo:main'
        ],
    },
)