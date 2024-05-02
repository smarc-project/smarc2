from setuptools import find_packages, setup
import glob, os

package_name = 'smarc_bringups'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob.glob('config/*')),
        (os.path.join('share', package_name, 'launch'), glob.glob('launch/*')),
        (os.path.join('share', package_name, 'scripts'), glob.glob('scripts/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Ozer Ozkahraman',
    maintainer_email='ozero@kth.se',
    description='Bringup scripts to launch a bunch of stuff for vehicles',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
    scripts=[
        "scripts/sam_bringup.sh"
    ]
)
