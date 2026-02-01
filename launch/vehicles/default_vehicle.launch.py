import os
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import ExecuteProcess, IncludeLaunchDescription, DeclareLaunchArgument, SetEnvironmentVariable, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def launch_vehicle(context, *args, **kwargs):

    # Get the id of the drone to be launched
    vehicle_id = int(LaunchConfiguration('vehicle_id').perform(context))
    port_increment = vehicle_id - 1

    # Define the vehicle spawn name
    vehicle_model = 'x500'
    vehicle_spawn_name = vehicle_model + '_' + str(vehicle_id)

    # Get the PX4 directory from the environment
    PX4_DIR = os.environ['PX4_DIR']
    PX4_RUN_DIR = os.environ['PX4_RUN_DIR']
   
    # 1. Launch PX4 SITL
    px4_sitl = ExecuteProcess(
        cmd=[
            PX4_DIR + '/build/px4_sitl_default/bin/px4',
            PX4_DIR + '/ROMFS/px4fmu_common/',
            '-s',
            PX4_DIR + '/ROMFS/px4fmu_common/init.d-posix/rcS',
            '-i ' + str(port_increment)
        ],
        prefix='bash -c "$0 $@"',
        cwd=PX4_RUN_DIR,
        output='screen',
        env={
            'ROS_VERSION': '2',
            'PX4_GZ_STANDALONE': '1',
            'PX4_GZ_MODEL_NAME': vehicle_spawn_name,
            'PX4_SYS_AUTOSTART': '4001',
            'PX4_GZ_WORLD': 'simulation_world',
            'PATH': os.environ.get('PATH', ''),
            'GZ_CONFIG_PATH': os.environ.get('GZ_CONFIG_PATH', ''),
        },
        shell=False
    )

    # 2. Spawn the Model in Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-file', os.path.join(get_package_share_directory('pegasus_gz'), 'models', vehicle_model, 'model.sdf'),
            '-name', vehicle_spawn_name,
            '-x', LaunchConfiguration('x').perform(context),
            '-y', LaunchConfiguration('y').perform(context), 
            '-z', LaunchConfiguration('z').perform(context),
            '-R', LaunchConfiguration('R').perform(context),
            '-P', LaunchConfiguration('P').perform(context),
            '-Y', LaunchConfiguration('Y').perform(context),
        ],
        output='screen'
    )

    return [
        px4_sitl,
        spawn_entity,
    ]

def generate_launch_description():

    # Create a temporary directory for PX4 runtime files
    PX4_RUN_DIR = '/tmp/px4_run_dir'
    os.makedirs(PX4_RUN_DIR, exist_ok=True)

    # Check if PX4_DIR is set in the environment
    if 'PX4_DIR' not in os.environ:
        raise EnvironmentError("Please set the environment variable 'PX4_DIR' to point to your PX4-Autopilot directory.")

    # Get the PX4 directory from the environment
    PX4_DIR = os.environ['PX4_DIR']

    pkg_pegasus_gz = get_package_share_directory('pegasus_gz')
    pegasus_gz_worlds = os.path.join(pkg_pegasus_gz, 'worlds')
    pegasus_gz_models = os.path.join(pkg_pegasus_gz, 'models')

    # Setup the gazebo path to include PX4 models and worlds
    px4_gz_models = os.path.join(PX4_DIR, 'Tools', 'simulation', 'gz', 'models')
    px4_gz_worlds = os.path.join(PX4_DIR, 'Tools', 'simulation', 'gz', 'worlds')
    px4_gz_plugins = os.path.join(PX4_DIR, 'build', 'px4_sitl_default', 'src', 'modules', 'simulation', 'gz_plugins')
    px4_gz_server_config = os.path.join(PX4_DIR, 'src', 'modules', 'simulation', 'gz_bridge', 'server.config')

    # Setup GZ_SIM environment variables
    gz_sim_resource_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    gz_sim_system_plugin_path = os.environ.get('GZ_SIM_SYSTEM_PLUGIN_PATH', '')

    return LaunchDescription([
        # Environment gazebo variables
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', f"{gz_sim_resource_path}:{px4_gz_models}:{px4_gz_worlds}:{pegasus_gz_models}:{pegasus_gz_worlds}"),
        SetEnvironmentVariable('GZ_SIM_SYSTEM_PLUGIN_PATH', f"{gz_sim_system_plugin_path}:{px4_gz_plugins}"),
        SetEnvironmentVariable('GZ_SIM_SERVER_CONFIG_PATH', px4_gz_server_config),
        SetEnvironmentVariable('GZ_TRANSPORT_LOCALHOST_ONLY','1'),
        SetEnvironmentVariable('IGN_TRANSPORT_DISABLE_MULTICAST', '1'),
        SetEnvironmentVariable('GZ_IP', '127.0.0.1'),

        # Environment PX4 variables
        SetEnvironmentVariable('PX4_RUN_DIR', PX4_RUN_DIR),

        # Get the vehicle id and initial position/orientation (ENU frame)
        DeclareLaunchArgument('vehicle', default_value='x500', description='Vehicle model to spawn'),
        DeclareLaunchArgument('vehicle_id', default_value='1', description='Drone ID in the network'),
        DeclareLaunchArgument('x', default_value='0.0', description='X position expressed in ENU'),
        DeclareLaunchArgument('y', default_value='0.0', description='Y position expressed in ENU'),
        DeclareLaunchArgument('z', default_value='0.0', description='Z position expressed in ENU'),
        DeclareLaunchArgument('R', default_value='0.0', description='Roll orientation expressed in ENU'),
        DeclareLaunchArgument('P', default_value='0.0', description='Pitch orientation expressed in ENU'),
        DeclareLaunchArgument('Y', default_value='0.0', description='Yaw orientation expressed in ENU'),

        # Launch the actual vehicle inside gazebo, along with the corresponding PX4 SITL instance
        OpaqueFunction(function=launch_vehicle)
    ])