from setuptools import find_packages, setup
import os
from glob import glob

package_name = "rtmp_ros"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Your Name",
    maintainer_email="todo@example.com",
    description="Stream ROS 2 image topics to an RTMP server via GStreamer H.264.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "rtmp_ros_node = rtmp_ros.rtmp_ros_node:main",
        ],
    },
)
