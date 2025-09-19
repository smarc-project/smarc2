from setuptools import find_packages, setup
import os
import glob

package_name = 'sam_path_planning'

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
    maintainer='torroba',
    maintainer_email='torroba@kth.se',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sam_planner_node = sam_path_planning.sam_planner_node:main',
            'topic_collector_node = sam_path_planning.topic_collector:main',
            'publish_hula_pose = sam_path_planning.pose_publisher:main'
        ],
    },
)
