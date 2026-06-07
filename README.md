# Apex Project — AR4 Industrial Painting Robot

A ROS 2 Jazzy workspace for the **AR4 6-DOF robot arm** by Annin Robotics, developed as a graduation project for industrial painting applications. The project supports three operation modes: Gazebo simulation, mock hardware, and real hardware (in progress).

---

## Project Structure

```
ar4_ws/
└── src/
    ├── ar4_description/       # URDF, meshes, ros2_control xacro
    ├── ar4_moveit_config/     # MoveIt 2 configuration (SRDF, kinematics, controllers)
    ├── ar4_bringup/           # Main launch files and controller config
    └── vision_project/        # Vision system for painting application
```

---

## Prerequisites

- Ubuntu 24.04
- ROS 2 Jazzy ([installation guide](https://docs.ros.org/en/jazzy/Installation.html))

---

## Install Required Packages

```bash
sudo apt update && sudo apt install -y \
  ros-jazzy-moveit \
  ros-jazzy-moveit-configs-utils \
  ros-jazzy-moveit-ros-move-group \
  ros-jazzy-ros-gz \
  ros-jazzy-gz-ros2-control \
  ros-jazzy-ros2-control \
  ros-jazzy-ros2-controllers \
  ros-jazzy-joint-trajectory-controller \
  ros-jazzy-joint-state-broadcaster \
  ros-jazzy-controller-manager \
  ros-jazzy-xacro \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-rviz2
```

---

## Setup

**1. Clone the repository**
```bash
git clone https://github.com/AhmdMgdy1/Apex_Project_AR4.git ~/ar4_ws
cd ~/ar4_ws
```

**2. Install any remaining dependencies**
```bash
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

**3. Build**
```bash
colcon build --symlink-install
```

**4. Source the workspace**
```bash
source install/setup.bash
```

Add to `~/.bashrc` to auto-source on every new terminal:
```bash
echo "source ~/ar4_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## Running the Project

### Gazebo Simulation + MoveIt
Full physics simulation with motion planning:
```bash
ros2 launch ar4_bringup ar4_moveit.launch.py is_gazebo_sim:=true
```

### Mock Hardware + MoveIt
Lightweight mode — no Gazebo, robot moves in RViz only. Good for testing MoveIt config and kinematics:
```bash
ros2 launch ar4_bringup ar4_moveit.launch.py is_gazebo_sim:=false
```

---

## Operation Modes Summary

| Mode | Command | Use Case |
|------|---------|----------|
| Gazebo + MoveIt | `is_gazebo_sim:=true` | Full simulation with physics |
| Mock + MoveIt | `is_gazebo_sim:=false` | Fast MoveIt testing, no sim overhead |
| Real Hardware | Coming soon | Physical AR4 deployment |

---

## Development Roadmap

- [x] URDF / RViz visualization
- [x] ros2_control with mock hardware
- [x] MoveIt 2 motion planning
- [x] Gazebo Harmonic simulation
- [x] MoveIt + Gazebo integration
- [ ] Real hardware control via Teensy microcontroller
- [ ] Painting path planning
- [ ] Vision system integration

---

## Tech Stack

| Tool | Version |
|------|---------|
| ROS 2 | Jazzy |
| MoveIt 2 | Jazzy |
| Gazebo | Harmonic |
| Ubuntu | 24.04 |
| Robot | AR4 by Annin Robotics |

---

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit your changes: `git commit -m "feat: description"`
3. Push and open a Pull Request

---

## Team

Graduation Project — Mechatronics Engineering
