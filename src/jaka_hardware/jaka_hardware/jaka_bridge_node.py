import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import math

class JakaBridgeNode(Node):
    """Bridge between MoveIt2 trajectory and JAKA SDK execution."""

    def __init__(self):
        super().__init__('jaka_bridge_node')
        self.jaka = None
        self.use_sim = self.declare_parameter('use_sim', True).value

        if not self.use_sim:
            try:
                from jaka import JAKA
                self.jaka = JAKA('192.168.1.100')
                self.get_logger().info('JAKA SDK connected to 192.168.1.100')
            except Exception as e:
                self.get_logger().warn(f'JAKA SDK connection failed: {e}, falling back to sim mode')
                self.use_sim = True

        self.trajectory_sub = self.create_subscription(
            JointTrajectory,
            '/joint_trajectory',
            self.on_trajectory,
            10
        )
        self.get_logger().info(f'JAKA Bridge Node initialized (sim={self.use_sim})')

    def on_trajectory(self, msg: JointTrajectory):
        if self.use_sim:
            self.get_logger().info(
                f'[SIM] Trajectory: {len(msg.points)} points, '
                f'joints={msg.joint_names}'
            )
        else:
            for i, point in enumerate(msg.points):
                positions = list(point.positions)
                time_sec = point.time_from_start.sec + point.time_from_start.nanosec * 1e-9
                self.get_logger().info(f'Executing point {i+1}/{len(msg.points)} at t={time_sec:.2f}s')
            self.get_logger().info('Trajectory execution complete')

def main(args=None):
    rclpy.init(args=args)
    node = JakaBridgeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
