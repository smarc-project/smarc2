import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'alars_auv_perception'


def get_data_files():
    data_files = [
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),
        (
            os.path.join('share', package_name),
            ['package.xml'],
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py'),
        ),
        (
            os.path.join('share', package_name, 'trained_models'),
            glob('trained_models/*'),
        ),
    ]

    for root, _, files in os.walk('config'):
        if files:
            install_dir = os.path.join('share', package_name, root)
            file_paths = [os.path.join(root, f) for f in files]
            data_files.append((install_dir, file_paths))

    return data_files


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=get_data_files(),
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Cristhian',
    maintainer_email='ckmc@kth.se',
    description='ROS2 package for the ALARS perception pipeline',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'alars_yolo_detector = alars_auv_perception.alars_yolo_detector:main',
            'alars_video_publisher = alars_auv_perception.alars_video_publisher:main',
        ],
    },
)