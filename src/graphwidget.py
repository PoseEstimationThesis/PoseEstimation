from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog
from PySide6.QtCore import QFile, QTextStream, QDateTime, QTimer
from PySide6.QtGui import QPainter
from datetime import datetime


class GraphWidget(QWidget):
    def __init__(self, camera_id):
        super().__init__()
        self.camera_id = camera_id
        self.layout = QVBoxLayout(self)

        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.load_button = QPushButton(f"Load Data for {self.camera_id} ", self)
        self.load_button.clicked.connect(self.load_data)
        self.layout.addWidget(self.load_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(1000)

    def load_data(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(None, "Load Data File", "", "CSV Files (*.csv);;All Files (*)",
                                                   options=options)
        data_file = QFile(file_name)
        if not data_file.open(QFile.ReadOnly | QFile.Text):
            print("Failed to open file:", file_name)
            return

        stream = QTextStream(data_file)
        header_line = stream.readLine()  # Skip the header line

        timestamps = []
        angles = []
        min_timestamp = None
        while not stream.atEnd():
            line = stream.readLine()
            values = line.split(',')
            if len(values) >= 3:
                timestamp_str = values[0]
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
                timestamps.append(timestamp)

                # Check for non-header lines
                if values[1].isdigit():  # Validate if the value is a number before conversion
                    device_number = int(values[1])
                    if self.camera_id == device_number:
                        try:
                            angle = float(values[2]) if values[2] else None
                            if angle is not None:
                                angles.append(angle)
                            else:
                                angles.append(0)
                        except ValueError as e:
                            print(f"Error processing line {line}: {e}")

        data_file.close()
        # Calculate timestamps in seconds from the epoch
        timestamps_seconds_from_epoch = [(timestamp - min(timestamps)).total_seconds()
                                         for timestamp in timestamps]

        # Use x-values against timestamps in seconds for plotting
        self.ax.plot(timestamps_seconds_from_epoch, angles)  # Change marker type if needed
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Angle')
        self.ax.set_title(f"CSV Data Chart for Device: {self.camera_id}")
        self.ax.set_xlim(0, max(timestamps_seconds_from_epoch))  # Start from zero based on lowest timestamp
        # Adjust y-axis limits according to your angles if needed
        self.canvas.draw()


    def update_graph(self):
        self.canvas.draw()
