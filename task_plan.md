# Task Plan - 视觉闭环路径控制系统

## 目标
在仿真空间（Gazebo + ros2_control）内实现视觉闭环路径控制，相机在末端执行器（eye-in-hand），用于识别抓取物体。

## 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                         感知层                                    │
│  [相机节点] ──→ /camera/image_raw ──→ [视觉检测节点] ──→ /detections│
│       │                                                               │
│       └──→ /camera_info ──→ [手眼标定] ──→ tf: camera → tool0       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         控制层（ros2_control）                       │
│  [视觉伺服节点] ──→ /arm_controller/trajectory (修正轨迹)              │
│         ↓                                                            │
│  joint_trajectory_controller (position接口)                          │
│         ↓ read()/write()                                            │
│  [IgnitionSystem] ← Gazebo 仿真器                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    /joint_states (状态反馈)
```

## 阶段

### 阶段 0：环境验证 ✅
- [x] ROS2 Humble + Gazebo Fortress 可用
- [x] jaka_ros2 工作空间可构建
- [x] ros2_control 配置已存在

### 阶段 1：Gazebo 仿真验证 ✅
- [x] 修改 ros2_control xacro：ign_ros2_control → gz_ros2_control/GazeboSimSystem
- [x] 验证 Gazebo + MoveIt 集成启动正常
- [x] 验证 /joint_states 反馈正常
- [x] **RViz 手动测试成功** — MoveIt 可控制 Gazebo 中的机器人

### 阶段 1 结论
- `demo_gazebo.launch.py` 已可用
- MoveIt → JointTrajectoryController → Gazebo 链路验证通过
- 无需新建仿真版 moveit_server，JointTrajectoryController 已处理

### 阶段 2：视觉检测节点
- [x] 创建视觉检测包（jaka_vision）
- [x] 集成 Apriltag/靶标检测（apriltag_ros）
- [x] 发布 /detections 话题
- [x] **simulated_detector_node 用于无相机测试**
- [ ] 添加 Gazebo 相机模型到末端执行器（待完成）

### 阶段 3：手眼标定
- [ ] 现有手眼标定方案调研
- [ ] 实现 eye-in-hand 标定
- [ ] 建立 tf 树：base → tool0 → camera

### 阶段 4：视觉伺服节点
- [ ] 创建视觉伺服包（jaka_visual_servo）
- [ ] 订阅 /detections 和 /joint_states
- [ ] 实现图像空间 → 关节空间误差映射
- [ ] 发送修正轨迹到 joint_trajectory_controller

### 阶段 5：闭环集成测试
- [ ] 静态目标抓取测试
- [ ] 动态目标跟踪测试
- [ ] 误差收敛分析

## 当前任务
**阶段 2：视觉检测节点**

## 关键决策
1. **不修改原有 moveit_server.cpp** — 保留真实机器人版本
2. **新建仿真专用版本** — `moveit_server_sim.cpp` 或新的 launch 配置
3. **使用 JointTrajectoryController** — 标准 ros2_control 控制器
4. **视觉伺服作为独立节点** — 不修改 ros2_control 内部
