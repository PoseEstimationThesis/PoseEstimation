import numpy as np
from constants import VISIBILITY_THRESHOLD

class AngleCalculator:
    def __init__(self):
        pass

    def calculate_joint_angle_left(self, landmarks, joint1, joint2, joint3):
        if landmarks is None:
            return None

        if (landmarks[joint1].visibility > VISIBILITY_THRESHOLD
                and landmarks[joint2].visibility > VISIBILITY_THRESHOLD
                and landmarks[joint3].visibility > VISIBILITY_THRESHOLD):
            x1, y1 = landmarks[joint1].x, landmarks[joint1].y
            x2, y2 = landmarks[joint2].x, landmarks[joint2].y
            x3, y3 = landmarks[joint3].x, landmarks[joint3].y

            angle = np.degrees(np.arctan2(y3 - y2, x3 - x2) - np.arctan2(y1 - y2, x1 - x2))
            angle = (angle + 360) % 360
            return abs(angle - 180)
        else:
            return None

    def calculate_joint_angle_right(self, landmarks, joint1, joint2, joint3):
        if landmarks is None:
            return None

        if (landmarks[joint1].visibility > VISIBILITY_THRESHOLD
                and landmarks[joint2].visibility > VISIBILITY_THRESHOLD
                and landmarks[joint3].visibility > VISIBILITY_THRESHOLD):
            x1, y1 = landmarks[joint1].x, landmarks[joint1].y
            x2, y2 = landmarks[joint2].x, landmarks[joint2].y
            x3, y3 = landmarks[joint3].x, landmarks[joint3].y

            angle = np.degrees(np.arctan2(y3 - y2, x3 - x2) - np.arctan2(y1 - y2, x1 - x2))
            angle = abs(angle)

            return abs(angle - 180)
        else:
            return None
