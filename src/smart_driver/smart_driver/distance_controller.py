import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

class DistanceController(Node):
    def __init__(self):
        super().__init__('distance_controller')
        
        # Publisher for movement commands
        self.publisher_ = self.create_publisher(Twist, '/model/vehicle_blue/cmd_vel', 10)
        
        # Subscriber for spatial position tracking
        self.subscription = self.create_subscription(
            Odometry,
            '/model/vehicle_blue/odometry',
            self.odom_callback,
            10)
            
        self.target_distance = 5.0
        self.reached_target = False

    def odom_callback(self, msg):
        # If the target is already reached, ignore new odometry data
        if self.reached_target:
            return

        # Extract the current X-coordinate from the complex Odometry message structure
        current_x = msg.pose.pose.position.x
        
        twist_msg = Twist()
        
        if current_x < self.target_distance:
            # Keep driving forward at 1.0 m/s
            twist_msg.linear.x = 1.0
            self.publisher_.publish(twist_msg)
            self.get_logger().info(f'Moving... Current Position: X = {current_x:.2f}m')
        else:
            # Stop the robot by publishing 0.0 m/s
            twist_msg.linear.x = 0.0
            self.publisher_.publish(twist_msg)
            self.get_logger().info('Target distance of 5.0m reached. Engaging brakes.')
            self.reached_target = True

def main(args=None):
    rclpy.init(args=args)
    node = DistanceController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()