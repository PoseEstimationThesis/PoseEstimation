from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QPixmap, QImage, QFont
from PySide6.QtCore import Qt
import cv2 as cv
from constants import VISIBILITY_THRESHOLD, CONNECTIONS, BODY_PARTS_NAME, BODY_PARTS_COLORS, LANDMARK_COLOR

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

        self.standard_width, self.standard_height = 1920, 1080  # Standard dimensions for calculating scaling

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

                scaling_factor = min(frame.shape[1] / self.standard_width, frame.shape[0] / self.standard_height)

                for connection in CONNECTIONS:
                    idx1, idx2 = connection
                    if idx1 in BODY_PARTS_NAME and idx2 in BODY_PARTS_NAME and landmarks[idx1].visibility > VISIBILITY_THRESHOLD and landmarks[idx2].visibility > VISIBILITY_THRESHOLD:
                        x1, y1 = int(landmarks[idx1].x * frame.shape[1]), int(landmarks[idx1].y * frame.shape[0])
                        x2, y2 = int(landmarks[idx2].x * frame.shape[1]), int(landmarks[idx2].y * frame.shape[0])
                        part_name = BODY_PARTS_NAME[idx2]
                        color = BODY_PARTS_COLORS[part_name]
                        cv.line(frame, (x1, y1), (x2, y2), color, int(10 * scaling_factor), lineType=cv.LINE_AA)

                for idx, landmark in enumerate(landmarks):
                    # Check if the landmark is part of the body
                    if idx in BODY_PARTS_NAME and landmark.visibility > VISIBILITY_THRESHOLD:
                        x, y, z = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0]), landmark.z
                        if 0 <= x < frame.shape[1] and 0 <= y < frame.shape[0]:
                            part_name = BODY_PARTS_NAME[idx]
                            outline_color = BODY_PARTS_COLORS[part_name]

                            normalized_z = max(min(z, 1), -1)

                            # Blend towards white for negative z (closer), towards black for positive z (further)
                            if normalized_z < 0:
                                blended_color = [int(c + (255 - c) * -normalized_z) for c in LANDMARK_COLOR]
                            else:
                                blended_color = [int(c * (1 - normalized_z)) for c in LANDMARK_COLOR]

                            # Draw the circle with the blended color

                            cv.circle(frame, (x, y), int(15 * scaling_factor), outline_color, -1)
                            cv.circle(frame, (x,y), int(13 * scaling_factor), blended_color, -1)
                            # cv.putText(frame, str(idx), (x, y), cv.FONT_HERSHEY_SIMPLEX, 1, outline_color, 2)  # Display landmark number
            self.update_image(frame)                
