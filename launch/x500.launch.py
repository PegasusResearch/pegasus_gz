import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, DeclareLaunchArgument, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

PX4_RUN_DIR = os.environ.get('HOME') + '/tmp/px4_run_dir'
os.makedirs(PX4_RUN_DIR, exist_ok=True)

def generate_launch_description():


    pkg_pegasus_gz = get_package_share_directory('pegasus_gz')
    pegasus_gz_worlds = os.path.join(pkg_pegasus_gz, 'worlds')
    pegasus_gz_models = os.path.join(pkg_pegasus_gz, 'models')

    # Setup the gazebo path to include PX4 models and worlds
    px4_dir = os.path.expanduser('~/Developer/PX4-Autopilot')
    px4_gz_models = os.path.join(px4_dir, 'Tools', 'simulation', 'gz', 'models')
    px4_gz_worlds = os.path.join(px4_dir, 'Tools', 'simulation', 'gz', 'worlds')
    px4_gz_plugins = os.path.join(px4_dir, 'build', 'px4_sitl_default', 'src', 'modules', 'simulation', 'gz_plugins')
    px4_gz_server_config = os.path.join(px4_dir, 'src', 'modules', 'simulation', 'gz_bridge', 'server.config')

    # Setup GZ_SIM environment variables
    gz_sim_resource_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    gz_sim_system_plugin_path = os.environ.get('GZ_SIM_SYSTEM_PLUGIN_PATH', '')
    gz_sim_server_config_path = os.environ.get('GZ_SIM_SERVER_CONFIG_PATH', '')
                            
    gz_sim_resource_path = f"{gz_sim_resource_path}:{px4_gz_models}:{px4_gz_worlds}:{pegasus_gz_models}:{pegasus_gz_worlds}"
    gz_sim_system_plugin_path = f"{gz_sim_system_plugin_path}:{px4_gz_plugins}"
    gz_sim_server_config_path = px4_gz_server_config

    # Use the resources inside the PX4 directory as well as this package
    #gz_resource_path = os.path.join(pkg_pegasus_gz, 'models') + \
    #':' + os.path.join(px4_dir, 'Tools', 'simulation', 'gz', 'models') + \
    #':' + os.path.join(px4_dir, 'Tools', 'simulation', 'gz', 'worlds')

    set_gz_path = SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', gz_sim_resource_path)
    set_gz_sim_system_plugin = SetEnvironmentVariable('GZ_SIM_SYSTEM_PLUGIN_PATH', gz_sim_system_plugin_path)
    set_gz_sim_server_config = SetEnvironmentVariable('GZ_SIM_SERVER_CONFIG_PATH', gz_sim_server_config_path)

    # 1. Launch Gazebo World
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={'gz_args': f"-r {pkg_pegasus_gz}/worlds/taguspark_arena/taguspark_arena.sdf"}.items(),
    )

    # GZ_SIM_RESOURCE_PATH=/home/marcelo/.simulation-gazebo/models GZ_SIM_SERVER_CONFIG_PATH=/home/marcelo/.simulation-gazebo/server.config gz sim -r /home/marcelo/.simulation-gazebo/worlds/default.sdf

    # 2. Launch PX4 SITL
    # We use ExecuteProcess to run the binary directly
    # px4_sitl = ExecuteProcess(
    #     cmd=[
    #         f'{px4_dir}/build/px4_sitl_default/bin/px4',
    #         f'{px4_dir}/ROMFS/px4fmu_common',
    #         '-s', 
    #         f'{px4_dir}/ROMFS/px4fmu_common/init.d-posix/rcS',
    #         '-i', '0'
    #     ],
    #     prefix='bash -c "$0 $@"',
    #     cwd=PX4_RUN_DIR,
    #     env={'PX4_SYS_AUTOSTART': '4001',
    #          'PX4_GZ_STANDALONE': '1',
    #          'PX4_GZ_MODEL_NAME': 'x500',
    #          'PX4_SIM_MODEL': 'gz_x500',
    #          'ROS_VERSION': '2'}, # x500 ID
    #     output='screen'
    # )

    environment = os.environ
    environment["PX4_SIM_MODEL"] = 'gz_x500'
    environment["ROS_VERSION"] = '2'
    environment["PX4_GZ_STANDALONE"] = '1'
    environment["PX4_GZ_MODEL_NAME"] = 'x500'
    environment["PX4_SYS_AUTOSTART"] = '4001'  # x500

    px4_sitl = ExecuteProcess(
        cmd=[
            px4_dir + '/build/px4_sitl_default/bin/px4',
            px4_dir + '/ROMFS/px4fmu_common/',
            '-s',
            px4_dir + '/ROMFS/px4fmu_common/init.d-posix/rcS',
            '-i ' + '0'
        ],
        prefix='bash -c "$0 $@"',
        cwd=PX4_RUN_DIR,
        output='screen',
        env=environment,
        shell=False
    )

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
        set_gz_sim_system_plugin,
        set_gz_sim_server_config,
        gz_sim,
        px4_sitl,
        spawn_entity,
        bridge
    ])