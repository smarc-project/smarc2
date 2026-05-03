from setuptools import find_packages, setup

package_name = 'smarc_basic'

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
    description='Pile of basic actions',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'geofence_node = smarc_basic.geofence_node:main',
            'wait_action = smarc_basic.wait_action:main',
            'log_action = smarc_basic.log_action:main'
        ],
    },
)
