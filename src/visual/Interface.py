import sys
from PySide6.QtCore import Qt
from src.visual.Button import ButtonObject
from src.visual.Event import EventObject

from PySide6.QtWidgets import QApplication, QLabel


class BasicInterface:

    @staticmethod
    def initialize_interface():
        app = QApplication(sys.argv)
        label = QLabel("Hello World", alignment=Qt.AlignCenter)
        label.show()
        button = ButtonObject("Piwo")
        text = "123"
        button.onClick(EventObject.printfunc(text))
        button.show()
        sys.exit(app.exec())

