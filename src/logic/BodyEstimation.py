import mediapipe as mp
import cv2 as cv

class BodyEstimator:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.landmarks = None
        self.frame = None

    def estimate_body(self, frame):
        # Convert the frame to RGB format if needed
        # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.frame = frame
        results = self.pose.process(frame)
        if results.pose_landmarks:
            self.landmarks = results.pose_landmarks.landmark
        else:
            return None

    def draw_landmarks(self):
        if self.landmarks is not None:
            connections = [
                    (11, 12), (12, 24), (11, 23),  # Head
                    (11, 13), (12, 14),  # Neck and spine
                    (13, 15), (14, 16),  # Upper arms
                    (15, 17), (16, 18),  # Forearms
                    (23, 25), (24, 26),  # Hips
                    (25, 27), (26, 28),  # Thighs
                    (27, 29), (28, 30)  # Lower legs
                ]

            for idx, landmark in enumerate(self.landmarks):
                    # Check if the landmark is part of the body
                    if idx in [11, 12, 23, 24, 13, 14, 15, 16, 17, 18, 25, 26, 27, 28, 29, 30]:
                        x, y = int(landmark.x * self.frame.shape[1]), int(landmark.y * self.frame.shape[0])
                        cv.circle(self.frame, (x, y), 5, (0, 0, 255), -1)  # Draw a red circle at each body landmark
                        cv.putText(self.frame, str(idx), (x, y), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                                   1)  # Display landmark number

            for connection in connections:
                    point1 = self.landmarks[connection[0]]
                    point2 = self.landmarks[connection[1]]
                    x1, y1 = int(point1.x * self.frame.shape[1]), int(point1.y * self.frame.shape[0])
                    x2, y2 = int(point2.x * self.frame.shape[1]), int(point2.y * self.frame.shape[0])
                    cv.line(self.frame, (x1, y1), (x2, y2), (0, 0, 255), 5)  # Draw lines in red
