# ROS 2 Multimodal Teleoperation (Gaze & Hand Control)

A computer vision-based ROS 2 control node that bridges human gesture recognition with a 3D Gazebo simulation. This project allows you to navigate a differential drive vehicle entirely hands-free (or keyboard-free) by tracking your eye movements for steering and counting your fingers for throttle control.

![Demo Placeholder](https://via.placeholder.com/800x400?text=Replace+this+with+a+GIF+of+your+HUD+and+Gazebo+moving)

## 🌟 Features
* **👀 Gaze-Based Steering & Shifting:** Tracks the iris relative to the eyelids and eye corners.
* **✋ Dynamic Hand Throttle:** Geometric hand-tracking counts raised fingers to set speed dynamically (1 to 5 m/s).
* **🖥️ Live HUD:** Projects real-time gear states, throttle metrics, and AI diagnostic data over the camera feed.
* **⚡ Hardware Optimized:** Configured to handle WSL2 USB bridge bandwidth limits by forcing MJPG codecs, eliminating decoding artifacts.

## 🛠️ Prerequisites
* **Host OS:** Windows 10/11 running WSL2 (Ubuntu)
* **ROS Distribution:** ROS 2 Lyrical
* **Simulation:** Gazebo (Ignition)
* **Python Libraries:** `opencv-python`, `mediapipe`

## ⚙️ Hardware Setup (Windows to WSL2 Passthrough)
Because WSL2 cannot natively access Windows webcams, you must use `usbipd` to bridge the connection.

1. Open **Windows PowerShell** (Administrator) and find your camera's BUSID:
   ```powershell
   usbipd list
   
2. Bind and attach the camera to Ubuntu (replace <busid> with your camera's ID):
usbipd bind --busid <busid>
usbipd attach --wsl --busid <busid>

Installation & Build
1. Clone the repository into your ROS 2 workspace:
cd ~/ROS2_workspace/src
git clone [https://github.com/lakshman-maker/ROS2-Multimodal-Teleop.git](https://github.com/lakshman-maker/ROS2-Multimodal-Teleop.git)

2. Download the MediaPipe AI Models:
Navigate to the root of your workspace and download the required Task files:
cd ~/ROS2_workspace
wget -O face_landmarker.task [https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task](https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task)
wget -O hand_landmarker.task [https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task)
(Note: Ensure the absolute paths in gaze_controller.py match your workspace directory).

3. Install Dependencies & Build:
pip install opencv-python mediapipe
colcon build --packages-select vision_driver
source install/setup.bash

🎮 How to Play
1. Launch the Gazebo Environment (Terminal 1):
ros2 launch ros_gz_sim_demos diff_drive.launch.xml

2. Run the Vision Controller (Terminal 2):
source install/setup.bash
ros2 run vision_driver gaze_controller

Controls
Speed (Hand Tracker): Hold up 1 to 5 fingers to the camera to set the speed from 1 m/s to 5 m/s.
Gas (Center): Look straight ahead into the camera to drive forward.
Steer (Left / Right): Look to the left or right edge of the screen to turn the vehicle.
Brake (Up): Look up toward the ceiling to stop the vehicle.
Reverse (Down): Look down at your keyboard to reverse.

👤 Author
Lakshman Shrestha
GitHub: @lakshman-maker

