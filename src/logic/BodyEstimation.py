from logic.AngleCalculator import AngleCalculator
from logic.DataManager import shared_data_instance
from feature import JointDict
import mediapipe as mp
import cv2 as cv


class BodyEstimator:
    def __init__(self, camera_id):
        self.camera_id = camera_id
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.landmarks = None
        self.frame = None
        self.angle_calculator = AngleCalculator()

    def estimate_body(self, frame):
        # Convert the frame to RGB format if needed
        # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.frame = frame
        results = self.pose.process(frame)
        if results.pose_landmarks:
            self.landmarks = results.pose_landmarks.landmark
        else:
            return 0

    def draw_landmarks(self):
        if self.landmarks is not None:
            connections = [
                (11, 12), (12, 24), (11, 23), # Torso
                (13, 11), (13, 15), (15, 17), # Left Arm
                (14, 12), (14, 16), (16, 18), # Right Arm
                (25, 23), (25, 27), (27, 29), # Left Leg 
                (26, 24), (26, 28), (28, 30)  # Right Leg
            ]

            body_parts = {
                11: "Torso", 12: "Torso", 23: "Torso", 24: "Torso",
                13: "Left Arm", 15: "Left Arm", 17: "Left Arm",
                14: "Right Arm" ,16: "Right Arm", 18: "Right Arm",
                25: "Left Leg", 27: "Left Leg", 29: "Left Leg",
                26: "Right Leg", 28: "Right Leg", 30: "Right Leg"
            }

            body_part_colors = {
                "Torso": (255, 0, 0),  # Red
                "Right Arm": (255, 128, 0),  # Orange
                "Right Leg": (255, 255, 0),  # Yellow
                "Left Arm": (255, 0, 255),  # Magenta
                "Left Leg": (0, 0, 255)  # Blue
            }

            for idx, landmark in enumerate(self.landmarks):
                # Check if the landmark is part of the body
                if idx in body_parts:
                    x, y = int(landmark.x * self.frame.shape[1]), int(landmark.y * self.frame.shape[0])
                    part_name = body_parts[idx]
                    color = body_part_colors[part_name]
                    cv.circle(self.frame, (x, y), 5, color, -1)  # Draw a colored circle at each body landmark
                    cv.putText(self.frame, str(idx), (x, y), cv.FONT_HERSHEY_SIMPLEX, 1, color, 2)  # Display landmark number

            for connection in connections:
                idx1, idx2 = connection
                if idx1 in body_parts and idx2 in body_parts:
                    x1, y1 = int(self.landmarks[idx1].x * self.frame.shape[1]), int(self.landmarks[idx1].y * self.frame.shape[0])
                    x2, y2 = int(self.landmarks[idx2].x * self.frame.shape[1]), int(self.landmarks[idx2].y * self.frame.shape[0])
                    part_name = body_parts[idx1]
                    color = body_part_colors[part_name]
                    cv.line(self.frame, (x1, y1), (x2, y2), color, 5, lineType=cv.LINE_AA)

    def calculate_all(self):
        self.left_elbow = self.angle_calculator.calculate_joint_angle_left(self.landmarks, 11, 13, 15)
        shared_data_instance.set_data(self.camera_id, JointDict.shared_joint_dict.get_reverse({"11", "13", "15"}), self.left_elbow)
        self.right_elbow = self.angle_calculator.calculate_joint_angle_right(self.landmarks, 12, 14, 16)
        shared_data_instance.set_data(self.camera_id, JointDict.shared_joint_dict.get_reverse({"12", "14", "16"}), self.right_elbow)
        self.left_knee = self.angle_calculator.calculate_joint_angle_left(self.landmarks, 23, 25, 27)
        shared_data_instance.set_data(self.camera_id, JointDict.shared_joint_dict.get_reverse({"23", "25", "27"}), self.left_knee)
        self.right_knee = self.angle_calculator.calculate_joint_angle_right(self.landmarks, 24, 26, 28)
        shared_data_instance.set_data(self.camera_id, JointDict.shared_joint_dict.get_reverse({"24", "26", "28"}), self.right_knee)
