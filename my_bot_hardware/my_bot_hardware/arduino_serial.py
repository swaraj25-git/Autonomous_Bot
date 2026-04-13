import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray
from geometry_msgs.msg import Twist
import serial

class ArduinoBridge(Node):
    def __init__(self):
        super().__init__('arduino_bridge')
        
        # Corrected Baud Rate to 57600 to match your Arduino code
        self.serial_port = serial.Serial('/dev/ttyACM0', 57600, timeout=0.1)
        
        self.encoder_pub = self.create_publisher(Int32MultiArray, 'encoder_ticks', 10)
        self.cmd_vel_sub = self.create_subscription(Twist, 'cmd_vel', self.cmd_vel_callback, 10)
        
        self.timer = self.create_timer(0.05, self.read_serial_data)
        self.get_logger().info('Arduino Bridge started at 57600 baud.')

    def cmd_vel_callback(self, msg):
        linear_x = msg.linear.x
        angular_z = msg.angular.z
        
        # Basic Kinematics: You may need to scale these values to 0-255 PWM
        # PWM_val = (velocity * speed_to_pwm_ratio)
        left_speed = int((linear_x - angular_z) * 255) 
        right_speed = int((linear_x + angular_z) * 255)
        
        # Constrain to PWM limits
        left_speed = max(min(left_speed, 255), -255)
        right_speed = max(min(right_speed, 255), -255)

        # Matched your Arduino: "m <left_pwm> <right_pwm>"
        command = f"m {left_speed} {right_speed}\n"
        self.serial_port.write(command.encode('utf-8'))

    def read_serial_data(self):
        if self.serial_port.in_waiting > 0:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                # Matched your Arduino: "e <left_count> <right_count>"
                if line.startswith('e '):
                    parts = line.split(' ')
                    if len(parts) == 3:
                        msg = Int32MultiArray()
                        msg.data = [int(parts[1]), int(parts[2])]
                        self.encoder_pub.publish(msg)
            except Exception as e:
                self.get_logger().warn(f"Serial read error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = ArduinoBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.serial_port.close()
        node.destroy_node()
        rclpy.shutdown()