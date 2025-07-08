import os
import glob
from setuptools import find_packages, setup

package_name = 'lolo_emergency_action'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob.glob('launch/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='tko',
    maintainer_email='aldot@kth.se',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "client = lolo_emergency_action.emergency_client:main",
            "server = lolo_emergency_action.emergency_server:main",
        ],
    },
)
