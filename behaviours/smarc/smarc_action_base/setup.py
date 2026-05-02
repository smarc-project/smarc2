from setuptools import find_packages, setup

package_name = 'smarc_action_base'

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
    maintainer='ozero',
    maintainer_email='ozero@kth.se',
    description='Base package for SMARC action servers and clients',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'trigger_service_action_server = smarc_action_base.trigger_service_action_server:main'
        ],
    },
)
