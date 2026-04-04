# Progress - 视觉闭环路径控制

## 2026-04-02

### 完成的工作
1. 加载 ROS skills：ros2-skill, ros-robotics-skill, ros2-control
2. 读取 jaka_ros2 文档和源码
3. 分析现有架构：
   - moveit_server.cpp：直接连接真实机器人，绕过 ros2_control
   - ros2_controllers.yaml：配置存在但未被用于仿真
   - jaka_zu7.ros2_control.xacro：支持 Gazebo (IgnitionSystem) 和 RViz (GenericSystem)

### 关键发现
- **问题**：moveit_server.cpp 使用 Jaka SDK 直接控制，无法用于 Gazebo 仿真
- **解决**：需要创建仿真专用的轨迹执行方案，使用 ros2_control 标准接口

### 创建的文件
- `findings.md` — 架构分析文档
- `task_plan.md` — 阶段规划
- `progress.md` — 本进度文件

### 下一步
阶段 1：创建适配 ros2_control 的仿真环境
- 选项 A：修改 demo_gazebo.launch.py 使用 ros2_control
- 选项 B：创建新的仿真 launch 入口
- 验证 JointTrajectoryController 能控制 Gazebo 中的机器人

### 关键发现（更新）
- **Gazebo 仿真成功**：`gazebo.launch.py` 启动后，Gazebo 内部的 gz_ros2_control 插件成功加载了：
  - hardware 'jaka_zu7_hardware'
  - controller_manager（Gazebo 内部）
  - joint_state_broadcaster 和 jaka_zu7_controller
  - `/joint_states` 话题正常发布

- **ros2_control_node 崩溃**：不影响仿真，因为 Gazebo 内部已有 controller_manager
  - 原因：xacro 中 `<hardware><plugin>gz_ros2_control/GazeboSimSystem</plugin></hardware>` 让 ros2_control_node 尝试加载硬件接口
  - 但这个接口已经由 Gazebo 内部提供了，导致重复加载

- **可用话题验证**：
  - `/jaka_zu7_controller/joint_trajectory` ✅
  - `/joint_states` ✅
  - `/dynamic_joint_states` ✅

### 修改的文件
- `src/jaka_zu7_moveit_config/config/jaka_zu7.ros2_control.xacro` — 将 `ign_ros2_control/IgnitionSystem` 改为 `gz_ros2_control/GazeboSimSystem`

### 阶段 1 验证成功 ✅
- 手动测试完成：RViz 中拖动末端标记 → Plan → Execute，Gazebo 中机器人成功跟随
- 架构链路验证：
  ```
  RViz/MoveIt → /jaka_zu7_controller/follow_joint_trajectory
              → JointTrajectoryController
              → gz_ros2_control
              → Gazebo 仿真器 ✅
  ```

### 阶段 2 完成项

**创建的文件：**
- `src/jaka_vision/package.xml` — 包描述（含 apriltag_msgs, tf2_ros 等依赖）
- `src/jaka_vision/setup.py` — 构建配置（含 2 个节点入口）
- `src/jaka_vision/jaka_vision/apriltag_detector_node.py` — 真实 Apriltag 检测节点
- `src/jaka_vision/jaka_vision/simulated_detector_node.py` — **模拟检测节点（用于无相机测试）**
- `src/jaka_vision/launch/apriltag_detector.launch.py` — 启动文件

**安装的依赖：**
- `ros-humble-apriltag-ros` ✅
- `ros-humble-apriltag-msgs` ✅
- `ros-humble-apriltag-detector` ✅

**可用节点：**
| 节点 | 用途 |
|------|------|
| `apriltag_detector_node` | 真实 Apriltag 检测，transform 到 base_link |
| `simulated_detector_node` | 模拟检测（发布固定位置，用于测试） |

### 下一步
阶段 3：手眼标定（Eye-in-Hand）
- 创建 `jaka_camera_gazebo.xacro` — 相机 URDF 定义
- 创建 `jaka_zu7_with_camera.urdf.xacro` — 带相机的机器人模型
- 创建 `gazebo_camera_bridge.launch.py` — Gazebo + ros_gz_image 桥接
- **待测试**：Gazebo 中相机是否能正常发布图像话题

### Gazebo 相机集成遇到的 问题

