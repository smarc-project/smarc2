import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'evolo_map_cluster'

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
    maintainer='Mattias',
    maintainer_email='mtrende@kth.se',
    description='Cluster occupied areas from a occupancy grid, to provide easy input for the CBF.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'clustering_grid = evolo_map_cluster.cluster_grid:main',
        ],
    },
)
