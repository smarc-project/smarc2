from setuptools import setup
import os
from glob import glob

package_name = 'floatsam_topic_bridge'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='filippo',
    maintainer_email='fidf@kth.se',
    description='Topic bridge to convert Floatsam simulator/hardware topics to standard SMaRC topics',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'smarc_topics_publisher = floatsam_topic_bridge.smarc_topics_publisher:main',
            'floatsam_health_checker = floatsam_topic_bridge.floatsam_health_checker:main',
        ],
    },
)
