from setuptools import find_packages
from setuptools import setup

setup(
    name='sam_msgs',
    version='0.1.0',
    packages=find_packages(
        include=('sam_msgs', 'sam_msgs.*')),
)
