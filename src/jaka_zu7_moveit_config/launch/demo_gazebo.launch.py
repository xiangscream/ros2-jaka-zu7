from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_demo_gazebo_launch


def generate_launch_description():
    # Build moveit config with xacro args for gazebo
    moveit_config = (
        MoveItConfigsBuilder("jaka_zu7", package_name="jaka_zu7_moveit_config")
        .robot_description(mappings={"use_gazebo": "true"})
        .to_moveit_configs()
    )
    return generate_demo_gazebo_launch(moveit_config)
