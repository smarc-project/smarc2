import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'floatsam_controllers'

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
    maintainer='filippo',
    maintainer_email='fidf@kth.se',
    description='Control stack for FloatSam USV - cascaded PID controllers and captain mixer',
    license='BSD-3-Clause',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'captain = floatsam_controllers.captain:main',
            'rvo_service_node = floatsam_controllers.rvo_service:main',
        ],
    },
)
