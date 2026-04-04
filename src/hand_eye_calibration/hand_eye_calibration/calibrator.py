# hand_eye_calibration/hand_eye_calibration/calibrator.py
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped, PoseStamped
import numpy as np

class HandEyeCalibrator(Node):
    """Eye-in-Hand hand-eye calibration using Apriltag."""

    def __init__(self):
        super().__init__('hand_eye_calibrator')
        self.tag_size = self.declare_parameter('tag_size', 0.166).value

        self.create_subscription(PoseStamped, '/tag_detections', self.on_tag_pose, 10)
        self.create_subscription(PoseStamped, '/tool_pose', self.on_flange_pose, 10)

        self.tag_poses = []
        self.flange_poses = []
        self.calibrated = False

        self.get_logger().info('HandEyeCalibrator initialized, waiting for pose pairs...')

    def on_tag_pose(self, msg: PoseStamped):
        if not self.calibrated and len(self.tag_poses) < 30:
            self.tag_poses.append(msg)

    def on_flange_pose(self, msg: PoseStamped):
        if not self.calibrated and len(self.flange_poses) < 30:
            self.flange_poses.append(msg)
        if not self.calibrated and len(self.tag_poses) >= 15 and len(self.flange_poses) >= 15:
            self.calibrate()

    def calibrate(self):
        import cv2
        try:
            R_cam2tag, t_cam2tag = [], []
            R_base2flange, t_base2flange = [], []

            for i in range(min(len(self.tag_poses), len(self.flange_poses))):
                p_tag = self.tag_poses[i].pose
                p_flange = self.flange_poses[i].pose
                q1 = [p_tag.orientation.x, p_tag.orientation.y, p_tag.orientation.z, p_tag.orientation.w]
                q2 = [p_flange.orientation.x, p_flange.orientation.y, p_flange.orientation.z, p_flange.orientation.w]
                R_tag = self._quaternion_matrix(q1)[:3, :3]
                R_flange = self._quaternion_matrix(q2)[:3, :3]
                R_cam2tag.append(R_tag)
                t_cam2tag.append([p_tag.position.x, p_tag.position.y, p_tag.position.z])
                R_base2flange.append(R_flange)
                t_base2flange.append([p_flange.position.x, p_flange.position.y, p_flange.position.z])

            R_cam2flange, t_cam2flange = cv2.calibrateHandEye(
                R_base2flange, t_base2flange, R_cam2tag, t_cam2tag,
                cv2.CALIB_HAND_EYE_DANIILIDIS
            )
            self._publish_transform(R_cam2flange, t_cam2flange)
            self.calibrated = True
            self.get_logger().info(f'Calibration done! t={t_cam2flange.flatten()}')
        except Exception as e:
            self.get_logger().error(f'Calibration failed: {e}')

    def _quaternion_matrix(self, q):
        x, y, z, w = q
        return np.array([
            [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w), 0],
            [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w), 0],
            [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y), 0],
            [0, 0, 0, 1]
        ])

    def _publish_transform(self, R, t):
        from geometry_msgs.msg import TransformStamped
        import tf_transformations as tf
        t_msg = TransformStamped()
        t_msg.header.stamp = self.get_clock().now().to_msg()
        t_msg.header.frame_id = 'tool0'
        t_msg.child_frame_id = 'camera_link'
        t_msg.transform.translation.x = t[0][0]
        t_msg.transform.translation.y = t[0][1]
        t_msg.transform.translation.z = t[0][2]
        M = np.vstack([np.hstack([R, t.T]), [0,0,0,1]])
        q = tf.quaternion_from_matrix(M)
        t_msg.transform.rotation.x, t_msg.transform.rotation.y = q[0], q[1]
        t_msg.transform.rotation.z, t_msg.transform.rotation.w = q[2], q[3]
        # Note: static TF broadcaster would be set up in __init__ in full impl

def main(args=None):
    rclpy.init(args=args)
    node = HandEyeCalibrator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
