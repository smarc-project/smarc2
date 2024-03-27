from setuptools import find_packages, setup
import glob, os

package_name = 'workshopfun'

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
    maintainer='ozer',
    maintainer_email='ozero@kth.se',
    description='does nothing useful :D',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'view_test = workshopfun.SAMThrustView:test_view',
            'science_node = workshopfun.ThrustyControllerNode:main',
            'action_server_node = workshopfun.ActionserverControllerNode:main',
            'action_client_node = workshopfun.ActionClientNode:main'
        ],
    },
)
