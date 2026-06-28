from setuptools import find_packages, setup

package_name = 'prox_ops_bt'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, [
            'README.md',
            'prox_ops_bt/goal_example.json',
            'prox_ops_bt/goal_example.md',
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='aldo',
    maintainer_email='aldot@kth.se',
    description='Python behaviour tree for Evolo prox-ops missions.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'prox_ops_bt = prox_ops_bt.prox_ops_bt:main',
        ],
    },
)
