from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'sam_dead_reckoning'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='julian',
    maintainer_email='jvaldez@gkth.com',
    description='Sam and floatSam specific dead reckoning',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'dr_node = sam_dead_reckoning.dr_node:main',
            'gps_node = sam_dead_reckoning.gps_node:main',
            'depth_node = sam_dead_reckoning.press_to_depth:main',
            'rpy_node = sam_dead_reckoning.sbg_imu_2_rpy_enu:main',
            'compass_heading_node = sam_dead_reckoning.yaw_enu_2_compass_heading:main',
            'dr_lat_lon_node = sam_dead_reckoning.dr_odom_2_lat_lon:main'
        ],
    },
)
