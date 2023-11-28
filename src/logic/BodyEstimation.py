from logic.AngleCalculator import AngleCalculator
from logic.DataManager import shared_data_instance
from feature import JointDict
import mediapipe as mp
# import cv2 as cv
from constants import VISIBILITY_THRESHOLD, DETECTION_CONFIDENCE, TRACKING_CONFIDENCE

class BodyEstimator:
    def __init__(self, camera_id):
        self.camera_id = camera_id
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(model_complexity=0,
                            static_image_mode=False,
                            min_detection_confidence=DETECTION_CONFIDENCE,
                            min_tracking_confidence=TRACKING_CONFIDENCE,
                            smooth_landmarks=True)
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
            return None

    def calculate_all(self):
        # pass
        self.left_elbow = self.angle_calculator.calculate_joint_angle_left(self.landmarks, 11, 13, 15)
        shared_data_instance.set_data(self.camera_id, JointDict.shared_joint_dict.get_reverse({"11", "13", "15"}), self.left_elbow)
        self.right_elbow = self.angle_calculator.calculate_joint_angle_right(self.landmarks, 12, 14, 16)
        shared_data_instance.set_data(self.camera_id, JointDict.shared_joint_dict.get_reverse({"12", "14", "16"}), self.right_elbow)
        self.left_knee = self.angle_calculator.calculate_joint_angle_left(self.landmarks, 23, 25, 27)
        shared_data_instance.set_data(self.camera_id, JointDict.shared_joint_dict.get_reverse({"23", "25", "27"}), self.left_knee)
        self.right_knee = self.angle_calculator.calculate_joint_angle_right(self.landmarks, 24, 26, 28)
        shared_data_instance.set_data(self.camera_id, JointDict.shared_joint_dict.get_reverse({"24", "26", "28"}), self.right_knee)
