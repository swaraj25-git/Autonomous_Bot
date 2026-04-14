import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray
from nav_msgs.msg import Odometry
import math

class OdometryNode(Node):
    def __init__(self):
        super().__init__('odom_node')

        # --- Robot Physical Parameters ---
        # Pulled from your URDF (robot_core.xacro)
        self.wheel_radius = 0.055  # meters
        self.wheel_separation = 0.48  # meters (0.24 * 2)
        
        # IMPORTANT: You must change this to match your specific encoder/motor specs!
        # (e.g., How many ticks does your Arduino count for exactly 1 full rotation of the wheel?)
        self.ticks_per_rev = 3061.7 

        # --- State Variables ---
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        
        self.prev_left_ticks = 0
        self.prev_right_ticks = 0
        self.last_time = self.get_clock().now()

        # --- ROS 2 Interfaces ---
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.encoder_sub = self.create_subscription(
            Int32MultiArray, 
            'encoder_ticks', 
            self.encoder_callback, 
            10
        )
        self.get_logger().info('Odometry Kinematics Node started.')

    def encoder_callback(self, msg):
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds / 1e9

        if dt <= 0:
            return

        # Extract current ticks
        current_left_ticks = msg.data[0]
        current_right_ticks = msg.data[1]

        # Calculate difference in ticks since last callback
        delta_left_ticks = current_left_ticks - self.prev_left_ticks
        delta_right_ticks = current_right_ticks - self.prev_right_ticks

        # Distance traveled by each wheel (in meters)
        distance_per_tick = (2.0 * math.pi * self.wheel_radius) / self.ticks_per_rev
        d_left = delta_left_ticks * distance_per_tick
        d_right = delta_right_ticks * distance_per_tick

        # Distance traveled by the center of the robot
        d_center = (d_left + d_right) / 2.0
        
        # Change in heading (theta)
        d_theta = (d_right - d_left) / self.wheel_separation

        # Update robot's pose (X, Y, Theta)
        self.x += d_center * math.cos(self.theta + (d_theta / 2.0))
        self.y += d_center * math.sin(self.theta + (d_theta / 2.0))
        self.theta += d_theta

        # Calculate velocities
        linear_v = d_center / dt
        angular_w = d_theta / dt

        # --- Create and Publish Odometry Message ---
        odom_msg = Odometry()
        odom_msg.header.stamp = current_time.to_msg()
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_link'

        # Set Pose (Position)
        odom_msg.pose.pose.position.x = self.x
        odom_msg.pose.pose.position.y = self.y
        odom_msg.pose.pose.position.z = 0.0
        
        # Convert Theta (Euler) to Quaternion for ROS
        odom_msg.pose.pose.orientation.z = math.sin(self.theta / 2.0)
        odom_msg.pose.pose.orientation.w = math.cos(self.theta / 2.0)

        # Set Twist (Velocity)
        odom_msg.twist.twist.linear.x = linear_v
        odom_msg.twist.twist.angular.z = angular_w

        self.odom_pub.publish(odom_msg)

        # Update previous values
        self.prev_left_ticks = current_left_ticks
        self.prev_right_ticks = current_right_ticks
        self.last_time = current_time

def main(args=None):
    rclpy.init(args=args)
    node = OdometryNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()