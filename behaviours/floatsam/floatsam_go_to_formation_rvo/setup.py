from setuptools import find_packages, setup
import os 
import glob
package_name = 'floatsam_go_to_formation_rvo'

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
    maintainer='aleba',
    maintainer_email='03alebassi@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'floatsam_go_to_formation_rvo_action_server = floatsam_go_to_formation_rvo.floatsam_go_to_formation_rvo_server:main',
        ],
    },
)
