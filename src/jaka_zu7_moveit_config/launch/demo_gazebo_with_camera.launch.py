from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import (
    generate_rsp_launch,
    generate_move_group_launch,
    generate_moveit_rviz_launch,
)
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # Build moveit config with xacro args for gazebo
    moveit_config = (
        MoveItConfigsBuilder("jaka_zu7", package_name="jaka_zu7_moveit_config")
        .robot_description(mappings={"use_gazebo": "true"})
        .to_moveit_configs()
    )

    # Get launch package path
    launch_package_path = moveit_config.package_path

    ld = LaunchDescription()

    # Declare arguments
    ld.add_action(DeclareLaunchArgument("use_rviz", default_value="true"))

    # 1) robot_state_publisher
    rsp_launch = generate_rsp_launch(moveit_config)
    ld.add_action(rsp_launch)

    # 2) Launch Gazebo with custom world
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("ros_gz_sim"), "launch", "gz_sim.launch.py")
        ),
        launch_arguments={
            "gz_args": str(launch_package_path / "worlds/jaka_zu7_with_camera.world") + " -r",
        }.items()
    )
    ld.add_action(gazebo_launch)

    # 3) Spawn robot via ros_gz_sim create - waits for robot_description topic
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', '/robot_description',
            '-name', 'jaka_zu7',
            '-allow_renaming',
        ],
        output='screen',
    )
    ld.add_action(spawn_robot)

    # 4) Launch MoveIt
    moveit_launch = generate_move_group_launch(moveit_config)
    ld.add_action(moveit_launch)

    # 5) Launch RViz
    rviz_launch = generate_moveit_rviz_launch(moveit_config)
    ld.add_action(rviz_launch)

    # 6) Spawn controllers to Gazebo's controller_manager
    # Note: Do NOT start ros2_control_node! Gazebo's gz_ros2_control plugin
    # already provides /controller_manager. We only spawn controllers to it.
    controller_spawner = TimerAction(
        period=5.0,  # Wait for gz_ros2_control to be ready
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['jaka_zu7_controller', '--controller-manager', '/controller_manager'],
                output='screen',
            ),
        ]
    )
    ld.add_action(controller_spawner)

    joint_state_broadcaster_spawner = TimerAction(
        period=5.5,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
                output='screen',
            ),
        ]
    )
    ld.add_action(joint_state_broadcaster_spawner)

    return ld
