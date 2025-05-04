from setuptools import find_packages, setup

package_name = 'go_to_hydrobaticpoint'

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
    maintainer='torroba',
    maintainer_email='torroba@kth.se',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "client = go_to_hydrobaticpoint.hydrobaticpoint_client:main",
            "server = go_to_hydrobaticpoint.hydrobaticpoint_server:main",
        ],
    },
)
