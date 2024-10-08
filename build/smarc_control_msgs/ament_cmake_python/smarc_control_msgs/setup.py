from setuptools import find_packages
from setuptools import setup

setup(
    name='smarc_control_msgs',
    version='0.0.0',
    packages=find_packages(
        include=('smarc_control_msgs', 'smarc_control_msgs.*')),
)
