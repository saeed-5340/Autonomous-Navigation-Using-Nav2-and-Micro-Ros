#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import math
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Int32MultiArray
from tf_transformations import quaternion_from_euler
import tf2_ros
from geometry_msgs.msg import TransformStamped
from sensor_msgs.msg import JointState
from std_msgs.msg import Header


wheel_radius = 0.10
wheel_separation = 0.425
ticks_per_revolution = 48
# distance_per_tick = (2 * math.pi *wheel_radius)/ticks_per_revolution



class Dead_Reckoning_Node(Node):
    def __init__(self):
        super().__init__('Odometry_publisher_node')
        
        # declare and get parameters
        self.declare_parameter('wheel_radius', wheel_radius)
        self.declare_parameter('wheel_separation', wheel_separation)
        self.declare_parameter('ticks_per_revolution', ticks_per_revolution)
        
        self.wheel_radius = self.get_parameter('wheel_radius').value
        self.wheel_separation = self.get_parameter('wheel_separation').value
        self.ticks_per_revolution = self.get_parameter('ticks_per_revolution').value
        self.distance_per_tick = (2 * math.pi *self.wheel_radius)/self.ticks_per_revolution
        
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.prev_left_ticks = None
        self.prev_right_ticks = None
        
        self.prev_time = None
        
        self.odom_publisher = self.create_publisher(Odometry, 'odom', 10)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.create_subscription(Int32MultiArray, '/get_ticks', self.encoder_callback, 10)
        self.joint_state_publisher = self.create_publisher(JointState,'/joint_states',10)
        
        self.get_logger().info('Waiting for encoder data...')
        
    def encoder_callback(self, msg):
            # if len(msg.data) < 2:
            #     self.get_logger().error('Received encoder data does not contain enough information.')
            #     return
            current_left_ticks = msg.data[0]
            current_right_ticks = msg.data[1]
            current_time = self.get_clock().now()
            self.get_logger().info(
                f'First encoder message received: left={current_left_ticks}, right={current_right_ticks}'
            )
            # ── 2. First message: just store baseline, nothing to compute yet ────
            if self.prev_left_ticks is None:
                self.prev_left_ticks  = current_left_ticks
                self.prev_right_ticks = current_right_ticks
                self.prev_time  = current_time
                self.get_logger().info(
                    f'First encoder message received: left={current_left_ticks}, right={current_right_ticks}'
                )
                return
            
            delta_left_ticks = current_left_ticks - self.prev_left_ticks
            delta_right_ticks = current_right_ticks - self.prev_right_ticks
            
            delta_left_distance = delta_left_ticks * self.distance_per_tick
            delta_right_distance = delta_right_ticks * self.distance_per_tick
            
            
            # Dead reckoning calculations
            delta_s = (delta_right_distance + delta_left_distance) / 2.0
            delta_theta = (delta_right_distance - delta_left_distance) / self.wheel_separation
            
            self.x += delta_s * math.cos(self.theta + delta_theta / 2.0)
            self.y += delta_s * math.sin(self.theta + delta_theta / 2.0)
            self.theta += delta_theta
            
            self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))
            
            dt = (current_time - self.prev_time).nanoseconds / 1e9
            if dt > 0:
                vb = delta_s / dt
                omega = delta_theta / dt
            else:
                vb = 0.0
                omega = 0.0
                
             
             
                
            # Publish joint states for visualization
            
            left_theta_for_joint_state = (delta_left_ticks / self.ticks_per_revolution) * 2 * math.pi
            right_theta_for_joint_state = (delta_right_ticks / self.ticks_per_revolution) * 2 * math.pi
            joint_V_right = (delta_right_distance / dt) * self.wheel_radius
            joint_V_left = (delta_left_distance / dt) * self.wheel_radius
            joint_state_msg = JointState()
            joint_state_msg.header = Header()
            joint_state_msg.header.stamp = current_time.to_msg()
            joint_state_msg.header.frame_id = ''
            
            joint_state_msg.name = ['left_wheel_joint', 'right_wheel_joint']
            
            joint_state_msg.position = [left_theta_for_joint_state, right_theta_for_joint_state]
            
            joint_state_msg.velocity = [joint_V_left, joint_V_right]
            
            joint_state_msg.effort = []
            
            self.joint_state_publisher.publish(joint_state_msg)
            
            

            # ── 7. Build quaternion from yaw (theta) ─────────────────────────────
            q = quaternion_from_euler(0.0, 0.0, self.theta)
            #   returns [x, y, z, w]
    
            # ── 8. Publish TF: odom → base_footprint ────────────────────────────
            tf_msg                         = TransformStamped()
            tf_msg.header.stamp            = current_time.to_msg()
            tf_msg.header.frame_id         = 'odom'
            tf_msg.child_frame_id          = 'base_footprint'
            tf_msg.transform.translation.x = self.x
            tf_msg.transform.translation.y = self.y
            tf_msg.transform.translation.z = 0.0
            tf_msg.transform.rotation.x    = q[0]
            tf_msg.transform.rotation.y    = q[1]
            tf_msg.transform.rotation.z    = q[2]
            tf_msg.transform.rotation.w    = q[3]
    
            self.tf_broadcaster.sendTransform(tf_msg)
               
            # ── 9. Publish Odometry message ──────────────────────────────────────
            odom_msg = Odometry()
            odom_msg.header.stamp = current_time.to_msg()
            odom_msg.header.frame_id = 'odom'
            odom_msg.child_frame_id = 'base_footprint'
            
            # Pose
            odom_msg.pose.pose.position.x     = self.x
            odom_msg.pose.pose.position.y     = self.y
            odom_msg.pose.pose.position.z     = 0.0
            odom_msg.pose.pose.orientation.x  = q[0]
            odom_msg.pose.pose.orientation.y  = q[1]
            odom_msg.pose.pose.orientation.z  = q[2]
            odom_msg.pose.pose.orientation.w  = q[3]
    
            # Twist (velocity)
            odom_msg.twist.twist.linear.x     = vb
            odom_msg.twist.twist.angular.z    = omega
    
            self.odom_publisher.publish(odom_msg)
            
            # ── 10. Update previous values ───────────────────────────────────────
            self.prev_left_ticks  = current_left_ticks
            self.prev_right_ticks = current_right_ticks
            self.prev_time        = current_time
            

def main(args=None):
    rclpy.init(args=args)
    node = Dead_Reckoning_Node()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()