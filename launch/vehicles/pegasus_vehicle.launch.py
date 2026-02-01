#!/usr/bin/env python3
"""
| File: pegasus_vehicle.launch.py
| Author: Marcelo Jacinto (marcelo.jacinto@tecnico.ulisboa.pt)
| License: Non-Commercial & Non-Military BSD4 License. Copyright (c) 2026, Marcelo Jacinto. All rights reserved.
| Description: Base launch file to spawn the pegasus vehicle model in Gazebo, along with its corresponding PX4 SITL instance.
"""
import os
from launch_ros.actions import Node
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
                'vehicle': 'pegasus',
                'px4_config_file': '4502_pg_pegasus',
                'id': LaunchConfiguration('vehicle_id'),
                'x': LaunchConfiguration('x'),
                'y': LaunchConfiguration('y'),
                'z': LaunchConfiguration('z'),
                'R': LaunchConfiguration('R'),
                'P': LaunchConfiguration('P'),
                'Y': LaunchConfiguration('Y')
            }.items()
        ),

        # Launch the bridge and get the realsense topics bridged from gazebo to ROS2
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                # Format: /gazebo_topic@ros_msg_type@gazebo_msg_type
                
                # 1. Camera Info
                '/world/simulation_world/model/pegasus_1/link/base_link/sensor/realsense_d435i/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
                
                # 2. RGB Image
                '/world/simulation_world/model/pegasus_1/link/base_link/sensor/realsense_d435i/image@sensor_msgs/msg/Image[gz.msgs.Image',
                
                # 3. Depth Image
                '/world/simulation_world/model/pegasus_1/link/base_link/sensor/realsense_d435i/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
                
                # 4. Point Cloud
                 '/world/simulation_world/model/pegasus_1/link/base_link/sensor/realsense_d435i/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked'
            ],
            # This is where you specify the output topics
            remappings=[
                (f'/world/simulation_world/model/pegasus_1/link/base_link/sensor/realsense_d435i/camera_info', '/camera/camera_info'),
                (f'/world/simulation_world/model/pegasus_1/link/base_link/sensor/realsense_d435i/image',       '/camera/image_raw'),
                (f'/world/simulation_world/model/pegasus_1/link/base_link/sensor/realsense_d435i/depth_image', '/camera/depth/image_raw'),
                (f'/world/simulation_world/model/pegasus_1/link/base_link/sensor/realsense_d435i/points',      '/camera/points'),
            ],
            output='screen'
        )
    ])