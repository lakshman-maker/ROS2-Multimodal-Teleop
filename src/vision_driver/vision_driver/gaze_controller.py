import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math

class GazeHandRacingController(Node):
    def __init__(self):
        super().__init__('racing_gaze_controller')
        self.publisher_ = self.create_publisher(Twist, '/model/vehicle_blue/cmd_vel', 10)
        
        workspace_path = '/mnt/c/Users/Lakshman/OneDrive/Documents/ROS2_workspace/2_ROS2/'
        
        # Initialize Face AI
        face_options = vision.FaceLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=workspace_path + 'face_landmarker.task'),
            num_faces=1)
        self.face_landmarker = vision.FaceLandmarker.create_from_options(face_options)
        
        # Initialize Hand AI
        hand_options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=workspace_path + 'hand_landmarker.task'),
            num_hands=1)
        self.hand_landmarker = vision.HandLandmarker.create_from_options(hand_options)
        
        # Camera Setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        self.timer = self.create_timer(0.1, self.process_frame)

    def count_fingers(self, landmarks):
        fingers = 0
        
        # Thumb: Calculate distance from tip to pinky base vs MCP to pinky base
        thumb_tip = landmarks[4]
        thumb_mcp = landmarks[2]
        pinky_mcp = landmarks[17]
        
        dist_tip = math.hypot(thumb_tip.x - pinky_mcp.x, thumb_tip.y - pinky_mcp.y)
        dist_mcp = math.hypot(thumb_mcp.x - pinky_mcp.x, thumb_mcp.y - pinky_mcp.y)
        if dist_tip > dist_mcp:
            fingers += 1
            
        # Other Fingers: Check if the fingertip is higher up on the screen than the middle joint
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        for tip, pip in zip(tips, pips):
            if landmarks[tip].y < landmarks[pip].y:
                fingers += 1
                
        return min(fingers, 5)

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret: return

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Run both AI models
        face_results = self.face_landmarker.detect(mp_image)
        hand_results = self.hand_landmarker.detect(mp_image)

        msg = Twist()
        speed = 0.0
        current_action = "NO FACE/HAND DETECTED"
        hud_color = (255, 255, 255)

        # 1. Read Hand Throttle (1 to 5 m/s)
        if hand_results.hand_landmarks:
            speed = float(self.count_fingers(hand_results.hand_landmarks[0]))

        # 2. Read Gaze Steering
        if face_results.face_landmarks:
            landmarks = face_results.face_landmarks[0]
            
            left_eye_outer, left_eye_inner = landmarks[33].x, landmarks[133].x
            iris_x, iris_y = landmarks[468].x, landmarks[468].y
            eye_top, eye_bottom = landmarks[159].y, landmarks[145].y
            
            eye_width = left_eye_inner - left_eye_outer
            eye_height = eye_bottom - eye_top
            
            if eye_width > 0 and eye_height > 0:
                h_ratio = (iris_x - left_eye_outer) / eye_width
                v_ratio = (iris_y - eye_top) / eye_height
                
                if v_ratio < 0.40:
                    msg.linear.x = 0.0
                    msg.angular.z = 0.0
                    current_action = "BRAKE (UP)"
                    hud_color = (0, 0, 255)
                elif v_ratio > 0.65:
                    msg.linear.x = -speed
                    msg.angular.z = 0.0
                    current_action = "REVERSE (DOWN)"
                    hud_color = (0, 165, 255)
                elif h_ratio < 0.40:
                    msg.linear.x = speed * 0.8
                    msg.angular.z = 1.0
                    current_action = "LEFT"
                    hud_color = (0, 255, 0)
                elif h_ratio > 0.60:
                    msg.linear.x = speed * 0.8
                    msg.angular.z = -1.0
                    current_action = "RIGHT"
                    hud_color = (0, 255, 0)
                else:
                    msg.linear.x = speed
                    msg.angular.z = 0.0
                    current_action = "GAS (CENTER)"
                    hud_color = (255, 0, 0)
        
        self.publisher_.publish(msg)

        # Draw Expanded Racing HUD
        cv2.rectangle(frame, (10, 10), (450, 140), (0, 0, 0), -1)
        cv2.putText(frame, f"GEAR: {current_action}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, hud_color, 2)
        cv2.putText(frame, f"THROTTLE: {int(speed)} Fingers", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"SPEED: {abs(msg.linear.x):.1f} m/s", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Gaze & Hand Racing HUD', frame)
        cv2.waitKey(1)

    def destroy_node(self):
        self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = GazeHandRacingController()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__': main()