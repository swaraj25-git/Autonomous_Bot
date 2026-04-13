import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    # 1. Include the Robot State Publisher from the description package
    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('my_bot_description'), 'launch', 'rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'false'}.items()
    )

    # 2. Start the RViz Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    # 3. Start the IMU Node
    imu_node = Node(
        package='my_bot_hardware',
        executable='mpu6050',
        name='mpu6050_node',
        output='screen'
    )

    # 4. Start the Arduino Serial Bridge
    arduino_node = Node(
        package='my_bot_hardware',
        executable='arduino_serial',
        name='arduino_serial_node',
        output='screen'
    )

    # 5. Start the RPLidar Node
    # Note: frame_id matches your lidar.xacro link name
    lidar_node = Node(
        package='sllidar_ros2',
        executable='sllidar_node',
        name='sllidar_node',
        parameters=[{
            'serial_port': '/dev/ttyUSB1', 
            'frame_id': 'laser_frame',
            'angle_compensate': True,
            'scan_mode': 'Standard'
        }],
        output='screen'
    )

    return LaunchDescription([
        rsp,
        rviz_node,
        imu_node,
        arduino_node,
        lidar_node
    ])