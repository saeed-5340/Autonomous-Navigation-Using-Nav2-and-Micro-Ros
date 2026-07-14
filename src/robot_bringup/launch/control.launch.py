from launch import LaunchDescription
import os
from ament_index_python.packages import get_package_share_path
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription

# REAL MAPPING CODE TO ADD IF YOU DO NOT USE robot_bringup:
# from launch_ros.parameter_descriptions import ParameterValue
# from launch.substitutions import Command


def generate_launch_description():
    
    pkg_path_1 = get_package_share_path('robot_description')
    pkg_path_2 = get_package_share_path('robot_control')
    pkg_path_3 = get_package_share_path('robot_bringup')
    
    # REAL ROBOT MAPPING NOTE:
    # If there is no separate robot_bringup package, this is the launch file
    # where you would add the real mapping stack:
    # - robot_state_publisher / URDF
    # - dead_reckoning_node and cmd_vel_to_pwm_node
    # - slam_toolbox async_slam_toolbox_node
    # - rviz2 with a mapping RViz config
    # - a static transform from lidar_link to the real scan frame if needed
    # For RPLIDAR C1, /scan often uses frame_id "laser", while the URDF frame is
    # "lidar_link", so a static lidar_link -> laser transform is required.
    # Keep use_sim_time false for the real robot.
    
    robot_description_launch = os.path.join(pkg_path_3, 'launch', 'display.launch.py')
    # REAL MAPPING CODE TO ADD IF YOU DO NOT USE robot_bringup:
    # slam_params_path = os.path.join(pkg_path_1, 'config', 'slam_toolbox_params.yaml')
    # mapping_rviz_path = os.path.join(pkg_path_1, 'rviz', 'urdf_config.rviz')
    #
    # For real mapping, edit slam_toolbox_params.yaml so use_sim_time is false.
    # Also edit urdf_config.rviz or make a new RViz config with:
    # - Fixed Frame: map
    # - Map display: /map
    # - LaserScan display: /scan
    # - RobotModel display: /robot_description
    # - TF display
    
    display_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(robot_description_launch))
    
    # display_launch = Node(
    #     package = 'robot_description',
    #     executable = 'display.launch.py',
    #     name = 'display_launch',
    #     output = 'screen',
    #     # launch_arguments={'use_sim_time': 'true'}.items()
    # )
    
    dead_reckoning_node = Node(
        package = 'robot_control',
        executable = 'dead_reckoning_node',
        name = 'dead_reckoning_node',
        output = 'screen',
        
    )
    
    cmd_vel_to_pwm_node = Node(
        package = 'robot_control',
        executable = 'cmd_vel_to_pwm_node',
        name = 'cmd_vel_to_pwm_node',
        output = 'screen',
    )
    
    rqt_launch = Node(
        package='rqt_graph',
        executable='rqt_graph',
        name = 'rqt_graph',
        output = 'screen',
    )

    # REAL MAPPING CODE TO ADD IF YOU DO NOT USE robot_bringup:
    # Your RPLIDAR C1 publishes /scan with header.frame_id "laser".
    # Your URDF has the physical lidar frame named "lidar_link".
    # This static transform connects those two names for SLAM Toolbox.
    #
    # lidar_scan_frame_tf_node = Node(
    #     package='tf2_ros',
    #     executable='static_transform_publisher',
    #     name='lidar_scan_frame_publisher',
    #     output='screen',
    #     arguments=[
    #         '0', '0', '0',
    #         '0', '0', '0',
    #         'lidar_link', 'laser',
    #     ],
    # )
    #
    # slam_toolbox_node = Node(
    #     package='slam_toolbox',
    #     executable='async_slam_toolbox_node',
    #     name='slam_toolbox',
    #     output='screen',
    #     parameters=[
    #         slam_params_path,
    #         {
    #             'use_sim_time': False,
    #             'scan_topic': '/scan',
    #         },
    #     ],
    # )
    #
    # rviz_mapping_node = Node(
    #     package='rviz2',
    #     executable='rviz2',
    #     name='rviz2_mapping',
    #     output='screen',
    #     arguments=['-d', mapping_rviz_path],
    #     parameters=[{'use_sim_time': False}],
    # )
    
    
    return LaunchDescription([
        display_launch,
        dead_reckoning_node,
        cmd_vel_to_pwm_node,
        rqt_launch,
        # REAL MAPPING CODE TO ADD IF YOU DO NOT USE robot_bringup:
        # Add these to the LaunchDescription list after rqt_launch:
        # lidar_scan_frame_tf_node,
        # slam_toolbox_node,
        # rviz_mapping_node,
    ])
