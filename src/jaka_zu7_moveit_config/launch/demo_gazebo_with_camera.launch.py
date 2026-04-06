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
    # Note: We use the basic jaka_zu7.urdf.xacro because the world file
    # already contains the complete robot with camera inline
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
    ld.add_action(DeclareLaunchArgument("use_camera_bridge", default_value="true"))

    # 1) robot_state_publisher - publishes robot description for MoveIt
    rsp_launch = generate_rsp_launch(moveit_config)
    ld.add_action(rsp_launch)

    # 2) Launch Gazebo with world file that contains robot INLINE
    # The robot model is NOT dynamically spawned - it loads with the world
    # This ensures camera sensor is properly registered by sensors-system
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("ros_gz_sim"), "launch", "gz_sim.launch.py")
        ),
        launch_arguments={
            # Use the eye-in-hand camera world file (robot inline in world)
            "gz_args": str(launch_package_path / "worlds/jaka_zu7_eye_in_hand_camera.world") + " -r",
        }.items()
    )
    ld.add_action(gazebo_launch)

    # 3) NO robot spawner needed! Robot is already in the world file

    # 4) Launch MoveIt move_group
    moveit_launch = generate_move_group_launch(moveit_config)
    ld.add_action(moveit_launch)

    # 5) Launch RViz
    rviz_launch = generate_moveit_rviz_launch(moveit_config)
    ld.add_action(rviz_launch)

    # 6) Spawn controllers to Gazebo's controller_manager
    # Gazebo's gz_ros2_control plugin provides /controller_manager
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

    # 7) Camera bridge - bridges Gazebo camera topic to ROS
    # Camera topic: /world/jaka_zu7_eye_in_hand/model/jaka_zu7/link/Link_6/sensor/camera_sensor/image
    camera_bridge = TimerAction(
        period=10.0,  # Wait for Gazebo sensors to initialize
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory("jaka_vision"),
                        "launch",
                        "gazebo_camera_bridge.launch.py"
                    )
                ),
            )
        ]
    )
    ld.add_action(camera_bridge)

    return ld
