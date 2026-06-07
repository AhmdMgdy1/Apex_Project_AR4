"""
How to Run:
1- Gazebo Simulation:
   $ ros2 launch ar4_bringup ar4_moveit.launch.py
2- Mock/Real Hardware:
   $ ros2 launch ar4_bringup ar4_moveit.launch.py is_gazebo_sim:=false
"""

import os
from pathlib import Path
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():

    ar4_description_dir = get_package_share_directory("ar4_description")
    ar4_bringup_dir     = get_package_share_directory("ar4_bringup")
    ar4_moveit_dir      = get_package_share_directory("ar4_moveit_config")

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

    # ─── MoveIt Config ──────────────────────────────────────────────────────
    moveit_config = (
        MoveItConfigsBuilder("AR4", package_name="ar4_moveit_config")
        .to_moveit_configs()
    )

    # ─── Robot Description ──────────────────────────────────────────────────
    robot_description = ParameterValue(
        Command(["xacro ", LaunchConfiguration("model"), " is_gazebo_sim:=", is_gazebo_sim]),
        value_type=str
    )

    # ─── Environment ────────────────────────────────────────────────────────
    gazebo_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=[str(Path(ar4_description_dir).parent.resolve())]
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
            os.path.join(ar4_bringup_dir, "config", "ros2_controllers.yaml")
        ],
        condition=UnlessCondition(is_gazebo_sim)
    )

    # ─── Gazebo only ────────────────────────────────────────────────────────
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory("ros_gz_sim"), "launch"),
            "/gz_sim.launch.py"
        ]),
        launch_arguments=[("gz_args", " -v 4 -r empty.sdf")],
        condition=IfCondition(is_gazebo_sim)
    )

    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=["-topic", "robot_description", "-name", "AR4"],
        condition=IfCondition(is_gazebo_sim)
    )

    gz_ros2_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"],
        parameters=[{"use_sim_time": True}],
        condition=IfCondition(is_gazebo_sim)
    )

    # ─── Controllers (both modes) ────────────────────────────────────────────
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

    # ─── MoveIt move_group ──────────────────────────────────────────────────
    move_group_mock = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(ar4_moveit_dir, "launch"),
            "/move_group.launch.py"
        ]),
        condition=UnlessCondition(is_gazebo_sim)
    )

    move_group_gazebo = TimerAction(
        period=5.0,
        actions=[
            Node(
                package="moveit_ros_move_group",
                executable="move_group",
                output="screen",
                parameters=[
                    moveit_config.to_dict(),
                    {"use_sim_time": True},
                ],
                condition=IfCondition(is_gazebo_sim)
            )
        ]
    )

    # ─── RViz ───────────────────────────────────────────────────────────────
    rviz_mock = Node(                              # ← fixed: was IncludeLaunchDescription
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", os.path.join(ar4_bringup_dir, "config", "moveit.rviz")],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
        ],
        condition=UnlessCondition(is_gazebo_sim)
    )

    rviz_gazebo = TimerAction(
        period=7.0,
        actions=[
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                output="screen",
                arguments=["-d", os.path.join(ar4_bringup_dir, "config", "moveit.rviz")],
                parameters=[
                    moveit_config.robot_description,
                    moveit_config.robot_description_semantic,
                    moveit_config.robot_description_kinematics,
                    moveit_config.planning_pipelines,
                    moveit_config.joint_limits,
                    {"use_sim_time": True},
                ],
                condition=IfCondition(is_gazebo_sim)
            )
        ]
    )

    return LaunchDescription([
        is_gazebo_sim_arg,
        model_arg,
        gazebo_resource_path,
        gazebo,
        gz_ros2_bridge,
        robot_state_publisher,
        ros2_control_node,
        gz_spawn_entity,
        joint_state_broadcaster_spawner,
        arm_controller_spawner,
        move_group_mock,
        move_group_gazebo,
        rviz_mock,
        rviz_gazebo,
    ])