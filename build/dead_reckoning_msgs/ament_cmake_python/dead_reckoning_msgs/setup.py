from setuptools import find_packages
from setuptools import setup

setup(
    name='dead_reckoning_msgs',
    version='0.0.0',
    packages=find_packages(
        include=('dead_reckoning_msgs', 'dead_reckoning_msgs.*')),
)
