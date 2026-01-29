from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'sam_path_following'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='David Doerner',
    maintainer_email='ddorner@kth.se',
    description='Action server, client, and action for path following',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'csv_path_publisher = sam_path_following.path_publisher:main',
            'path_client = sam_path_following.path_client:main',
        ],
    },
)
