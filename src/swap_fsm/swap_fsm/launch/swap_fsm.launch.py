from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='swap_fsm',
            executable='swap_fsm_node',
            name='swap_fsm',
            output='screen'
        )
    ])
