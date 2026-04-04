# visual_servo/launch/servo.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='visual_servo',
            executable='servo_node',
            name='visual_servo',
            output='screen'
        )
    ])
