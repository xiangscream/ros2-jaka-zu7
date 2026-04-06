# JAKA ZU7 Eye-in-Hand Gazebo 仿真设计

## 1. 背景与目标

**问题**：
1. 当前项目 `ros2-jaka-zu7` 存在文件结构混乱、重复文件多的问题
2. Gazebo 中 eye-in-hand 相机无法正常发布图像话题
3. 需要同时完成毕设视觉伺服功能和保持项目结构合理

**目标**：
- 创建一个最小可用的 eye-in-hand 相机 Gazebo 仿真环境
- 验证相机能正常发布 `/camera/image_raw` 话题
- 验证 `rqt_image_view` 能正常显示图像
- 为毕设视觉伺服提供可靠的仿真基础

## 2. 参考项目

**Universal_Robots_ROS2_Gazebo_Simulation** (GitHub: deboradcm/Universal_Robots_ROS2_Gazebo_Simulation)

该项目的结构特点：
- 单一功能包 `ur_simulation_gazebo`
- URDF/world/launch/config 都在一个包内
- 使用 inline SDF world 直接加载机器人（含传感器）
- 不使用动态 spawn

## 3. 解决方案

### 3.1 创建新包 `jaka_gazebo_sim`

参考 UR 结构，创建独立的 Gazebo 仿真包：

```
jaka_gazebo_sim/
├── package.xml
├── setup.py
├── setup.cfg
├── jaka_gazebo_sim/
│   └── __init__.py
├── urdf/
│   ├── jaka_zu7.urdf.xacro          # 基础机器人定义
│   └── inc/
│       └── camera.urdf.xacro          # 相机 xacro 宏
├── worlds/
│   └── jaka_zu7_eye_in_hand.world    # inline SDF world
├── launch/
│   └── sim_eye_in_hand.launch.py     # 单一 launch 文件
└── config/
    └── ros2_controllers.yaml         # ros2_control 配置
```

### 3.2 相机实现方案

**核心思路**：使用 inline SDF world，机器人和相机随 Gazebo 启动一起加载，确保 sensors-system 正确初始化。

**xacro 定义**：
```xml
<!-- camera.urdf.xacro -->
<xacro:macro name="jaka_camera_gazebo" params="parent">
  <link name="camera_link">
    <sensor name="camera_sensor" type="camera">
      <topic>/camera/image_raw</topic>
      <!-- ... camera params ... -->
    </sensor>
  </link>
  <joint name="camera_joint" type="fixed">
    <parent link="${parent}"/>
    <child link="camera_link"/>
  </joint>
</xacro:macro>
```

**URDF → SDF 转换**：
使用 `gz sdf -p` 将 xacro 转换为 SDF，确保相机传感器一起转换。

### 3.3 World 文件结构

```xml
<sdf version="1.7">
  <world name="jaka_zu7_eye_in_hand">
    <!-- 核心系统 -->
    <plugin filename="gz-sim-sensors-system" .../>  <!-- 相机需要 -->
    <plugin filename="gz-sim-physics-system" .../>
    <!-- 地面 -->
    <model name="ground_plane">...</model>
    <!-- 目标物体 -->
    <model name="apriltag_target">...</model>
    <!-- 机器人（inline，不动态spawn） -->
    <model name="jaka_zu7">
      <!-- 完整机器人SDF，含Link_6上的相机传感器 -->
    </model>
  </world>
</sdf>
```

### 3.4 Launch 文件

单一 launch 文件，启动所有组件：

```python
def generate_launch_description():
    # 1. robot_state_publisher
    # 2. Gazebo with inline world
    # 3. ros2_control spawner
    # 4. joint_state_broadcaster
    # 5. camera_bridge (可选)
```

### 3.5 话题桥接

Gazebo → ROS2 图像桥接：

```bash
# 桥接命令
ros2 run ros_gz_image image_bridge /camera/image_raw
```

或使用 launch 中的 node：

```python
Node(
    package='ros_gz_image',
    executable='image_bridge',
    arguments=['/camera/image_raw'],
)
```

## 4. 验证步骤

```bash
# 1. 启动仿真
ros2 launch jaka_gazebo_sim sim_eye_in_hand.launch.py

# 2. 检查 Gazebo 话题
gz topic -l | grep camera

# 3. 检查 ROS 话题
ros2 topic list | grep camera

# 4. 查看图像
ros2 run rqt_image_view rqt_image_view /camera/image_raw
```

## 5. 清理计划

完成后删除以下重复/废弃文件：

```
# 删除根目录废弃文件
rm -rf launch/
rm -rf worlds/
rm -rf models/

# 删除 src 中的重复文件
rm -rf src/jaka_zu7_moveit_config/worlds/
rm -rf src/jaka_zu7_moveit_config/models/
rm -rf src/jaka_vision/models/
```

## 6. 后续步骤

验证通过后：
1. 将 `jaka_gazebo_sim` 的结构推广到其他包
2. 整合 `jaka_vision` 视觉检测
3. 开发视觉伺服节点

## 7. 技术要点

| 要点 | 说明 |
|------|------|
| 为什么不用动态 spawn | sensors-system 在初始化后才 spawn 的模型，相机传感器无法注册 |
| 为什么用 inline SDF | 机器人在 world 加载时已存在，sensors-system 能正确识别 |
| 相机位置 | Link_6 (末端执行器) 上方 5cm，朝下看工作空间 |
