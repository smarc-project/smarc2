from setuptools import find_packages, setup
import glob, os

package_name = 'alars'

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
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Ozer Ozkahraman',
    maintainer_email='ozero@kth.se',
    description='Airborne launch and recovery',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "alars_move_to_action_server = alars.alars_move_to_action_server:main",
            "alars_recover_action_server = alars.alars_recover_action_server:main",
            "alars_search_action_server = alars.alars_search_action_server:main",
            "alars_follow_auv_action_server = alars.alars_follow_auv_action_server:main",
            "alars_bt = alars.alars_bt:main",
        ],
    },
)
