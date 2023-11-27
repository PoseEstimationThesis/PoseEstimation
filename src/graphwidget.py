import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import timedelta
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Signal
from logic.DataManager import shared_data_instance

class GraphWidget(QWidget):
    shown = Signal()
    hidden = Signal()

    def __init__(self, joint_name):
        super().__init__()
        self.joint_name = joint_name
        # self.device_numbers = shared_data_instance.get_device_numbers()
        # print(self.device_numbers)

        # Set up the matplotlib figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.ax.set_xlabel('Timestamp')
        self.ax.set_ylabel('Angle')
        self.ax.set_title(f'{self.joint_name}')

        # Setup a QTimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_update)

        self.shown.connect(lambda: self.timer.start(200))
        self.hidden.connect(lambda: self.timer.stop())

    def showEvent(self, event):
        super().showEvent(event)
        self.shown.emit()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.hidden.emit()

    def on_update(self):
        if self.isVisible() and shared_data_instance.record_data_running:
            self.ax.clear()

            window_size = 10  # Window size for rolling average
            threshold = 15  # Threshold for detecting outliers
            time_window = 5  # Time window in seconds for filtering data

            for device_number in shared_data_instance.get_device_numbers():
                original_data = shared_data_instance.get_data(device_number, self.joint_name)
                if not original_data.empty:
                    # Convert 'Timestamp' to datetime and create a copy of the data
                    data = original_data.copy()
                    data['Timestamp'] = pd.to_datetime(data['Timestamp'])

                    # Filter for the last 5 seconds and create a copy to avoid SettingWithCopyWarning
                    latest_timestamp = data['Timestamp'].max()
                    start_time = latest_timestamp - timedelta(seconds=time_window)
                    filtered_data = data[data['Timestamp'] >= start_time].copy()
 
                    # Get the color for the device from the map
                    color = shared_data_instance.get_color_for_device(device_number)

                    # Apply rolling window and calculate the mean
                    filtered_data['Rolling'] = filtered_data['Angle'].rolling(window=window_size, min_periods=1).mean()

                    # Plot the rolling average
                    self.ax.plot(filtered_data['Timestamp'], filtered_data['Rolling'], label=f'Device {device_number}', color=color)

                    # Detect and plot outliers
                    # outliers = filtered_data[np.abs(filtered_data['Angle'] - filtered_data['Rolling']) > threshold]
                    # self.ax.scatter(outliers['Timestamp'], outliers['Angle'], color=color)

            self.ax.set_xlabel('Timestamp')
            self.ax.set_ylabel('Angle')
            self.ax.set_title(f'{self.joint_name}')
            self.ax.set_ylim(0, 360)
            # self.ax.legend()
            self.canvas.draw()
