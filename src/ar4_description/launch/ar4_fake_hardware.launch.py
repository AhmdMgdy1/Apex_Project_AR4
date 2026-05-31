"""
AR4 Fake Hardware Launch File
File: ar4_description/launch/ar4_fake_hardware.launch.py
ROS2 Distro: Jazzy

Starts the AR4 arm with mock_components/GenericSystem.
No real robot or Gazebo needed.
Use this to test ros2_control and MoveIt2 planning.

Usage:
    ros2 launch ar4_description ar4_fake_hardware.launch.py

Verify after launch:
    ros2 control list_controllers
    ros2 topic echo /joint_states

    Testing motion in Rviz:
    ros2 action send_goal /joint_trajectory_controller/follow_joint_trajectory \
    control_msgs/action/FollowJointTrajectory "{
    trajectory: {
    joint_names: [Joint_0, Joint_1, Joint_2, Joint_3, Joint_4, Joint_5],
    points: [
      {
        positions: [0.5, 0.3, -0.3, 0.0, 0.5, 0.0],
        velocities: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        time_from_start: {sec: 3, nanosec: 0}
      }
    ]
  }
}"
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.substitutions import (
    Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    # ── Arguments ─────────────────────────────────────────────
    declared_args = [
        DeclareLaunchArgument(
            "gazebo",
            default_value="false",
            description="false = mock hardware | true = Gazebo hardware",
        ),
    ]

    gazebo_arg = LaunchConfiguration("gazebo")

    # ── Robot description (xacro → URDF string) ───────────────
    robot_description_content = ParameterValue(
        Command([
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("ar4_description"), "urdf", "ar4.urdf.xacro"]
            ),
            " gazebo:=",
            gazebo_arg,
        ]),
        value_type=str,
    )
    robot_description = {"robot_description": robot_description_content}

    # ── Controllers config ────────────────────────────────────
    robot_controllers = PathJoinSubstitution(
        [FindPackageShare("ar4_description"), "config", "controllers.yaml"]
    )

    # ── RViz config ───────────────────────────────────────────
    rviz_config = PathJoinSubstitution(
        [FindPackageShare("ar4_description"), "rviz", "ar4.rviz"]
    )

    # ═══════════════════════════════════════════════════════════
    #  NODES
    # ═══════════════════════════════════════════════════════════

    # 1. Robot State Publisher
    #    Reads robot_description and publishes TF transforms
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
    )

    # 2. ros2_control node
    #    Loads the hardware interface (mock_components/GenericSystem)
    #    and starts the controller manager
    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, robot_controllers],
        output="screen",
    )

    # 3. Joint State Broadcaster spawner
    #    Must be activated FIRST — publishes /joint_states
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager", "/controller_manager",
        ],
        output="screen",
    )

    # 4. Joint Trajectory Controller spawner
    #    Activated AFTER broadcaster — accepts trajectory goals
    joint_trajectory_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_trajectory_controller",
            "--controller-manager", "/controller_manager",
        ],
        output="screen",
    )

    # Enforce order: JTC starts only after JSB is confirmed active
    delay_jtc_after_jsb = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[joint_trajectory_controller_spawner],
        )
    )

    # 5. RViz
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config],
        parameters=[robot_description],
    )

    return LaunchDescription(
        declared_args + [
            robot_state_publisher_node,
            control_node,
            joint_state_broadcaster_spawner,
            delay_jtc_after_jsb,
            rviz_node,
        ]
    )
