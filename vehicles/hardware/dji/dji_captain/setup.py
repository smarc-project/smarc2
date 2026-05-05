from setuptools import find_packages, setup
from glob import glob

package_name = 'dji_captain'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Ozer Ozkahraman',
    maintainer_email='ozero@kth.se',
    description='Captain interface to a dji psdk drone',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'dji_captain = dji_captain.dji_captain:main',
            'esc_splitter = dji_captain.dji_esc_data_splitter:main',
            'service_caller = dji_captain.dji_service_caller:main',
            'joy_tester = dji_captain.joy_tester:main',
            'psdk_faker = dji_captain.psdk_faker:main',
        ],
    },
)
