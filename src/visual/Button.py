from PySide6.QtWidgets import QPushButton


class ButtonObject:

    def __init__(self, text):
        self.text = text
        self.button = QPushButton(text)


    def onClick(self, func):
        self.button.clicked.connect(func)


    def show(self):
        self.button.show()

