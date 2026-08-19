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
    install_requires=['setuptools', 'control'],
    zip_safe=True,
    maintainer='Ozer Ozkahraman',
    maintainer_email='ozero@kth.se',
    description='Airborne launch and recovery',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "alars_bt = alars.alars_bt:main",
            "alars_move_to_action_server = alars.alars_move_to_as:main",
            "alars_recover_action_server = alars.alars_recover_as:main",
            "alars_search_action_server = alars.alars_search_as:main",
            "alars_follow_auv_action_server = alars.alars_follow_auv_as:main",
            "alars_ping_search_action_server = alars.alars_ping_search_as:main",
            "alars_move_to_damped_action_server = alars.alars_move_to_damped_as:main",
            "alars_estimate_length_and_damping_action_server = alars.alars_estimate_rope_swing_as:main"
        ],
    },
)
