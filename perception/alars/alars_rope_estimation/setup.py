import glob, os

from setuptools import find_packages, setup

package_name = 'alars_rope_estimation'

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
    maintainer='Josef Kahoun',
    maintainer_email='kahoun@kth.se',
    description='Estimates rope direction and force from 3/4 winch load cells.',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'rope_estimation_node = alars_rope_estimation.rope_estimation_node:main',
        ],
    },
)
