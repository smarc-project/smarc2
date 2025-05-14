from setuptools import find_packages, setup

package_name = 'tmux_alert'

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
    maintainer='David Doerner',
    maintainer_email='ddorner@kth.se',
    description='Alert node in tmux for battery, leak, and temperature monitoring',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'tmux_alert = tmux_alert.AlertNode:main',
        ],
    },
)
