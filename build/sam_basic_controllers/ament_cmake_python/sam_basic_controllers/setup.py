from setuptools import find_packages
from setuptools import setup

setup(
    name='sam_basic_controllers',
    version='0.1.0',
    packages=find_packages(
        include=('sam_basic_controllers', 'sam_basic_controllers.*')),
)
