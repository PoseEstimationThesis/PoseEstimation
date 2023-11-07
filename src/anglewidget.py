from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer, QCoreApplication
from logic.DataManager import shared_data_instance

class AngleWidget(QWidget):
    def __init__(self, joint1, joint2, joint3):
        super().__init__()
        self.mJoint1 = joint1
        self.mJoint2 = joint2
        self.mJoint3 = joint3

        self.layout = QVBoxLayout(self)

        self.angle_label = QLabel("Angle: ")
        self.angle_label.setAlignment(Qt.AlignCenter)
        self.angle_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        font = QFont()
        font.setPointSize(12)  # Set the font size
        font.setBold(True)  # Make font bold
        self.angle_label.setFont(font)

        self.layout.addWidget(self.angle_label)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(5, 1, 5, 5)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.timer.start(1000)


    def update_angle(self):
        for key, data in shared_data_instance.angle_data.items():
            device_number, joint1, joint2, joint3 = key.split('_')
            if (self.mJoint1 == joint1 and self.mJoint2 == joint2 and self.mJoint3 == joint3):
                angle = data["angle"]
                angle_text = f"Angle (Device {device_number}): {angle:.2f} between joints: {joint1}, {joint2}, {joint3}"
                self.angle_label.setText(angle_text)


