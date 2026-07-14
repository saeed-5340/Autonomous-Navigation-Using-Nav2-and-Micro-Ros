from launch import LaunchDescription
import os
from ament_index_python.packages import get_package_share_path
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    package_path = get_package_share_path('robot_description')
    
    urdf_path = os.path.join(package_path, 'urdf', 'my_car.urdf.xacro')
    rviz_config_path = os.path.join(get_package_share_path('robot_bringup'), 'rviz', 'urdf_config.rviz')
    world_path = os.path.join(package_path,'world','maze.sdf')
    bridge_config_path = os.path.join(get_package_share_path('robot_bringup'),'config','gz_bridge.yaml')
    # SIMULATION MAPPING CODE TO ADD:
    # slam_params_path = os.path.join(package_path, 'config', 'slam_toolbox_params.yaml')
    
    # SIMULATION MAPPING NOTE:
    # Gazebo launch files should use simulation time and the Gazebo bridge.
    # Add slam_toolbox here only for simulated mapping, using the simulation
    # SLAM params in config/slam_toolbox_params.yaml where use_sim_time is true.
    # Do not launch the real RPLIDAR driver from this file.
    
    
    robot_description = ParameterValue(Command(['xacro ', urdf_path]), value_type=str)
    
    gz_launch_path = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_path('ros_gz_sim'),
            'launch',
            'gz_sim.launch.py')),
        launch_arguments={'gz_args': world_path, 'use_sim_time': 'true'}.items()
    )
    
    
    
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description , 
                     "use_sim_time": True}]
    )
    
    # joint_state_publisher_node = Node(
    #     package='joint_state_publisher_gui',
    #     executable='joint_state_publisher_gui',
    #     parameters=[{"use_sim_time": True}]
    # )
    
    rviz_node = Node(
        package= 'rviz2',
        executable= 'rviz2',
        arguments=['-d',rviz_config_path],
        parameters=[{"use_sim_time": True}]
    )
    
        
    spawn_entity_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            "-name", "my_car",
            "-topic", "robot_description",
            "-x", "0.0",
            "-y", "0.0",
            "-z", "0.0"
        ],
        output='screen',
        parameters=[{"use_sim_time": True}]
    )
    
    gazebo_bridge_node = Node(
        package = 'ros_gz_bridge',
        executable = 'parameter_bridge',
        parameters=[{
            'config_file': bridge_config_path, 
            'use_sim_time': True
        }]
    )

    # SIMULATION MAPPING CODE TO ADD:
    # This is only for Gazebo mapping. It uses Gazebo /clock, simulated /scan,
    # and the Gazebo bridge from config/gz_bridge.yaml.
    #
    # slam_toolbox_node = Node(
    #     package='slam_toolbox',
    #     executable='async_slam_toolbox_node',
    #     name='slam_toolbox',
    #     output='screen',
    #     parameters=[
    #         slam_params_path,
    #         {
    #             'use_sim_time': True,
    #             'scan_topic': '/scan',
    #         },
    #     ],
    # )
    
    return LaunchDescription([
        gz_launch_path,
        spawn_entity_node,
        robot_state_publisher_node,
        # joint_state_publisher_node,
        gazebo_bridge_node,
        # rviz_node,
        # SIMULATION MAPPING CODE TO ADD:
        # slam_toolbox_node,
    ])
