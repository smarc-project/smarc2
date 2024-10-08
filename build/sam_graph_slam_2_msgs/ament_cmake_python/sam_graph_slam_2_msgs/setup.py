from setuptools import find_packages
from setuptools import setup

setup(
    name='sam_graph_slam_2_msgs',
    version='0.0.0',
    packages=find_packages(
        include=('sam_graph_slam_2_msgs', 'sam_graph_slam_2_msgs.*')),
)
