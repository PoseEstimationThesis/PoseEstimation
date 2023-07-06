import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel


class BasicInterface():

    def initialize_interface(self):
        app = QApplication(sys.argv)
        label = QLabel("Hello World", alignment=Qt.AlignCenter)
        label.show()
        sys.exit(app.exec_())