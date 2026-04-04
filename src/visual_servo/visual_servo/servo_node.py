# visual_servo/visual_servo/servo_node.py
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Vector3
import numpy as np
import tf_transformations as tf
import math

POS_ERROR_THRESHOLD = 0.003   # 3mm
ANG_ERROR_THRESHOLD = math.radians(2)  # 2 degrees

class VisualServoNode(Node):
    """Visual servoing for closed-loop correction."""

    def __init__(self):
        super().__init__('visual_servo_node')
        self.create_subscription(PoseStamped, '/visual/pose', self.on_visual_pose, 10)
        self.create_subscription(PoseStamped, '/motion/current_pose', self.on_current_pose, 10)
        self.error_pub = self.create_publisher(Vector3, '/servo/error', 10)
        self.command_pub = self.create_publisher(PoseStamped, '/servo/command', 10)
        self.visual_pose = None
        self.current_pose = None
        self.target_pose = None
        self.get_logger().info('VisualServoNode initialized')

    def on_visual_pose(self, msg: PoseStamped):
        self.visual_pose = msg

    def on_current_pose(self, msg: PoseStamped):
        self.current_pose = msg
        if self.visual_pose and self.current_pose:
            error = self.compute_error()
            if error:
                self.error_pub.publish(error)
                if self.should_replan(error):
                    self.publish_corrected_target(error)

    def compute_error(self) -> Vector3:
        if self.current_pose is None or self.visual_pose is None:
            return None
        dx = self.visual_pose.pose.position.x - self.current_pose.pose.position.x
        dy = self.visual_pose.pose.position.y - self.current_pose.pose.position.y
        dz = self.visual_pose.pose.position.z - self.current_pose.pose.position.z
        q_curr = [self.current_pose.pose.orientation.x, self.current_pose.pose.orientation.y,
                  self.current_pose.pose.orientation.z, self.current_pose.pose.orientation.w]
        q_vis = [self.visual_pose.pose.orientation.x, self.visual_pose.pose.orientation.y,
                 self.visual_pose.pose.orientation.z, self.visual_pose.pose.orientation.w]
        euler_curr = tf.euler_from_quaternion(q_curr)
        euler_vis = tf.euler_from_quaternion(q_vis)
        dtheta = euler_vis[2] - euler_curr[2]
        error = Vector3()
        error.x = dx; error.y = dy; error.z = dtheta
        return error

    def should_replan(self, error: Vector3) -> bool:
        if error is None: return False
        pos_error = math.sqrt(error.x**2 + error.y**2)
        ang_error = abs(error.z)
        return pos_error > POS_ERROR_THRESHOLD or ang_error > ANG_ERROR_THRESHOLD

    def publish_corrected_target(self, error: Vector3):
        if self.target_pose is None: return
        corrected = PoseStamped()
        corrected.header.stamp = self.get_clock().now().to_msg()
        corrected.header.frame_id = 'base_link'
        corrected.pose = self.target_pose.pose
        corrected.pose.position.x += error.x
        corrected.pose.position.y += error.y
        corrected.pose.position.z += error.z
        self.command_pub.publish(corrected)

def main(args=None):
    rclpy.init(args=args)
    node = VisualServoNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
