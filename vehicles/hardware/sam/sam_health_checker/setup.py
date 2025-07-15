from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'sam_health_checker'

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
    maintainer='Julian Valdez',
    maintainer_email='jvaldez@gkth.com',
    description='health checking',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            f'sam_rate_health_node = {package_name}.sam_rate_health_node:main',
            f'dummy_health_node = {package_name}.dummy_health_node:main'
        ],
    },
)
