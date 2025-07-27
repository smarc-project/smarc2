from setuptools import find_packages, setup

package_name = 'dji_captain'

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
    maintainer='Ozer Ozkahraman',
    maintainer_email='ozero@kth.se',
    description='Captain interface to a dji psdk drone',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'dji_captain = dji_captain.dji_captain:main',
            'unity_translator = dji_captain.unity_translator:main'
        ],
    },
)
