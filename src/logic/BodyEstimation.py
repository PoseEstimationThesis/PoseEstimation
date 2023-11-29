# from logic.AngleCalculator import AngleCalculator
# from feature import JointDict
from datetime import datetime
from logic.DataManager import shared_data_instance
import mediapipe as mp
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
        self.world_landmarks = None
        self.frame = None
        # self.angle_calculator = AngleCalculator()

    def estimate_body(self, frame):
        self.frame = frame
        results = self.pose.process(frame)
        if results.pose_world_landmarks and results.pose_landmarks:
            self.landmarks = results.pose_landmarks.landmark
            landmark_data = self.get_landmark_data(self.landmarks, self.camera_id, 'landmark')
            shared_data_instance.set_landmark_data(landmark_data)

            self.world_landmarks = results.pose_world_landmarks.landmark
            world_landmark_data = self.get_landmark_data(self.world_landmarks, self.camera_id, 'world_landmark')
            shared_data_instance.set_world_landmark_data(world_landmark_data)

    def get_landmark_data(self, landmarks, device_number, prefix='landmark'):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        landmark_data = {}
        for idx, landmark in enumerate(landmarks):
            key = (device_number, timestamp, f'{prefix}_{idx}')
            landmark_data[key] = {
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            }
        return landmark_data

    def calculate_all(self):
        pass
        # self.left_elbow = self.angle_calculator.calculate_joint_angle_left(self.landmarks, 11, 13, 15)
        # shared_data_instance.set_data(self.camera_id, JointDict.shared_joint_dict.get_reverse({"11", "13", "15"}), self.left_elbow)
        # self.right_elbow = self.angle_calculator.calculate_joint_angle_right(self.landmarks, 12, 14, 16)
        # shared_data_instance.set_data(self.camera_id, JointDict.shared_joint_dict.get_reverse({"12", "14", "16"}), self.right_elbow)
        # self.left_knee = self.angle_calculator.calculate_joint_angle_left(self.landmarks, 23, 25, 27)
        # shared_data_instance.set_data(self.camera_id, JointDict.shared_joint_dict.get_reverse({"23", "25", "27"}), self.left_knee)
        # self.right_knee = self.angle_calculator.calculate_joint_angle_right(self.landmarks, 24, 26, 28)
        # shared_data_instance.set_data(self.camera_id, JointDict.shared_joint_dict.get_reverse({"24", "26", "28"}), self.right_knee)
