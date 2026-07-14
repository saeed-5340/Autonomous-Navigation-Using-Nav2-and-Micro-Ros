# Real Robot Mapping

This repo now has a hardware mapping launch:

Launch In Terminal - 1

```bash
ros2 launch robot_description real_map.launch.py 
```
Launch In Terminal - 2

```bash
ros2 launch rplidar_ros rplidar_c1_launch.py
```
Note: For rplidar model use these model launch file.
github repo for rplidar package : https://github.com/Slamtec/rplidar_ros.git

Start your real LiDAR driver before or alongside that launch. The driver must publish:

```bash
/scan  sensor_msgs/msg/LaserScan
```

Quick checks:

```bash
ros2 topic list
ros2 topic echo /scan --once
ros2 topic hz /scan
ros2 run tf2_tools view_frames
```

For SLAM Toolbox to create `/map`, these transforms must exist:

```text
map -> odom
odom -> base_footprint
base_footprint -> base_link -> lidar_link
```

`real_map.launch.py` starts:

- `robot_state_publisher` for the robot URDF and fixed LiDAR transform
- `dead_reckoning_node` for `odom -> base_footprint`
- `cmd_vel_to_pwm_node`
- `slam_toolbox` in mapping mode with `use_sim_time: false`
- RViz with `/map`, `/scan`, `/odom`, robot model, and TF displays

If your LiDAR publishes on a different topic:

```bash
ros2 launch robot_bringup real_mapping.launch.py scan_topic:=/your_scan_topic
```

For RPLIDAR C1, the scan frame is commonly `laser`. The mapping launch publishes a fixed transform from `lidar_link` to `laser` by default. If your LiDAR message uses a different `header.frame_id`, pass it to the launch:

```bash
ros2 launch robot_bringup real_mapping.launch.py scan_frame:=your_laser_frame
```

Check the live scan frame with:

```bash
ros2 topic echo /scan --once --field header
```

Save a map after driving around:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/my_map
```

If RViz shows LaserScan points but no map, check `/odom` and TF. If RViz shows neither points nor map, the LiDAR driver/topic/frame is the first thing to fix.
