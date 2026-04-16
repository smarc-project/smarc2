from setuptools import find_packages, setup
import os
import glob

package_name = 'floatsam_move_to_path'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # QUESTA E' LA RIGA CHE MANCAVA:
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
            'floatsam_move_to_path_action_server = floatsam_move_to_path.floatsam_move_to_path_server:main',
        ],
    },
)