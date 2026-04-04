# jaka_ws/launch/real_bringup.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='jaka_hardware',
            executable='jaka_bridge_node',
            parameters=[{'use_sim': False}],
            output='screen'
        ),
        Node(
            package='apriltag_ros',
            executable='apriltag_node',
            parameters=['config/apriltag.yaml'],
            remappings=[
                ('/image_rect', '/camera/image_rect'),
                ('/camera_info', '/camera/camera_info'),
            ],
            output='screen'
        ),
        Node(
            package='hand_eye_calibration',
            executable='calibrator',
            output='screen'
        ),
        Node(
            package='visual_servo',
            executable='servo_node',
            output='screen'
        ),
        Node(
            package='swap_fsm',
            executable='swap_fsm_node',
            output='screen'
        ),
        Node(
            package='moveit_ros_move_group',
            executable='move_group',
            parameters=[{'use_sim_time': False}],
            output='screen'
        ),
    ])
