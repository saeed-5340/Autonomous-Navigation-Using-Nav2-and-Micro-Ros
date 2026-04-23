from launch import LaunchDescription
import os
from ament_index_python.packages import get_package_share_path
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription


def generate_launch_description():
    
    pkg_path_1 = get_package_share_path('robot_description')
    pkg_path_2 = get_package_share_path('robot_control')
    
    robot_description_launch = os.path.join(pkg_path_1, 'launch', 'display.launch.py')
    
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
    
    
    return LaunchDescription([
        display_launch,
        dead_reckoning_node,
        cmd_vel_to_pwm_node,
        rqt_launch
    ])