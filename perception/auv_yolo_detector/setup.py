from setuptools import find_packages, setup
import glob, os

package_name = 'auv_yolo_detector'

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
    maintainer='fm',
    maintainer_email='franmira2003@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "auv_yolo_detector = auv_yolo_detector.auv_yolo_detector:main"
        ],
    },
)
