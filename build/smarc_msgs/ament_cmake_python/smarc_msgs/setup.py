from setuptools import find_packages
from setuptools import setup

setup(
    name='smarc_msgs',
    version='0.1.0',
    packages=find_packages(
        include=('smarc_msgs', 'smarc_msgs.*')),
)
