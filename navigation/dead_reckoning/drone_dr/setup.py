from setuptools import find_packages, setup
import glob, os

package_name = 'drone_dr'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    # py_modules=['estimator', 'KNN','model_kf','model_ekf'], 
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob.glob('launch/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='aryan',
    maintainer_email='aryand@kth.se',
    description='dead reckoning for drone',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
	    'estimator = drone_dr.drone_dr:main', 
            
        ],
    },
)
