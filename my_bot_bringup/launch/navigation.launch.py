import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument

def generate_launch_description():
    bringup_pkg = get_package_share_directory('my_bot_bringup')
    nav2_pkg = get_package_share_directory('nav2_bringup')
    
    # Paths
    nav2_params_path = os.path.join(bringup_pkg, 'config', 'nav2_params.yaml')
    default_map_path = os.path.join(bringup_pkg, 'maps', 'my_map.yaml') # Assume you save maps here

    map_arg = DeclareLaunchArgument('map', default_value=default_map_path, description='Full path to map yaml file to load')

    # Include Nav2 Bringup Launch
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(nav2_pkg, 'launch', 'bringup_launch.py')]),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'use_sim_time': 'false',
            'params_file': nav2_params_path
        }.items()
    )

    return LaunchDescription([
        map_arg,
        nav2_bringup
    ])