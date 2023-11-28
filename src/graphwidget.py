import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import timedelta
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Signal
from logic.DataManager import shared_data_instance

class GraphWidget(QWidget):
    shown = Signal()
    hidden = Signal()

    def __init__(self, joint_name, show_legend=False):
        super().__init__()
        self.joint_name = joint_name
        self.show_legend = show_legend

        # Set up the matplotlib figure and canvas
        self.figure, self.ax = plt.subplots()

        self.ax.set_xlabel('Δt (seconds)')
        self.ax.set_ylabel('Angle')
        self.ax.set_title(f'{self.joint_name}')

        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Setup a QTimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_update)

        self.shown.connect(lambda: self.timer.start(200))
        self.hidden.connect(lambda: self.timer.stop())

        self.canvas.draw()

    def showEvent(self, event):
        super().showEvent(event)
        self.on_update()
        self.shown.emit()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.hidden.emit()

    def on_update(self):
        if self.isVisible() and shared_data_instance.record_data_running:
            self.ax.clear()

            window_size = 10  # amount of samples for rolling average
            threshold = 30  # Threshold for detecting outliers
            time_window = 5  # Time window in seconds for filtering data

            current_time = pd.to_datetime("now")

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

                    # Calculate time differences in seconds from current time
                    filtered_data['TimeDelta'] = (filtered_data['Timestamp'] - current_time).dt.total_seconds()
 
                    # Get the color for the device from the map
                    color = shared_data_instance.get_color_for_device(device_number)

                    # Apply rolling window and calculate the mean
                    filtered_data['Rolling'] = filtered_data['Angle'].rolling(window=window_size, min_periods=1).mean()

                    # Plot the rolling average
                    self.ax.plot(filtered_data['TimeDelta'], filtered_data['Rolling'], label=f'Device {device_number}', color=color)
                    
                    # Detect and plot outliers
                    outliers = filtered_data[np.abs(filtered_data['Angle'] - filtered_data['Rolling']) > threshold]
                    self.ax.scatter(outliers['TimeDelta'], outliers['Angle'], color=color, marker='o', s=5)

                    # Draw horizontal lines to the plot for each outlier
                    for index, outlier in outliers.iterrows():
                        rolling_value = filtered_data.loc[index, 'Rolling']
                        self.ax.plot([outlier['TimeDelta'], outlier['TimeDelta']], [outlier['Angle'], rolling_value], color=color, linestyle='--', linewidth=0.5)

            self.ax.set_xlabel('Δt (seconds)')
            self.ax.set_ylabel('Angle')
            self.ax.set_title(f'{self.joint_name}')
            self.ax.set_ylim(0, 360)
            if self.show_legend:
                self.ax.legend(loc='upper right')
            self.canvas.draw()
