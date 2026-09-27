import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class InertiaDriver(Node):
    def __init__(self):
        super().__init__('inertia_driver')
        
        self.publisher_ = self.create_publisher(Twist, '/model/vehicle_blue/cmd_vel', 10)
        
        # Run the physics loop at 10Hz (every 0.1 seconds)
        self.timer = self.create_timer(0.1, self.apply_damping)
        
        # Mechanical simulation parameters
        self.target_velocity = 10      # The desired top speed (m/s)
        self.current_velocity = 0.5     # The actual speed starting from rest
        self.damping_coefficient = 0.01 # Controls the "weight" of the virtual flywheel

    def apply_damping(self):
        # First-order damping equation: V_current = V_current + (Error * Damping)
        velocity_error = self.target_velocity - self.current_velocity
        self.current_velocity += velocity_error * self.damping_coefficient
        
        msg = Twist()
        msg.linear.x = self.current_velocity
        self.publisher_.publish(msg)
        
        # Log the output to watch the curve flatten out
        self.get_logger().info(f'Inertia applied. Current Velocity: {self.current_velocity:.3f} m/s')

def main(args=None):
    rclpy.init(args=args)
    node = InertiaDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()