from setuptools import find_packages, setup
import glob
import os

package_name = 'quadrotor_basic_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob.glob('config/*')),
        (os.path.join('share', package_name, 'launch'), glob.glob('launch/*'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jonathan Lane',
    maintainer_email='jglane@purdue.edu',
    description='Taeyoung Lee\'s quadrotor controller for the ALARS drone',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'test = quadrotor_basic_controller.controller_node:test',
            'controller = quadrotor_basic_controller.controller_node:controller',
        ],
    },
)
