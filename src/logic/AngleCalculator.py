import numpy as np


class AngleCalculator:
    def __init__(self):
        pass

    def calculate_joint_angle_left(self, landmarks, joint1, joint2, joint3):
        if landmarks is None:
            return None

        print(f"1 JOINT: {landmarks[joint1].visibility}\n")
        print(f"2 JOINT: {landmarks[joint2].visibility}\n")
        print(f"3 JOINT: {landmarks[joint3].visibility}\n")
        if (landmarks[joint1].visibility > 0.5
                and landmarks[joint2].visibility > 0.5
                and landmarks[joint3].visibility > 0.5):
            x1, y1 = landmarks[joint1].x, landmarks[joint1].y
            x2, y2 = landmarks[joint2].x, landmarks[joint2].y
            x3, y3 = landmarks[joint3].x, landmarks[joint3].y

            angle = np.degrees(np.arctan2(y3 - y2, x3 - x2) - np.arctan2(y1 - y2, x1 - x2))
            angle = (angle + 360) % 360
            return angle
        else:
            return 0.0

    def calculate_joint_angle_right(self, landmarks, joint1, joint2, joint3):
        if landmarks is None:
            return None

        if (landmarks[joint1].visibility > 0.5
                and landmarks[joint2].visibility > 0.5
                and landmarks[joint3].visibility > 0.5):
            x1, y1 = landmarks[joint1].x, landmarks[joint1].y
            x2, y2 = landmarks[joint2].x, landmarks[joint2].y
            x3, y3 = landmarks[joint3].x, landmarks[joint3].y

            angle = np.degrees(np.arctan2(y3 - y2, x3 - x2) - np.arctan2(y1 - y2, x1 - x2))
            angle = abs(angle)

            return angle
        else:
            return None
