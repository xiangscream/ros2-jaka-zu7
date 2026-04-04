# jaka_ws/launch/sim_bringup.launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os

def generate_launch_description():
    pkg_share = FindPackageShare('jaka_description').find('jaka_description')
    urdf_file = os.path.join(pkg_share, 'urdf/jaka_zu7_gazebo.urdf')
    with open(urdf_file, 'r') as f:
        robot_description = f.read()
    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen'
        ),
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=['-entity', 'jaka_zu7', '-topic', 'robot_description'],
            output='screen'
        ),
        Node(
            package='controller_manager',
            executable='ros2_control_node',
            parameters=[{'robot_description': robot_description}],
            output='screen'
        ),
        Node(
            package='ros2_controllers',
            executable='joint_trajectory_controller',
            parameters=[{
                'joints': ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6'],
                'command_interfaces': ['velocity'],
                'state_interfaces': ['position', 'velocity']
            }],
            remappings=[('/joint_trajectory', '/controllers/joint_trajectory_command')],
            output='screen'
        ),
        Node(
            package='moveit_ros_move_group',
            executable='move_group',
            parameters=[{'robot_description': robot_description, 'use_sim_time': True}],
            output='screen'
        ),
    ])
