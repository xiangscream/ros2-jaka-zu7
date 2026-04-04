"""
Simulated Apriltag Detector for Testing

Publishes fake apriltag detections at a fixed position for testing
the visual servo pipeline without needing a real camera or apriltag.

Used for Phase 2 development before integrating real camera.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from apriltag_msgs.msg import AprilTagDetectionArray, AprilTagDetection
from std_msgs.msg import Header
import math


class SimulatedDetectorNode(Node):
    """
    Simulates apriltag detections for testing.

    Publishes to:
        /apriltag/detections : AprilTagDetectionArray (simulated)
        /jaka_vision/detections : geometry_msgs/PoseStamped (in base_link frame)
    """

    def __init__(self):
        super().__init__('simulated_detector_node')

        # Simulation parameters
        self.declare_parameter('target_x', 0.3)
        self.declare_parameter('target_y', 0.0)
        self.declare_parameter('target_z', 0.2)
        self.declare_parameter('tag_id', 9)
        self.declare_parameter('publish_rate', 10.0)  # Hz

        self.target_x = self.get_parameter('target_x').value
        self.target_y = self.get_parameter('target_y').value
        self.target_z = self.get_parameter('target_z').value
        self.tag_id = self.get_parameter('tag_id').value
        self.publish_rate = self.get_parameter('publish_rate').value

        # Publishers
        self.apriltag_pub = self.create_publisher(
            AprilTagDetectionArray,
            '/apriltag/detections',
            10
        )

        self.detection_pub = self.create_publisher(
            PoseStamped,
            '/jaka_vision/detections',
            10
        )

        # Timer for publishing
        timer_period = 1.0 / self.publish_rate
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.get_logger().info(f'SimulatedDetectorNode initialized')
        self.get_logger().info(f'  Target position: ({self.target_x}, {self.target_y}, {self.target_z})')
        self.get_logger().info(f'  Tag ID: {self.tag_id}')
        self.get_logger().info(f'  Publish rate: {self.publish_rate} Hz')

    def timer_callback(self):
        """Publish simulated detection."""
        now = self.get_clock().now().to_msg()

        # Create AprilTagDetectionArray message
        detection_array = AprilTagDetectionArray()
        detection_array.header = Header()
        detection_array.header.stamp = now
        detection_array.header.frame_id = 'base_link'

        # Create single detection
        detection = AprilTagDetection()
        detection.family = '36h11'
        detection.id = self.tag_id
        detection.hamming = 0
        detection.goodness = 1.0
        detection.decision_margin = 1.0

        # Center point in image (simplified)
        from apriltag_msgs.msg import Point
        detection.centre = Point()
        detection.centre.x = 320.0
        detection.centre.y = 240.0

        # Corners (simplified square)
        detection.corners = [
            Point(x=280.0, y=200.0),
            Point(x=360.0, y=200.0),
            Point(x=360.0, y=280.0),
            Point(x=280.0, y=280.0),
        ]

        detection_array.detections.append(detection)

        # Publish apriltag detection
        self.apriltag_pub.publish(detection_array)

        # Also publish directly in base_link (simulating tf2 transform)
        pose = PoseStamped()
        pose.header = Header()
        pose.header.stamp = now
        pose.header.frame_id = 'base_link'
        pose.pose.position.x = self.target_x
        pose.pose.position.y = self.target_y
        pose.pose.position.z = self.target_z
        pose.pose.orientation.w = 1.0

        self.detection_pub.publish(pose)


def main(args=None):
    rclpy.init(args=args)
    node = SimulatedDetectorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
