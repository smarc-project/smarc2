from setuptools import find_packages, setup
import glob, os

package_name = 'virtual_lolo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob.glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='aldot',
    maintainer_email='aldot@kth.se',
    description='Virtual lolo class to be used for control, planning, etc.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
