"""
Launch file for Gazebo Camera Bridge

Bridges Gazebo camera topics to ROS 2 image topics using ros_gz_bridge.

Usage:
    # 首先启动 Gazebo + MoveIt with camera world
    ros2 launch jaka_zu7_moveit_config demo_gazebo_with_camera.launch.py

    # 然后在另一个终端启动相机桥接
    ros2 launch jaka_vision gazebo_camera_bridge.launch.py

Gazebo Camera Topic Mapping (Eye-in-Hand):
    Source (Gazebo):  /world/jaka_zu7_eye_in_hand/model/jaka_zu7/link/Link_6/sensor/camera_sensor/image
    Target (ROS 2):   /camera/image_raw
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node


def generate_launch_description():
    # Declare launch arguments
    declared_arguments = [
        DeclareLaunchArgument('use_sim_time', default_value='true'),
    ]

    # Gazebo Fortress camera topic path for eye-in-hand camera
    # Format: /world/<world_name>/model/<model_name>/link/<link_name>/sensor/<sensor_name>/image
    gz_camera_topic = '/world/jaka_zu7_eye_in_hand/model/jaka_zu7/link/Link_6/sensor/camera_sensor/image'
    ros_camera_topic = '/camera/image_raw'

    # ros_gz_bridge for explicit image topic mapping
    # Bridge Gazebo Image to ROS Image
    camera_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='camera_bridge',
        arguments=[
            f'{gz_camera_topic}@sensor_msgs/msg/Image@ros_gz_interfaces/msg/Image'
        ],
        parameters=[{'use_sim_time': True}],
        remappings=[
            (gz_camera_topic, ros_camera_topic),
        ],
        output='screen',
    )

    # Camera info relay (for camera calibration)
    # Try to relay camera_info if available from Gazebo
    gz_camera_info_topic = gz_camera_topic.replace('/image', '/camera_info')

    return LaunchDescription([
        *declared_arguments,
        camera_bridge,
    ])
