# Findings - 视觉伺服架构分析

## 1. 现有架构分析

### 1.1 jaka_planner/moveit_server.cpp

**用途**：MoveIt 2 的轨迹执行器（action server）

**问题**：专为**真实机器人**设计，完全绕过了 ros2_control

```
MoveIt2 → moveit_server (action server) → Jaka SDK → 真实机器人
                    ↓
            robot.servo_j() @ 125Hz
```

**关键代码问题**：
- 直接调用 `robot.login_in()` 连接真实机器人
- 使用 `robot.servo_j()` 直接发送关节角度
- 不经过 ros2_control 的 hardware_interface
- Gazebo 仿真无法使用此节点

### 1.2 ros2_controllers.yaml

```yaml
controller_manager:
  ros__parameters:
    update_rate: 1000  # Hz

jaka_zu7_controller:
  type: joint_trajectory_controller/JointTrajectoryController
  joints: [joint_1~joint_6]
  command_interfaces: [position]
  state_interfaces: [position, velocity]
```

**现状**：
- 配置存在但**未被使用**
- demo_gazebo.launch.py 使用 MoveItConfigsBuilder，会加载此配置
- 但 moveit_server.launch.py 不会启动 ros2_control

### 1.3 ros2_control.xacro

**RViz 仿真** (`use_rviz_sim=true`):
```xml
<plugin>mock_components/GenericSystem</plugin>
```

**Gazebo 仿真** (`use_gazebo=true`):
```xml
<plugin>ign_ros2_control/IgnitionSystem</plugin>
```

## 2. 核心问题

### 问题 1：双轨架构不兼容
| 模式 | moveit_server | ros2_control |
|------|---------------|---------------|
| 真实机器人 | ✅ 使用 | ❌ 未配置 |
| Gazebo仿真 | ❌ 不兼容 | ✅ 已配置 |
| RViz仿真 | ✅ 可用 | ✅ 已配置 |

### 问题 2：视觉伺服需要闭环控制

当前开环轨迹执行：
```
目标位姿 → MoveIt规划 → 轨迹点序列 → moveit_server执行 → 完成
                                                        ↑ 没有反馈修正
```

视觉伺服需要：
```
目标位姿 → MoveIt规划 → 轨迹点序列
                            ↓
                    [视觉伺服节点]
                            ↓
            检测误差 → 计算修正量 → 注入下一个轨迹点
                            ↓
                    JointTrajectoryController → 执行
```

## 3. 仿真架构设计

### 3.1 Gazebo 仿真下的 ros2_control 链路

```
demo_gazebo.launch.py
    ├── MoveIt2 move_group
    ├── robot_state_publisher
    ├── ros2_control_node
    │       └── controller_manager
    │               └── jaka_zu7_controller (JointTrajectoryController)
    │                       ↓
    │               ign_ros2_control/IgnitionSystem
    │                       ↓
    │               Gazebo 仿真器
    └── joint_state_broadcaster
```

### 3.2 视觉伺服节点需要的位置

```
[视觉检测节点] → /detections (物体位置)
        ↓
[视觉伺服节点] → /arm_controller/trajectory (修正后的轨迹命令)
        ↓
[JointTrajectoryController] → /joint_commands
        ↓
[IgnitionSystem] → Gazebo
```

## 4. 关键文件路径

| 文件 | 作用 |
|------|------|
| `src/jaka_planner/src/moveit_server.cpp` | 真实机器人轨迹执行（需重构/新建） |
| `src/jaka_zu7_moveit_config/config/ros2_controllers.yaml` | ros2_control 配置 |
| `src/jaka_zu7_moveit_config/config/jaka_zu7.ros2_control.xacro` | 硬件接口 xacro |
| `src/jaka_zu7_moveit_config/launch/demo_gazebo.launch.py` | Gazebo 仿真入口 |
| `src/jaka_description/urdf/jaka_zu7.urdf` | 机器人 URDF 模型 |
