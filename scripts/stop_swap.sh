#!/bin/bash
# jaka_ws/scripts/stop_swap.sh
# Stop all swap-related nodes

pkill -f jaka_bridge_node 2>/dev/null && echo "jaka_bridge_node stopped"
pkill -f swap_fsm_node 2>/dev/null && echo "swap_fsm_node stopped"
pkill -f visual_servo 2>/dev/null && echo "visual_servo stopped"
pkill -f hand_eye_calibration 2>/dev/null && echo "hand_eye_calibrator stopped"
pkill -f apriltag_node 2>/dev/null && echo "apriltag_node stopped"
pkill -f move_group 2>/dev/null && echo "move_group stopped"
pkill -f gazebo 2>/dev/null && echo "gazebo stopped"

echo "All nodes stopped"
