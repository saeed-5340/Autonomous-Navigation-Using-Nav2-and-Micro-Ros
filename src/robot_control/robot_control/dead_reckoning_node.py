#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import math
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Int32MultiArray

class Dead_Reckoning_Node(Node):
    def __init__(self):
        super().__init__('Odometry_publisher_node')
        
        self.odom_publisher = self.create_publisher(Odometry, 'odom',10)
        self.subscriptions = self.create_subscription(Int32MultiArray,
            'encoder_data',
            self.encoder_callback,
            10)
        self.tf_publisher = self.create_publisher(Twist, 'tf' , 10)
        
        