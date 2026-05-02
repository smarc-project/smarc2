from setuptools import find_packages, setup

package_name = 'actionable_geofence'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Ozer Ozkahraman',
    maintainer_email='ozero@kth.se',
    description='A common geofence checking node that exposes a wasp-bt compatible action',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'geofence_node = actionable_geofence.geofence_node:main',
            'test_action = actionable_geofence.geofence_node:test_action',
        ],
    },
)
