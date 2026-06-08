from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'smarc_utilities'

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
    maintainer='tko',
    maintainer_email='kogucki@kth.se',
    description='SMARC Utilities for various items',
    license='MIT',
    #tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simple_tts = smarc_utilities.tts:main',
            'beckholmen_vis = smarc_utilities.beckholmen_vis:main',
            'internet_checker = smarc_utilities.internet_checker:main',
        ],
    },
)
