from setuptools import find_packages
from setuptools import setup

setup(
    name='smarc_mission_msgs',
    version='0.0.0',
    packages=find_packages(
        include=('smarc_mission_msgs', 'smarc_mission_msgs.*')),
)
