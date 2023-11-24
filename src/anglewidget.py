from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer, QCoreApplication
from logic.DataManager import shared_data_instance

class AngleWidget(QWidget):
    def __init__(self, camera_id, joint_name):
        super().__init__()
        self.joint_name = joint_name
        self.camera_id = camera_id

        self.layout = QVBoxLayout(self)

        self.angle_label = QLabel("Angle: ")
        self.angle_label.setAlignment(Qt.AlignCenter)
        self.angle_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        font = QFont()
        font.setPointSize(12)  # Set the font size
        font.setBold(True)  # Make font bold
        self.angle_label.setFont(font)

        self.setStyleSheet("background-color: #54939C; border-radius: 5px;")

        self.layout.addWidget(self.angle_label)
        self.layout.setContentsMargins(10, 10, 10, 10)

        self.layout.addWidget(self.angle_label)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(5, 1, 5, 5)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.timer.start(1)


    def update_angle(self):
        data = shared_data_instance.get_data(self.camera_id, self.joint_name)
        if data is not None:
            angle = data
            angle_text = f"Angle (Device {self.camera_id}): {angle:.2f} for joint: {self.joint_name}"
            self.angle_label.setText(angle_text)



