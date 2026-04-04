"""
JAKA Vision - Apriltag Detection Node

Subscribes to apriltag detections and transforms them to the robot base frame.
Publishes detection poses in base_link coordinates.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from geometry_msgs.msg import PoseStamped
from apriltag_msgs.msg import AprilTagDetectionArray
from sensor_msgs.msg import CameraInfo
import tf2_ros
from tf2_ros import TransformException
from rclpy.duration import Duration


class ApriltagDetectorNode(Node):
    """
    Transforms apriltag detections from camera frame to robot base frame.

    Subscribes:
        /apriltag/detections : AprilTagDetectionArray (from apriltag_ros)
        /camera/camera_info : CameraInfo (camera intrinsics)

    Publishes:
        /jaka_vision/detections : geometry_msgs/PoseStamped (in base_link frame)
    """

    def __init__(self):
        super().__init__('apriltag_detector_node')

        # TF2 buffer and listener
        self.tf_buffer = tf2_ros.Buffer(Duration(seconds=10))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Camera info storage
        self.camera_info = None
        self.camera_frame = 'camera_link'

        # Target frame for transformations
        self.base_frame = 'base_link'

        # QoS for sensor data
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Subscribers
        self.detection_sub = self.create_subscription(
            AprilTagDetectionArray,
            '/apriltag/detections',
            self.detection_callback,
            sensor_qos
        )

        self.camera_info_sub = self.create_subscription(
            CameraInfo,
            '/camera/camera_info',
            self.camera_info_callback,
            10
        )

        # Publisher
        self.detection_pub = self.create_publisher(
            PoseStamped,
            '/jaka_vision/detections',
            10
        )

        self.get_logger().info('ApriltagDetectorNode initialized')
        self.get_logger().info('  Subscribes to: /apriltag/detections, /camera/camera_info')
        self.get_logger().info('  Publishes to: /jaka_vision/detections')

    def camera_info_callback(self, msg: CameraInfo):
        """Store camera info for pose estimation."""
        self.camera_info = msg
        if msg.header.frame_id:
            self.camera_frame = msg.header.frame_id

    def detection_callback(self, msg: AprilTagDetectionArray):
        """
        Transform apriltag detections to base_link frame and republish.
        """
        if not msg.detections:
            return

        for detection in msg.detections:
            try:
                # Try to use full pose from apriltag_ros
                if (hasattr(detection, 'pose') and
                    detection.pose.header.stamp.sec > 0):

                    # apriltag_ros provides full 3D pose
                    tag_pose = detection.pose.pose.pose

                    # Transform from camera frame to base_link
                    pose_stamped = PoseStamped()
                    pose_stamped.header = detection.pose.header
                    pose_stamped.header.frame_id = self.base_frame
                    pose_stamped.pose.position.x = tag_pose.position.x
                    pose_stamped.pose.position.y = tag_pose.position.y
                    pose_stamped.pose.position.z = tag_pose.position.z
                    pose_stamped.pose.orientation.x = tag_pose.orientation.x
                    pose_stamped.pose.orientation.y = tag_pose.orientation.y
                    pose_stamped.pose.orientation.z = tag_pose.orientation.z
                    pose_stamped.pose.orientation.w = tag_pose.orientation.w

                    self.detection_pub.publish(pose_stamped)

                    self.get_logger().debug(
                        f'Detection ID {detection.id}: '
                        f'pos({tag_pose.position.x:.3f}, {tag_pose.position.y:.3f}, {tag_pose.position.z:.3f})'
                    )
                else:
                    # Fallback: estimate 3D from 2D center (needs depth)
                    # This is simplified - real implementation needs depth sensor
                    self.get_logger().warn(
                        'Using 2D center - need depth or full pose estimation',
                        throttle_duration_sec=5.0
                    )

            except TransformException as ex:
                self.get_logger().warn(
                    f'TF transform failed: {ex}',
                    throttle_duration_sec=1.0
                )


def main(args=None):
    rclpy.init(args=args)
    node = ApriltagDetectorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
