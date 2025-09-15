from setuptools import find_packages, setup

package_name = 'lolo_cruise_depth_at_heading'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='aldot',
    maintainer_email='aldot@kth.se',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "client = lolo_cruise_depth_at_heading.lolo_cruise_depth_at_heading_client:main",
            "server = lolo_cruise_depth_at_heading.lolo_cruise_depth_at_heading_server:main",
        ],
    },
)
