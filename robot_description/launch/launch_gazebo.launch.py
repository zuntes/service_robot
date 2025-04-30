import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument
from launch.actions import RegisterEventHandler
from launch.conditions import IfCondition
from launch.conditions import UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command
from launch.substitutions import FindExecutable
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare




def generate_launch_description():

    package_name='robot_description' 

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true', 'use_ros2_control': 'false'}.items()
    )

    joystick = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','joystick.launch.py'
                )])
    )

    twist_mux_params = os.path.join(get_package_share_directory(package_name),'config','twist_mux.yaml')
    twist_mux = Node(
            package="twist_mux",
            executable="twist_mux",
            parameters=[twist_mux_params, {'use_sim_time': True}],
            remappings=[('/cmd_vel_out','/cmd_vel')]
        )
    
    world_file_name = 'house.world'
    world = os.path.join(get_package_share_directory(package_name), 'worlds', world_file_name)

    gazebo_params_file = os.path.join(get_package_share_directory(package_name),'config','gazebo_params.yaml')

    # Include the Gazebo launch file, provided by the gazebo_ros package
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
                    launch_arguments={'world' : world,
                                      'extra_gazebo_args': '--ros-args --params-file ' + gazebo_params_file}.items()
             )

    # Run the spawner node from the gazebo_ros package. The entity name doesn't really matter if you only have a single robot.
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'service_bot'],
                        output='screen')

    rviz_config_file = 'robot.rviz'
    rviz_config = os.path.join(get_package_share_directory(package_name), 'rviz_config', rviz_config_file)
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        output='screen'
    )

    # diff_drive_spawner = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["diff_drive_controller"],
    # )

    # joint_broad_spawner = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["joint_broadcaster"],
    # )

    # delay_joint_broad_spawner = RegisterEventHandler(
    #         event_handler=OnProcessExit(
    #             target_action=spawn_entity,
    #             on_exit=[joint_broad_spawner],
    #         )
    #     )

    # delay_diff_drive_spawner = RegisterEventHandler(
    #         event_handler=OnProcessExit(
    #             target_action=joint_broad_spawner,
    #             on_exit=[diff_drive_spawner],
    #         )
    #     )

    # delay_rviz = RegisterEventHandler(
    #     event_handler=OnProcessExit(
    #         target_action=diff_drive_spawner,
    #         on_exit=[rviz_node],
    #     )
    # )

    # Launch them all!
    return LaunchDescription([
        rsp,
        #joystick,
        #twist_mux,
        gazebo,
        spawn_entity,
        # delay_joint_broad_spawner,
        # delay_diff_drive_spawner,
        rviz_node,
    ])
