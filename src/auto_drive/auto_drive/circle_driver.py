import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class CircleDriver(Node):
    def __init__(self):
        super().__init__('circle_driver')
        
        # Publish to the specific Gazebo bridge topic
        self.publisher_ = self.create_publisher(Twist, '/model/vehicle_blue/cmd_vel', 10)
        
        # Publish a movement command every 0.5 seconds
        self.timer = self.create_timer(0.5, self.move_robot)

    def move_robot(self):
        msg = Twist()
        
        # Linear velocity (Forward speed in m/s)
        msg.linear.x = 2.0 
        
        # Angular velocity (Rotation speed in rad/s)
        msg.angular.z = 1.0 
        
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing velocity: Driving in a circle...')

def main(args=None):
    rclpy.init(args=args)
    node = CircleDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()