from setuptools import find_packages, setup
import glob, os

package_name = 'auv_state_estimation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'),
            glob.glob('config/*')),
        (os.path.join('share', package_name, 'launch'), 
            [f for f in glob.glob('launch/*.py') if os.path.isfile(f)]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sebbe',
    maintainer_email='sebbe@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'projection = auv_state_estimation.projection:main',
            'ekf_node = auv_state_estimation.ekf_node:main',
        ],
    },
)
