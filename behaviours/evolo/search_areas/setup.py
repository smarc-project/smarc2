from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'search_areas'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='baptiste',
    maintainer_email='baptiste.rouquette@outlook.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        'search_area = search_areas.search_area:main',
        'search_areas = search_areas.search_areas:main',
        'search_areas_multi_goals = search_areas.search_areas_multi_goals:main',
        'search_area_obstacles = search_areas.search_area_obstacles:main',
        ],
    },
)
