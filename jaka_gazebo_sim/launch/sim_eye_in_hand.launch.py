"""
Launch file for JAKA ZU7 Eye-in-Hand Camera Gazebo Simulation

The robot is loaded INLINE in the SDF world file, not dynamically spawned.
This ensures the camera sensor is properly registered by the sensors-system.

Starts:
1. Robot state publisher
2. Gazebo Sim (Fortress) with inline world
3. ros2control controller spawner (if ros2_control tag present in URDF)
4. Camera image bridge (Gazebo -> ROS2)

Usage:
    ros2 launch jaka_gazebo_sim sim_eye_in_hand.launch.py
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration

import os
from ament_index_python.packages import get_package_share_directory


def get_robot_description():
    """Generate robot description by running xacro"""
    pkg_share = get_package_share_directory('jaka_gazebo_sim')
    urdf_file = os.path.join(pkg_share, 'urdf', 'jaka_zu7_with_camera.urdf.xacro')

    # Run xacro and capture output
    import subprocess
    result = subprocess.run(
        ['xacro', urdf_file, 'use_gazebo:=true'],
        capture_output=True,
        text=True
    )
    return result.stdout


def generate_launch_description():
    # Package paths
    pkg_share = get_package_share_directory('jaka_gazebo_sim')
    moveit_config_share = get_package_share_directory('jaka_zu7_moveit_config')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')

    # Gazebo world file (inline robot loading)
    world_file = os.path.join(
        pkg_share,
        'worlds',
        'jaka_zu7_eye_in_hand.world'
    )

    # ros2control parameters
    ros2_control_params = os.path.join(
        moveit_config_share,
        'config',
        'ros2_controllers.yaml'
    )

    # Camera topic paths
    gz_camera_topic = '/world/jaka_zu7_eye_in_hand/model/jaka_zu7/link/Link_6/sensor/camera_sensor/image'
    ros_camera_topic = '/camera/image_raw'

    # Declare arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock time'
    )

    # Robot state publisher - with robot_description set directly
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'robot_description': get_robot_description(),
        }],
        output='screen'
    )

    # Import ros_gz_sim launch to start Gazebo with proper environment
    from launch.actions import IncludeLaunchDescription
    from launch.launch_description_sources import PythonLaunchDescriptionSource

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': world_file,
            'gz_version': '6',  # Fortress
        }.items()
    )

    # ros2control spawner - loads controllers
    controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        name='ros2_control_spawner',
        arguments=[
            'jaka_zu7_controller',
            'joint_state_broadcaster',
            '--param-file', ros2_control_params,
            '--controller-manager', '/controller_manager'
        ],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )

    # Camera image bridge (Gazebo sensor topic -> ROS2 topic)
    camera_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        name='camera_image_bridge',
        arguments=[gz_camera_topic],
        remappings=[
            (gz_camera_topic, ros_camera_topic)
        ],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )

    return LaunchDescription([
        use_sim_time_arg,
        robot_state_publisher,
        gazebo_launch,
        TimerAction(period=3.0, actions=[controller_spawner]),
        camera_bridge,
    ])
