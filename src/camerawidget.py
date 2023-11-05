from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QPixmap, QImage, QFont
from PySide6.QtCore import Qt

class CameraWidget(QWidget):
    def __init__(self, camera_index):
        super().__init__()
        self.camera_index = camera_index
        self.layout = QVBoxLayout(self)


        # Spacer label to push down the index label
        self.spacer_label = QLabel("")
        self.spacer_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Create a label to display the camera index
        self.index_label = QLabel(f"Camera {camera_index}")
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

    def update_image(self, frame, camera_index):
        if camera_index == self.camera_index:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio))
            print(f"Camera {camera_index}: Image updated.")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image_label.pixmap() is not None:
            # Rescale the pixmap when the widget is resized
            self.image_label.setPixmap(self.image_label.pixmap().scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio))

    def notify_camera_stopped(self, camera_index):
        if camera_index == self.camera_index:
            print(f"Camera {camera_index} stopped.")
