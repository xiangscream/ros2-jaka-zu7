# swap_fsm/swap_fsm/swap_fsm_node.py
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse
import asyncio

STATE_NAMES = [
    'S0_HOME', 'S1_SIDE_APPROACH', 'S2_FINE_ALIGN', 'S3_GRIP',
    'S4_EXTRACT', 'S5_SAFE_RETREAT', 'S6_PLACE_OLD', 'S7_RESET',
    'S8_GRIP_NEW', 'S9_MOVE_TO_DOCK', 'S10_INSERT', 'S11_RETURN_HOME'
]

STATE_PLANNING_GROUPS = [
    'home', 'side_approach', 'fine_align', 'grip',
    'extract', 'safe_retreat', 'place_old', 'reset',
    'grip_new', 'move_to_dock', 'insert', 'return_home'
]

class SwapFSMNode(Node):
    def __init__(self):
        super().__init__('swap_fsm_node')
        self.current_state = 0
        self.is_executing = False
        self._goal_handle = None
        self._action_server = ActionServer(
            self,
            'Swap',
            '/swap/action',
            execute_callback=self._on_execute,
            cancel_callback=self._on_cancel
        )
        self.get_logger().info('SwapFSMNode initialized, waiting for goals...')

    async def _on_execute(self, goal_handle):
        seq = goal_handle.request.sequence_id
        self.get_logger().info(f'Received goal: sequence_id={seq}')
        if seq > 11:
            goal_handle.abort()
            result = SwapActionResult()
            result.success = False
            result.message = 'Invalid sequence_id (must be 0-11)'
            return result
        self.is_executing = True
        self.current_state = seq
        feedback = SwapActionFeedback()
        total_steps = 11 - seq
        try:
            for step in range(seq, 12):
                self.current_state = step
                feedback.current_state = step
                feedback.progress = float(step - seq) / total_steps if total_steps > 0 else 1.0
                goal_handle.publish_feedback(feedback)
                success = await self._execute_step(step)
                if not success:
                    goal_handle.abort()
                    result = SwapActionResult()
                    result.success = False
                    result.message = f'Step {step} failed'
                    self.is_executing = False
                    return result
            goal_handle.succeed()
            result = SwapActionResult()
            result.success = True
            result.message = 'Swap sequence completed'
            feedback.progress = 1.0
            goal_handle.publish_feedback(feedback)
            self.is_executing = False
            return result
        except Exception as e:
            goal_handle.abort()
            result = SwapActionResult()
            result.success = False
            result.message = str(e)
            self.is_executing = False
            return result

    async def _execute_step(self, step: int) -> bool:
        group_name = STATE_PLANNING_GROUPS[step]
        self.get_logger().info(f'Executing step {step} ({STATE_NAMES[step]}), group={group_name}')
        await asyncio.sleep(0.1)
        return True

    def _on_cancel(self, goal_handle):
        self.get_logger().info('Goal cancelled')
        return CancelResponse.ACCEPT

def main(args=None):
    rclpy.init(args=args)
    node = SwapFSMNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
