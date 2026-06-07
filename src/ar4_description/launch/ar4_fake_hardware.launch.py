"""
How to Run: ros2 launch ar4_description ar4_fake_hardware.launch.py is_gazebo_sim:=false
How to Test:
ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{
  header: {frame_id: ''},
  joint_names: ['Joint_0', 'Joint_1', 'Joint_2', 'Joint_3', 'Joint_4', 'Joint_5'],
  points: [
    {
      positions: [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
      velocities: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
      time_from_start: {sec: 2, nanosec: 0}
    }
  ]
}"

ros2 topic pub --once /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory "{
  header: {frame_id: ''},
  joint_names: ['Joint_0', 'Joint_1', 'Joint_2', 'Joint_3', 'Joint_4', 'Joint_5'],
  points: [
    {
      positions: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
      velocities: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
      time_from_start: {sec: 2, nanosec: 0}
    }
  ]
}"

"""

import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    ar4_description_dir = get_package_share_directory("ar4_description")

    # ─── Args ───────────────────────────────────────────────────────────────
    is_gazebo_sim_arg = DeclareLaunchArgument(
        name="is_gazebo_sim",
        default_value="true",
        description="Use Gazebo simulation (true) or mock/real hardware (false)"
    )

    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(ar4_description_dir, "urdf", "ar4.urdf.xacro"),
        description="Absolute path to the robot URDF file"
    )

    is_gazebo_sim = LaunchConfiguration("is_gazebo_sim")

    # ─── Robot Description ──────────────────────────────────────────────────
    robot_description = ParameterValue(
        Command(["xacro ", LaunchConfiguration("model"), " is_gazebo_sim:=", is_gazebo_sim]),
        value_type=str
    )

    # ─── Robot State Publisher ──────────────────────────────────────────────
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{
            "robot_description": robot_description,
            "use_sim_time": is_gazebo_sim
        }]
    )

    # ─── Mock hardware only ─────────────────────────────────────────────────
    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            {"robot_description": robot_description},
            os.path.join(ar4_description_dir, "config", "controllers.yaml")
        ]
    )

    # ─── Controllers ────────────────────────────────────────────
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"]
    )

    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller", "--controller-manager", "/controller_manager"]
    )

    # ─── RViz ───────────────────────────────────────────────────────────────
    rviz_mock = Node(                              
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", os.path.join(ar4_description_dir, "rviz", "ar4.rviz")]
    )

    return LaunchDescription([
        is_gazebo_sim_arg,
        model_arg,
        robot_state_publisher,
        ros2_control_node,
        joint_state_broadcaster_spawner,
        arm_controller_spawner,
        rviz_mock,
    ])