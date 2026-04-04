"""
Launch file for JAKA ZU7 with Eye-in-Hand Camera

Adds camera bridge to existing Gazebo + MoveIt setup.
Uses image_bridge for image topics (not parameter_bridge).

Usage:
    # 首先启动 Gazebo + MoveIt
    ros2 launch jaka_zu7_moveit_config demo_gazebo.launch.py

    # 然后在另一个终端启动相机桥接
    ros2 launch jaka_vision gazebo_camera_bridge.launch.py
"""

import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # ros_gz_image bridge for camera topics - uses image_bridge which is required for image transport
    camera_image_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        name='camera_image_bridge',
        arguments=[
            '/camera/image',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    # Relay camera_info to proper topic path
    camera_info_relay = Node(
        package='topic_tools',
        executable='relay',
        name='camera_info_relay',
        arguments=['camera/camera_info', 'camera/image/camera_info'],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        camera_image_bridge,
        camera_info_relay,
    ])
