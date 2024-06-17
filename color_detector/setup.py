# from setuptools import find_packages, setup

# package_name = 'color_detector'

# setup(
#     name=package_name,
#     version='0.0.0',
#     packages=find_packages(exclude=['test']),
#     data_files=[
#         ('share/ament_index/resource_index/packages',
#             ['resource/' + package_name]),
#         ('share/' + package_name, ['package.xml']),
#     ],
#     install_requires=['setuptools'],
#     zip_safe=True,
#     maintainer='Aryan',
#     maintainer_email='aryand@kth.se',
#     description='color gist detector',
#     license='MIT',
#     tests_require=['pytest'],
#     entry_points={
#         'console_scripts': [
#         ],
#     },
# )

from setuptools import setup

package_name = 'color_detector'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    py_modules=[],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='A ROS2 package for detecting yellow objects in camera feed using OpenCV.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'color_detector = color_detector.color_detector:main',
        ],
    },
)

