# ros2-jaka-zu7

JAKA ZU7 机械臂 ROS2 教学项目 - 毕业设计

## 项目简介

基于 ROS2 Humble 的 JAKA ZU7 机械臂视觉闭环路径规划系统，包含：

- JAKA 官方 ROS2 驱动 (`jaka_driver`)
- 机器人模型和 URDF/XACRO (`jaka_description`)
- MoveIt2 运动规划配置
- 视觉检测系统 - Apriltag 目标识别
- 手眼标定 - Eye-in-Hand 标定
- 视觉闭环伺服 - 图像空间误差修正
- 换电池 12 步状态机

## 支持的型号

- JAKA ZU3, ZU5, ZU7, ZU12, ZU18, ZU20, ZU30
- JAKA A5, A12, C5, C7, C12
- JAKA PRO5, PRO7, PRO12, PRO16, PRO18
- JAKA S5, S7, S12

## 环境要求

- Ubuntu 22.04 (Jammy)
- ROS2 Humble
- Gazebo Fortress
- Python 3.8+

## 快速开始

### 1. 编译

```bash
cd ~/ros2-jaka-zu7
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

### 2. 运行仿真

**Gazebo 仿真模式：**

```bash
ros2 launch jaka_zu7_moveit_config demo_gazebo.launch.py
```

**带相机的仿真：**

```bash
ros2 launch jaka_zu7_moveit_config demo_gazebo_with_camera.launch.py
```

**视觉检测模拟（无需相机）：**

```bash
ros2 launch jaka_vision simulated_detector.launch.py
```

## 目录结构

```
ros2-jaka-zu7/
├── src/
│   ├── jaka_driver/              # JAKA SDK 驱动
│   ├── jaka_description/         # 机器人模型
│   ├── jaka_msgs/                # 消息定义
│   ├── jaka_planner/             # 运动规划
│   ├── jaka_zu7_moveit_config/  # MoveIt 配置
│   ├── jaka_vision/             # 视觉检测
│   ├── jaka_hardware/            # 毕设：硬件桥接
│   ├── apriltag_ros/            # 毕设：Apriltag识别
│   ├── hand_eye_calibration/    # 毕设：手眼标定
│   ├── visual_servo/            # 毕设：视觉伺服
│   └── swap_fsm/                # 毕设：状态机
├── launch/                       # 顶层 launch
├── scripts/                      # 工具脚本
├── worlds/                       # Gazebo world 文件
└── docs/                        # 文档
```

## 文档

- [JAKA ROS2 文档](jaka_ros2_documentation-中文版.md) - 官方文档
- [任务规划](task_plan.md) - 开发进度
- [发现与问题](findings.md) - 技术调研

## License

MIT
