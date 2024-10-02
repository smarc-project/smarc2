from setuptools import find_packages, setup
from glob import glob
import os
package_name = 'sam_joy_xbox'

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
    maintainer='axel',
    maintainer_email='axbr',
    description='TODO: Package description',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sam_joy_xbox = sam_joy_xbox.controller:main',
        ],
    },
)
