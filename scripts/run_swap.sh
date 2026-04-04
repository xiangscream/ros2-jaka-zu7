#!/bin/bash
# jaka_ws/scripts/run_swap.sh
# One-touch run battery swap (auto-detect sim/real mode)
# Usage: ./run_swap.sh [sim|real]

MODE=${1:-sim}

if [ "$MODE" != "sim" ] && [ "$MODE" != "real" ]; then
    echo "Usage: $0 [sim|real]"
    exit 1
fi

source ~/jaka_ws/install/setup.bash

if [ "$MODE" = "sim" ]; then
    echo "[SIM] Launching Gazebo simulation..."
    ros2 launch ~/jaka_ws/launch/sim_bringup.launch.py
else
    echo "[REAL] Launching real machine bringup..."
    ros2 launch ~/jaka_ws/launch/real_bringup.launch.py
fi
