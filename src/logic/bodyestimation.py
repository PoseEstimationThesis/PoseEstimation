from datetime import datetime
from logic.datamanager import shared_data_instance
import mediapipe as mp
import numpy as np
from constants import VISIBILITY_THRESHOLD, DETECTION_CONFIDENCE, TRACKING_CONFIDENCE

class BodyEstimator:
    def __init__(self, camera_id):
        self.camera_id = camera_id
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(model_complexity=1,
                            static_image_mode=False,
                            min_detection_confidence=DETECTION_CONFIDENCE,
                            min_tracking_confidence=TRACKING_CONFIDENCE,
                            smooth_landmarks=True)
        self.landmarks = None
        self.world_landmarks = None
        self.frame = None

    def estimate_body(self, frame):
        self.frame = frame
        results = self.pose.process(frame)
        if results.pose_world_landmarks and results.pose_landmarks:
            self.landmarks = results.pose_landmarks.landmark
            self.world_landmarks = results.pose_world_landmarks.landmark
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            landmark_data = self.get_landmark_data(self.landmarks, self.camera_id, timestamp)
            shared_data_instance.set_landmark_data(landmark_data)

            world_landmark_data = self.get_landmark_data(self.world_landmarks, self.camera_id, timestamp)
            shared_data_instance.set_world_landmark_data(world_landmark_data)

    def get_landmark_data(self, landmarks, device_number, timestamp):
        landmark_data = {}
        for idx, landmark in enumerate(landmarks):
            key = (device_number, timestamp, idx)
            landmark_data[key] = {
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            }
        return landmark_data
