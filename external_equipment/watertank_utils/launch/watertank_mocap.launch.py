# Copyright (c) 2019, Samsung Electronics Inc., Vinnam Kim
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, 
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in the 
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its 
#    contributors may be used to endorse or promote products derived from 
#    this software without specific prior written permission. 
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node, SetParameter
from launch_ros.substitutions import FindPackagePrefix, FindPackageShare
from launch.substitutions import TextSubstitution, PathJoinSubstitution
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import ThisLaunchFileDir
from launch.actions import ExecuteProcess
import xacro

def generate_launch_description():

    return LaunchDescription([
        
        # Qualisys driver
        IncludeLaunchDescription(
        PathJoinSubstitution([FindPackageShare('mocap_qualisys'), 'launch', 'qualisys.launch.py']),
        launch_arguments={
            'server_address': '192.168.32.32'}.items()
        ),

        # RVIZ2 + robot models come in this launch file
        # TODO: modify to add more than one Bluerov with different names
        IncludeLaunchDescription(
        PathJoinSubstitution([FindPackageShare('watertank_utils'), 'launch', 'tank_visualization.launch.py']),
        launch_arguments={
            'brov_name': 'bluerov_saab',
            'brov_package': 'brov2heavy_description',
            'brov_package_path': PathJoinSubstitution(['robots', 'brov2heavy_default.urdf.xacro']),
            'tank_package': 'watertank_description',
            'tank_package_path': PathJoinSubstitution(['robots', 'watertank_default.urdf.xacro'])
            }.items()
        ),

        # Utils here
        Node(
            package='watertank_utils',
            executable='watertank_tf_utils',
            name='watertank_tf_utils_node',
            # parameters=[],
            output='screen',
            arguments=['--ros-args', '--log-level', 'info'])

    ])
    
generate_launch_description()
