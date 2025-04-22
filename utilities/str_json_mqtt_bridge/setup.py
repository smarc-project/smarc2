from setuptools import find_packages, setup
import glob, os

package_name = 'str_json_mqtt_bridge'

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
    maintainer='Ozer Ozkahraman',
    maintainer_email='ozero@kth.se',
    description='A simple json ros string to mqtt bridge',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "waraps_bridge = str_json_mqtt_bridge.bridge:main",
        ],
    },
)
