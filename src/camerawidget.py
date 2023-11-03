from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt

class CameraWidget(QWidget):
    def __init__(self, camera_index):
        super().__init__()
        self.camera_index = camera_index
        self.layout = QVBoxLayout(self)
        self.image_label = QLabel(self)
        self.layout.addWidget(self.image_label)

    def update_image(self, frame, camera_index):
        if camera_index == self.camera_index:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
            print(f"Camera {camera_index}: Image updated.")

    def notify_camera_stopped(self, camera_index):
        if camera_index == self.camera_index:
            # Handle camera stopped event, perhaps display a message or close the widget
            print(f"Camera {camera_index} stopped.")
