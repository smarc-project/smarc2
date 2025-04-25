from setuptools import find_packages, setup
import glob, os

package_name = 'sam_mpc'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob.glob('config/*')),
        (os.path.join('share', package_name, 'launch'), glob.glob('launch/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Simon Spang',
    maintainer_email='sspang@kth.se',
    description='Data-driven Methods for AUVs',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'manual_diving = sam_mpc.Node:main',
            'action_server_diving = sam_mpc.Node:action_server',
            'setpoint = sam_mpc.SetpointNode:main'
        ],
    },
)
