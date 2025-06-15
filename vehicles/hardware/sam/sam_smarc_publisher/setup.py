from setuptools import find_packages, setup
import os
import glob

package_name = 'sam_smarc_publisher'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
         glob.glob('launch/*.launch')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Li Ling',
    maintainer_email='liling@kth.se',
    description='Publisher node that converts SAM topics to general SMaRC topics',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sam_smarc_publisher = sam_smarc_publisher.sam_smarc_publisher:main',
            'sam_control_publisher = sam_smarc_publisher.sam_control_publisher:main',
        ],
    },
)
