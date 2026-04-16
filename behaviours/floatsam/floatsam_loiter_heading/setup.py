from setuptools import find_packages, setup
import os
import glob

package_name = 'floatsam_loiter_heading'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob.glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='lorenzo',
    maintainer_email='mannolorenzo421@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'floatsam_loiter_heading_action_server = floatsam_loiter_heading.floatsam_loiter_heading_server:main',
        ],
    },
)
