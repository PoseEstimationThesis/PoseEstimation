from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QPixmap, QImage, QFont
from PySide6.QtCore import Qt
import cv2 as cv
from constants import VISIBILITY_THRESHOLD

class CameraWidget(QWidget):
    def __init__(self, camera_id):
        super().__init__()
        self.camera_id = camera_id
        self.camera_id = camera_id
        self.layout = QVBoxLayout(self)


        # Spacer label to push down the index label
        self.spacer_label = QLabel("")
        self.spacer_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Create a label to display the camera index
        self.index_label = QLabel(f"Camera {camera_id}")
        self.index_label.setAlignment(Qt.AlignCenter)
        self.index_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        
        font = QFont()
        font.setPointSize(12)  # Set the font size
        font.setBold(True)  # Make font bold
        self.index_label.setFont(font)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)  # Ensure the feed is centered
        self.image_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Add the labels to the layout with specific stretch factors
        # The higher the stretch value, the more space that widget will take up relative to others
        self.layout.addWidget(self.spacer_label, stretch=1)  # Lower stretch
        self.layout.addWidget(self.index_label)
        self.layout.addWidget(self.image_label, stretch=10)  # Higher stretch
        
        # Adjust layout spacing and margins
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(5, 1, 5, 5)

    def update_image(self, frame):
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.isVisible() and self.image_label.pixmap() is not None:
            # Rescale the pixmap when the widget is resized
            self.image_label.setPixmap(self.image_label.pixmap().scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio))

    def draw_landmarks(self, camera_id, landmarks, frame):
        if self.isVisible() and camera_id == self.camera_id:
            if landmarks is not None:
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

                for idx, landmark in enumerate(landmarks):
                    # Check if the landmark is part of the body
                    if idx in body_parts and landmark.visibility > VISIBILITY_THRESHOLD:
                        x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
                        part_name = body_parts[idx]
                        color = body_part_colors[part_name]
                        cv.circle(frame, (x, y), 5, color, -1)  # Draw a colored circle at each body landmark
                        cv.putText(frame, str(idx), (x, y), cv.FONT_HERSHEY_SIMPLEX, 1, color, 2)  # Display landmark number

                for connection in connections:
                    idx1, idx2 = connection
                    if idx1 in body_parts and idx2 in body_parts and landmarks[idx1].visibility > VISIBILITY_THRESHOLD and landmarks[idx2].visibility > VISIBILITY_THRESHOLD:
                        x1, y1 = int(landmarks[idx1].x * frame.shape[1]), int(landmarks[idx1].y * frame.shape[0])
                        x2, y2 = int(landmarks[idx2].x * frame.shape[1]), int(landmarks[idx2].y * frame.shape[0])
                        part_name = body_parts[idx1]
                        color = body_part_colors[part_name]
                        cv.line(frame, (x1, y1), (x2, y2), color, 5, lineType=cv.LINE_AA)
            self.update_image(frame)                

    def notify_camera_stopped(self, camera_id):
        if camera_id == self.camera_id:
            pass
            # print(f"Camera {camera_id} stopped.")
