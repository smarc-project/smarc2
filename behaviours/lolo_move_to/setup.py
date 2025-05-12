from setuptools import find_packages, setup

package_name = 'lolo_move_to'

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
            "client = lolo_move_to.lolo_move_to_client:main",
            "server = lolo_move_to.lolo_move_to_server:main",
        ],
    },
)
