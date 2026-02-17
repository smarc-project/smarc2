from setuptools import find_packages, setup
from glob import glob
import os
package_name = 'brov2heavy_description'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))), 
        (os.path.join('share', package_name, 'urdf'), glob(os.path.join('urdf', '*urdf.[xacro]*'))),
        # (os.path.join('share', package_name, 'mesh'), glob(os.path.join('mesh', '*dae*, *stl*'))),
        (os.path.join('share', package_name, 'mesh'), glob(os.path.join('mesh', '*.dae')) + glob(os.path.join('mesh', '*.stl'))),
        (os.path.join('share', package_name, 'robots'), glob(os.path.join('robots', '*urdf.[xacro]*')))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='babypool',
    maintainer_email='babypool@todo.todo',
    description='TODO: Package description',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
