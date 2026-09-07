import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'active_hook'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kaplan',
    maintainer_email='aliulvi4103@hotmail.com',
    description='Teleop + mavros bridge captain interface for an ArduSub ROV',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'active_hook_captain = active_hook.active_hook_captain:main',
        ],
    },
)