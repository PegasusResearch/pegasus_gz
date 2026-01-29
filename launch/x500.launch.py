import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, DeclareLaunchArgument, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():


    pkg_pegasus_gz = get_package_share_directory('pegasus_gz')
    px4_dir = os.path.expanduser('~/Developer/PX4-Autopilot')

    # Use the resources inside the PX4 directory as well as this package
    gz_resource_path = os.path.join(pkg_pegasus_gz, 'models') + \
    ':' + os.path.join(px4_dir, 'Tools', 'simulation', 'gz', 'models') + \
    ':' + os.path.join(px4_dir, 'Tools', 'simulation', 'gz', 'worlds')

    set_gz_path = SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', gz_resource_path)

    # 1. Launch Gazebo World
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={'gz_args': f"-r {pkg_pegasus_gz}/worlds/lawn.sdf"}.items(),
    )

    # 2. Launch PX4 SITL
    # We use ExecuteProcess to run the binary directly
    # px4_sitl = ExecuteProcess(
    #     cmd=[
    #         f'{px4_dir}/build/px4_sitl_default/bin/px4',
    #         f'{px4_dir}/ROMFS/px4fmu_common',
    #         '-s', 'etc/init.d-posix/rcS'
    #     ],
    #     env={'PX4_SYS_AUTOSTART': '4001'}, # x500 ID
    #     output='screen'
    # )

    # 3. Spawn the Model in Gazebo
    # Note: Ensure your x500 SDF is compatible with New Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-file', os.path.join(pkg_pegasus_gz, 'models', 'x500_base', 'model.sdf'),
            '-name', 'x500',
            '-x', '0', '-y', '0', '-z', '0.5'
        ],
        output='screen'
    )

    # 4. Bridge (Crucial for ROS 2 <-> Gazebo communication)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/world/default/model/x500/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ],
        output='screen'
    )

    return LaunchDescription([
        set_gz_path,
        gz_sim,
        #px4_sitl,
        spawn_entity,
        #bridge
    ])