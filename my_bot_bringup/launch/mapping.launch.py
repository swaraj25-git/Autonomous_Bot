import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    bringup_pkg = get_package_share_directory('my_bot_bringup')
    
    # Path to EKF config
    ekf_config_path = os.path.join(bringup_pkg, 'config', 'ekf.yaml')

    # 1. EKF Node
    node_ekf = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config_path]
    )

    # 2. SLAM Toolbox Node (Online Async for real-time mapping)
    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py'
        )]),
        launch_arguments={'use_sim_time': 'false'}.items()
    )

    return LaunchDescription([
        node_ekf,
        slam_toolbox
    ])