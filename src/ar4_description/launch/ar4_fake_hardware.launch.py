"""
AR4 Fake Hardware Launch File
File: launch/ar4_fake_hardware.launch.py

Launches the AR4 arm with mock_components/GenericSystem.
NO real robot or Gazebo physics needed — joints respond instantly.
Perfect for testing ros2_control + MoveIt2 pipeline.

Run with:
    ros2 launch ar4_description ar4_fake_hardware.launch.py
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # ── Arguments ────────────────────────────────────────────
    declared_args = [
        DeclareLaunchArgument(
            "use_mock_hardware",
            default_value="true",
            description="Use mock hardware (no real robot needed)",
        ),
    ]

    use_mock_hardware = LaunchConfiguration("use_mock_hardware")

    # ── Robot Description (URDF from xacro) ──────────────────
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("ar4_description"), "urdf", "ar4.urdf.xacro"]
                #                  ^^^^^^^^^^
                #        Replace "ar4_description" with your actual package name
            ),
            " use_mock_hardware:=",
            use_mock_hardware,
        ]
    )

    robot_description = {
        "robot_description": ParameterValue(
            value=robot_description_content, value_type=str
        )
    }

    # ── Controller Manager config ─────────────────────────────
    robot_controllers = PathJoinSubstitution(
        [FindPackageShare("ar4_description"), "config", "controllers.yaml"]
        #                  ^^^^^^^^^^
        #        Replace "ar4_description" with your actual package name
    )

    # ── Nodes ─────────────────────────────────────────────────

    # 1. Robot State Publisher — publishes TF from /joint_states
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
    )

    # 2. Controller Manager — the core ros2_control node
    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, robot_controllers],
        output="screen",
    )

    # 3. Joint State Broadcaster — spawned AFTER controller manager starts
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager", "/controller_manager",
        ],
    )

    # 4. Joint Trajectory Controller — spawned AFTER broadcaster is active
    joint_trajectory_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_trajectory_controller",
            "--controller-manager", "/controller_manager",
        ],
    )

    # ── Spawn trajectory controller only after broadcaster is up ──
    delay_jtc_after_jsb = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[joint_trajectory_controller_spawner],
        )
    )

    # 5. RViz — optional, comment out if you don't need it
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", PathJoinSubstitution(
            [FindPackageShare("ar4_description"), "rviz", "urdf_config.rviz"]
        )],
    )

    return LaunchDescription(
        declared_args
        + [
            robot_state_publisher_node,
            control_node,
            joint_state_broadcaster_spawner,
            delay_jtc_after_jsb,
            rviz_node,
        ]
    )
