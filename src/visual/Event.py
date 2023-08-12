from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Slot


class EventObject:

    @staticmethod
    @Slot()
    def printfunc(text):
        print(text)
