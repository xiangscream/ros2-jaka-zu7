# ros2-jaka-zu7 仓库搭建实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 搭建完整 ROS2 工作空间，实现仿真模式可运行

**Architecture:**
- 顶层 workspace 包含 jaka_ros2 官方包 + 毕设模块
- 仿真模式：Gazebo + MoveIt + 视觉检测
- 使用 ros2_control 标准的 JointTrajectoryController

**Tech Stack:** ROS2 Humble, Gazebo Fortress, MoveIt2, ros2_control, apriltag_ros

---

## Phase 1: 创建仓库结构

### Task 1: 创建目录结构

**Files:**
- Create: `/home/xiang/ros2-jaka-zu7/`

```bash
mkdir -p /home/xiang/ros2-jaka-zu7/{src,launch,scripts,docs,models,worlds}
```

### Task 2: 复制 jaka_ros2 源码（排除 .git）

**Files:**
- Copy: `/home/xiang/jaka_ros2/src/` → `/home/xiang/ros2-jaka-zu7/src/jaka_ros2/`

```bash
rsync -a --exclude='.git' /home/xiang/jaka_ros2/src/ /home/xiang/ros2-jaka-zu7/src/jaka_ros2/
```

### Task 3: 复制毕设模块

**Files:**
- Copy: `/media/xiang/数据/jaka_ws/src/` → `/home/xiang/ros2-jaka-zu7/src/`

```bash
rsync -a /media/xiang/数据/jaka_ws/src/jaka_hardware/ /home/xiang/ros2-jaka-zu7/src/jaka_hardware/
rsync -a /media/xiang/数据/jaka_ws/src/apriltag_ros/ /home/xiang/ros2-jaka-zu7/src/apriltag_ros/
rsync -a /media/xiang/数据/jaka_ws/src/hand_eye_calibration/ /home/xiang/ros2-jaka-zu7/src/hand_eye_calibration/
rsync -a /media/xiang/数据/jaka_ws/src/visual_servo/ /home/xiang/ros2-jaka-zu7/src/visual_servo/
rsync -a /media/xiang/数据/jaka_ws/src/swap_fsm/ /home/xiang/ros2-jaka-zu7/src/swap_fsm/
```

### Task 4: 复制 launch 和 scripts

**Files:**
- Copy: `/media/xiang/数据/jaka_ws/launch/` → `/home/xiang/ros2-jaka-zu7/launch/`
- Copy: `/media/xiang/数据/jaka_ws/scripts/` → `/home/xiang/ros2-jaka-zu7/scripts/`

```bash
rsync -a /media/xiang/数据/jaka_ws/launch/ /home/xiang/ros2-jaka-zu7/launch/
rsync -a /media/xiang/数据/jaka_ws/scripts/ /home/xiang/ros2-jaka-zu7/scripts/
```

### Task 5: 创建 README.md

**Files:**
- Create: `/home/xiang/ros2-jaka-zu7/README.md`

```markdown
# ros2-jaka-zu7

JAKA ZU7 机械臂 ROS2 教学项目 - 毕设

## 包含内容

- JAKA 官方 ROS2 驱动和 MoveIt 配置
- 视觉检测系统 (Apriltag)
- 手眼标定 (Eye-in-Hand)
- 视觉闭环伺服
- 换电池 12 步状态机

## 快速开始

### 仿真模式

```bash
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
ros2 launch jaka_zu7_moveit_config demo_gazebo.launch.py
```
```

## 文档

- [docs/setup.md](docs/setup.md) - 环境配置
- [docs/simulation.md](docs/simulation.md) - 仿真教程
- [docs/architecture.md](docs/architecture.md) - 系统架构
```

### Task 6: 创建 .gitignore

**Files:**
- Create: `/home/xiang/ros2-jaka-zu7/.gitignore`

```
.git
build/
install/
log/
*.pyc
__pycache__/
*.egg-info/
.venv/
venv/
*.swp
*.swo
.DS_Store
```

## Phase 2: 修复包结构

### Task 7: 检查 jaka_hardware package.xml

**Files:**
- Read: `/home/xiang/ros2-jaka-zu7/src/jaka_hardware/package.xml`
- Read: `/home/xiang/ros2-jaka-zu7/src/jaka_hardware/setup.py`

### Task 8: 检查 apriltag_ros 包结构

**Files:**
- Read: `/home/xiang/ros2-jaka-zu7/src/apriltag_ros/package.xml`
- Read: `/home/xiang/ros2-jaka-zu7/src/apriltag_ros/launch/apriltag.launch.py`

### Task 9: 检查 hand_eye_calibration 包结构

**Files:**
- Read: `/home/xiang/ros2-jaka-zu7/src/hand_eye_calibration/package.xml`
- Read: `/home/xiang/ros2-jaka-zu7/src/hand_eye_calibration/setup.py`

### Task 10: 检查 visual_servo 包结构

**Files:**
- Read: `/home/xiang/ros2-jaka-zu7/src/visual_servo/package.xml`
- Read: `/home/xiang/ros2-jaka-zu7/src/visual_servo/setup.py`

### Task 11: 检查 swap_fsm 包结构

**Files:**
- Read: `/home/xiang/ros2-jaka-zu7/src/swap_fsm/package.xml`
- Read: `/home/xiang/ros2-jaka-zu7/src/swap_fsm/setup.py`
- Check: `/home/xiang/ros2-jaka-zu7/src/swap_fsm/swap_fsm/action/Swap.action`

## Phase 3: colcon build 测试

### Task 12: 运行 colcon build

**Files:**
- Run: `cd /home/xiang/ros2-jaka-zu7 && colcon build 2>&1`

### Task 13: 安装缺失依赖

**Files:**
- Run: `rosdep install -r -y --from-paths src --ignore-src 2>&1 | tail -50`

## Phase 4: 仿真测试

### Task 14: 测试 Gazebo 仿真启动

**Files:**
- Run: `source /home/xiang/ros2-jaka-zu7/install/setup.bash && ros2 launch jaka_zu7_moveit_config demo_gazebo.launch.py`

### Task 15: 检查仿真问题并修复

**Files:**
- 根据错误信息搜索 GitHub 参考项目
- 修复 ros2_control 配置
- 修复 URDF/XACRO 问题

## Phase 5: 视觉模块集成测试

### Task 16: 测试 apriltag 检测

**Files:**
- Run: `ros2 launch jaka_vision apriltag_detector.launch.py`

### Task 17: 测试 simulated_detector_node

**Files:**
- Run: `ros2 launch jaka_vision simulated_detector.launch.py`
