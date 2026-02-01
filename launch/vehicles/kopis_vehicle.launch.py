#!/usr/bin/env python3
"""
| File: kopis_vehicle.launch.py
| Author: Marcelo Jacinto (marcelo.jacinto@tecnico.ulisboa.pt)
| License: Non-Commercial & Non-Military BSD4 License. Copyright (c) 2026, Marcelo Jacinto. All rights reserved.
| Description: Base launch file to spawn the kopis vehicle model in Gazebo, along with its corresponding PX4 SITL instance.
"""
import os
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    return LaunchDescription([
        
        # Launch arguments
        DeclareLaunchArgument('vehicle_id', default_value='1', description='Drone ID in the network'),
        DeclareLaunchArgument('x', default_value='0.0', description='X position expressed in ENU'),
        DeclareLaunchArgument('y', default_value='0.0', description='Y position expressed in ENU'),
        DeclareLaunchArgument('z', default_value='0.0', description='Z position expressed in ENU'),
        DeclareLaunchArgument('R', default_value='0.0', description='Roll orientation expressed in ENU'),
        DeclareLaunchArgument('P', default_value='0.0', description='Pitch orientation expressed in ENU'),
        DeclareLaunchArgument('Y', default_value='0.0', description='Yaw orientation expressed in ENU'),
        
        # Launch the vehicle using the default vehicle launch file (which does all the heavy lifting)
        IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(get_package_share_directory('pegasus_gz'), 'launch/vehicles/default_vehicle.launch.py')),
            launch_arguments={
                'vehicle': 'kopis',
                'px4_config_file': '4503_pg_kopis',
                'id': LaunchConfiguration('vehicle_id'),
                'x': LaunchConfiguration('x'),
                'y': LaunchConfiguration('y'),
                'z': LaunchConfiguration('z'),
                'R': LaunchConfiguration('R'),
                'P': LaunchConfiguration('P'),
                'Y': LaunchConfiguration('Y')
            }.items()
        )
    ])