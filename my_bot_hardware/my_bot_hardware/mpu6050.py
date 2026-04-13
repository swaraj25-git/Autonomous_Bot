import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import smbus2
import math

# MPU6050 Registers and Addresses
PWR_MGMT_1   = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H  = 0x43
Device_Address = 0x68   # Default I2C address for MPU6050

class MPU6050Node(Node):
    def __init__(self):
        super().__init__('mpu6050_node')
        self.publisher_ = self.create_publisher(Imu, 'imu', 10)
        
        # Initialize I2C bus (Bus 1 is default on Pi)
        self.bus = smbus2.SMBus(1)
        self.bus.write_byte_data(Device_Address, PWR_MGMT_1, 0)
        
        # Publish at 50Hz (0.02 seconds)
        self.timer = self.create_timer(0.02, self.publish_imu_data)
        self.get_logger().info('MPU6050 IMU Node has been started.')

    def read_raw_data(self, addr):
        high = self.bus.read_byte_data(Device_Address, addr)
        low = self.bus.read_byte_data(Device_Address, addr+1)
        value = ((high << 8) | low)
        if(value > 32768):
            value = value - 65536
        return value

    def publish_imu_data(self):
        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link'

        # Read Accelerometer raw value (divide by 16384.0 and multiply by 9.81 to get m/s^2)
        msg.linear_acceleration.x = (self.read_raw_data(ACCEL_XOUT_H) / 16384.0) * 9.81
        msg.linear_acceleration.y = (self.read_raw_data(ACCEL_XOUT_H + 2) / 16384.0) * 9.81
        msg.linear_acceleration.z = (self.read_raw_data(ACCEL_XOUT_H + 4) / 16384.0) * 9.81

        # Read Gyroscope raw value (divide by 131.0 to get deg/s, then convert to rad/s)
        msg.angular_velocity.x = (self.read_raw_data(GYRO_XOUT_H) / 131.0) * (math.pi / 180.0)
        msg.angular_velocity.y = (self.read_raw_data(GYRO_XOUT_H + 2) / 131.0) * (math.pi / 180.0)
        msg.angular_velocity.z = (self.read_raw_data(GYRO_XOUT_H + 4) / 131.0) * (math.pi / 180.0)

        # Note: MPU6050 does not have a magnetometer, so orientation is usually calculated 
        # downstream by an EKF (like robot_localization) using these accel/gyro values.
        
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = MPU6050Node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()