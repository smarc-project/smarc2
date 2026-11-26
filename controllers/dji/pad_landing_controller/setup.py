from setuptools import find_packages, setup
from glob import glob

package_name = 'pad_landing_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', ['config/landing_params.yaml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Cristhian Mallqui',
    maintainer_email='ckmc@kth.se',
    description='Model-based autonomous landing on pad pipeline',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pad_landing_as = pad_landing_controller.pad_landing_as:main',
        ],
    },
)
