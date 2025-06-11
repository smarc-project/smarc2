from setuptools import find_packages, setup
import glob, os

package_name = 'geofence_checker'

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
    maintainer='julian',
    maintainer_email='jvaldez@kth.se',
    description='A simple geofence checker made into a service node.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "geofence_checker_service = geofence_checker.geofence_checker_node:main",
            "geofence_checker_client = geofence_checker.geofence_checker_client_node:main"
        ],
    },
)
