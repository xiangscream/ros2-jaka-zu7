"""
Launch file for JAKA vision apriltag detection

Starts:
    - apriltag detector (using apriltag_ros)
    - apriltag detector node (transforms to base_link)
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # Declare launch arguments
    camera_topic = DeclareLaunchArgument(
        'camera_topic',
        default_value='/camera/image_raw',
        description='Camera image topic'
    )

    camera_info_topic = DeclareLaunchArgument(
        'camera_info_topic',
        default_value='/camera/camera_info',
        description='Camera info topic'
    )

    tag_family = DeclareLaunchArgument(
        'tag_family',
        default_value='36h11',
        description='Apriltag family'
    )

    tag_size = DeclareLaunchArgument(
        'tag_size',
        default_value='0.173',
        description='Tag edge size in meters'
    )

    # Apriltag detector node (transforms detections to base_link)
    detector_node = Node(
        package='jaka_vision',
        executable='apriltag_detector_node',
        name='apriltag_detector_node',
        output='screen',
        parameters=[{
            'base_frame': 'base_link',
        }],
        remappings=[
            ('/apriltag/detections', '/detections'),
            ('/camera/camera_info', LaunchConfiguration('camera_info_topic')),
        ]
    )

    return LaunchDescription([
        camera_topic,
        camera_info_topic,
        tag_family,
        tag_size,
        detector_node,
    ])
