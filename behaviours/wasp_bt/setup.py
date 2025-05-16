from setuptools import find_packages, setup
import glob, os

package_name = 'wasp_bt'

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
    maintainer='Shekhar Devm Upadhyay',
    maintainer_email='sdup@kth.se',
    description='The NEW Behaviour Tree for varius SMaRC vehicles, compatible with WARA-PS agent API specs. Usually wet.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "wasp_bt = wasp_bt.bt.ros_bt:wasp_bt",
            "test_ros_vehicle = wasp_bt.vehicles.ros_vehicle:test_ros_vehicle",
            "test_sam_auv = wasp_bt.vehicles.sam_auv:test_sam_auv",
            "test_bt_conditions = wasp_bt.bt.ros_bt:test_bt_conditions",
            "send_test_mission = wasp_bt.mission.ros_mission_updater:send_test_mission_control",
            "test_dubins_planner_caller = wasp_bt.mission.ros_dubins_planner_caller:test_dubins_planner_caller"
        ],
    },
)
