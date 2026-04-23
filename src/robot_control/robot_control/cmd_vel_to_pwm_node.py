#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Int32MultiArray
import math


wheel_separation = 0.425  # meter
max_linear_speed = 0.5      # m/s
max_angular_speed = 2.0     # rad/s
max_pwm = 90            # max PWM value for motor control
min_pwm = 60             # min PWM value for motor control

class Cmd_Vel_To_PWM_Node(Node):
    def __init__(self):
        super().__init__('cmd_vel_to_pwm_node')
        
        # declare and get parameters
        
        self.declare_parameter('wheel_separation', wheel_separation)
        self.declare_parameter('max_linear_speed', max_linear_speed)
        self.declare_parameter('max_angular_speed', max_angular_speed)
        self.declare_parameter('max_pwm', max_pwm)
        self.declare_parameter('min_pwm', min_pwm)
        
        self.wheel_separation = self.get_parameter('wheel_separation').value
        self.max_linear_speed = self.get_parameter('max_linear_speed').value
        self.max_angular_speed = self.get_parameter('max_angular_speed').value
        self.max_pwm = self.get_parameter('max_pwm').value
        self.min_pwm = self.get_parameter('min_pwm').value
        self.direction = 1
        
        # declare publisher and subscriber
        self.publisher = self.create_publisher(Int32MultiArray, '/get_pwm_values',10)
        
        self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback,10)
        
        
        self.get_logger().info(
            f'Twist to PWM node started.\n'
            f'  wheel_separation = {self.wheel_separation} m\n'
            f'  max_linear_speed = {self.max_linear_speed} m/s\n'
            f'  max_pwm          = {self.max_pwm}\n'
            f'  min_pwm          = {self.min_pwm}  (deadband)\n'
            f'Subscribing to /cmd_vel ...'
        )
        
    def cmd_vel_callback(self,msg):
        linear_x = msg.linear.x
        angular_z = msg.angular.z
        
        # Compute wheel speeds
        v_left = linear_x - (angular_z * self.wheel_separation / 2)
        v_right = linear_x + (angular_z * self.wheel_separation / 2)
        
        # Convert wheel speeds to PWM values
        left_pwm = self._velocity_to_pwm(v_left)
        right_pwm = self._velocity_to_pwm(v_right)
        
        # publish PWM values
        pwm_msg = Int32MultiArray()
        pwm_msg.data = [left_pwm,right_pwm,self.direction]
        self.publisher.publish(pwm_msg)
        
    
    def _velocity_to_pwm(self, velocity):
        if abs(velocity) < 1e-4:
            return 0 
        self.direction = 1 if velocity > 0 else -1
        normalized = abs(velocity) / self.max_linear_speed
        normalized = min(normalized, 1.0)  # cap at max speed
        pwm = int(normalized * (self.max_pwm - self.min_pwm) + self.min_pwm)
        return pwm

def main(args=None):
    rclpy.init(args=args)
    node = Cmd_Vel_To_PWM_Node()
    rclpy.spin(node)
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
    