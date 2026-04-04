from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='hand_eye_calibration',
            executable='calibrator',
            name='hand_eye_calibrator',
            parameters=['config/calibration_params.yaml'],
            output='screen'
        )
    ])