**问题**：Gazebo 中相机传感器无法发布图像话题

**根本原因（已确认）**：

**URDF vs SDF 架构差异**：
| 特性 | URDF | SDF |
|------|------|-----|
| 设计定位 | 机器人运动学和可视化描述 | Gazebo 原生仿真格式 |
| 在 Gazebo 中的处理 | 转换时丢失传感器语义 | 直接加载，完整保留 |
| 插件机制 | 仅支持基础插件 | 支持所有系统/传感器插件 |

**核心问题**：
1. `libgazebo_ros_camera.so` 是 Gazebo Classic 插件，与 Fortress 不兼容
2. `ros_gz_sim create` 动态 spawn 时，sensors-system 已在世界加载时初始化，不会识别新 spawn 模型的传感器
3. URDF 中的 `<gazebo reference="...">` sensor 定义在转换时丢失

**已验证**：
- `camera_sensor.sdf` 直接在 world 中定义 ✅ 工作正常
- URDF spawn 的相机 sensor ❌ 不工作

**推荐解决方案**：
1. 将 URDF 转为 SDF（完整格式）
2. 在 world 文件中使用 `<include>` 预加载机器人模型
3. **使用固定相机观察工作空间** ✅ 已实现

### Gazebo 相机集成方案（更新）

**方案**：使用固定外部相机观察机器人工作空间

**架构**：
```
Gazebo SDF World
├── ground_plane
├── table (工作台)
├── apriltag_target (标定板)
├── workspace_camera (固定相机) ← 发布 /camera/image
│   └── camera_sensor (sensors-system 初始化时加载)
└── jaka_zu7 (URDF spawn via ros_gz_sim create)
    └── Link_6 (末端执行器)
```

**创建的文件**：
- `worlds/jaka_zu7_with_camera.world` — 完整 SDF 世界（含相机、桌子、标定板）
- `models/eye_in_hand_camera.sdf` — 相机 SDF 模型

**启动顺序**：
1. `demo_gazebo_with_camera.launch.py` — 启动 Gazebo + MoveIt
2. `gazebo_camera_bridge.launch.py` — 桥接相机图像到 ROS

**验证状态**：
- `simulated_detector_node` ✅ 工作正常，10Hz 发布频率
- `/jaka_vision/detections` 话题 ✅ 可用
- Gazebo + MoveIt ✅ 正常工作
- SDF world + image_bridge ✅ 相机可发布到 ROS
- **新方案**：`jaka_zu7_with_camera.world` + 外部相机 ✅

### 待解决问题：Eye-in-Hand 相机配置到末端

**问题**：URDF spawn 的相机传感器无法在 Gazebo Fortress 工作
**原因**：`ros_gz_sim create` 在 sensors-system 初始化后 spawn，传感器无法注册
**状态**：待解决

**临时方案**：使用外部固定相机观察工作空间（已实现）

**下一步尝试**：
- 使用 Gazebo service 在运行时将相机模型附加到机器人
- 或将完整 URDF 转为 SDF 后在 world 中预加载

### 测试步骤

**启动 Gazebo + MoveIt（含相机世界）**：
```bash
ros2 launch jaka_zu7_moveit_config demo_gazebo_with_camera.launch.py
```

**启动相机桥接（另一个终端）**：
```bash
ros2 launch jaka_vision gazebo_camera_bridge.launch.py
```

**验证相机图像**：
```bash
# 检查 ROS 话题
ros2 topic list | grep camera

# 查看图像（需要 rqt 或 rviz2）
ros2 run rqt_image_view rqt_image_view /camera/image
```

**或使用模拟检测节点测试视觉伺服**：
```bash
ros2 launch jaka_vision apriltag_detector.launch.py
```

### 遇到的错误/问题
| 问题 | 状态 |
|------|------|
| moveit_server.cpp 不兼容 Gazebo | 不影响仿真（已确认） |
| ros2_control_node 无法加载 GazeboSimSystem | 不影响仿真（已确认） |
| 需要仿真专用轨迹执行方案 | 不需要（JointTrajectoryController 已处理） |
| apriltag_ros 需真实相机 | 用 simulated_detector_node 绕过 |
| Gazebo URDF 相机 sensor 不工作 | 用 SDF 直接定义或 simulated_detector_node 绕过 |
