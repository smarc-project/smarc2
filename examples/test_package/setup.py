from setuptools import find_packages, setup
import glob
import os

package_name = 'test_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob.glob('config/*')),
        (os.path.join('share', package_name, 'launch'), glob.glob('launch/*'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jonathan Lane',
    maintainer_email='jglane@purdue.edu',
    description='test package',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'view_test = test_package.SAMThrustView:test_view',
        ],
    },
)
