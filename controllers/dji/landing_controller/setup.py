from setuptools import find_packages, setup

package_name = 'landing_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
        ('share/' + package_name + '/launch', [
            'launch/alars_stack_landing.launch.py',
        ]),
        ('share/' + package_name + '/config', [
            'config/landing_params.yaml',
        ]),
    ],
    install_requires=['setuptools', 'numpy', 'PyYAML', 'scipy'],
    zip_safe=True,
    maintainer='Cristhian Mallqui',
    maintainer_email='ckmc@kth.se',
    description='Model-based relative landing controller for ALARS.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'relative_state = landing_controller.relative_state_node:main',
            'landing_manager = landing_controller.landing_manager_node:main',
            'lqr_controller = landing_controller.lqr_controller_node:main',
            'velocity_command_mux = landing_controller.velocity_command_mux_node:main',
            'object_array_to_odometry = landing_controller.object_array_to_odometry_node:main',
        ],
    },
)
