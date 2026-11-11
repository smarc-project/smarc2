import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'waraps_officer'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Shekhar Devm Upadhyay',
    maintainer_email='shekharu@kth.se',
    description='WARA-PS agent nodes: waraps_vehicle publishes level 1, waraps_officer runs one task at a time.',
    license='MIT',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'waraps_vehicle = waraps_officer.waraps_vehicle:main',
            'waraps_officer = waraps_officer.officer:main',
        ],
    },
)
