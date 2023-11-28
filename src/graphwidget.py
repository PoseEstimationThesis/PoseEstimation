import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import timedelta
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator
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
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.window_size = 20 # In samples
        self.threshold = 20
        self.time_window = 25 # In seconds
        self.nth_point = 3

        # Set up axes, labels, and title
        self.ax.set_xlabel('Δt (seconds)')
        self.ax.set_ylabel('Angle')
        self.ax.set_title(f'{self.joint_name}')
        self.ax.set_ylim(-10, 190)
        self.ax.set_xlim(-self.time_window, 0)
        self.ax.yaxis.set_major_locator(MultipleLocator(20))

        # Set up the QTimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_update)
        self.shown.connect(lambda: self.timer.start(25))
        self.hidden.connect(lambda: self.timer.stop())

        self.canvas.draw()

    def on_update(self):
        if self.isVisible() and shared_data_instance.record_data_running:
            self.ax.clear()
            current_time = pd.to_datetime("now")

            for device_number in shared_data_instance.device_numbers:
                original_data = shared_data_instance.get_data(device_number, self.joint_name)
                if not original_data.empty:
                    # Convert 'Timestamp' to datetime and create a copy of the data
                    data = original_data.copy()
                    data['Timestamp'] = pd.to_datetime(data['Timestamp'])

                    # Filter for the last 5 seconds and create a copy to avoid SettingWithCopyWarning
                    latest_timestamp = data['Timestamp'].max()
                    start_time = latest_timestamp - timedelta(seconds=self.time_window)
                    filtered_data = data[data['Timestamp'] >= start_time].copy()

                    # Calculate time differences in seconds from current time
                    filtered_data['TimeDelta'] = (filtered_data['Timestamp'] - current_time).dt.total_seconds()
 
                    # Get the color for the device from the map
                    color = shared_data_instance.get_color_for_device(device_number)

                    # Apply rolling window and calculate the mean
                    filtered_data['Rolling'] = filtered_data['Angle'].rolling(window=self.window_size, min_periods=1).mean()

                    # Downsampling the data for plotting (plot every nth point)
                    downsampled_data = filtered_data.iloc[::self.nth_point, :]

                    # Plot the rolling average
                    self.ax.plot(downsampled_data['TimeDelta'], downsampled_data['Rolling'], label=f'Camera {device_number}', color=color)
                    
                    # Detect and plot outliers
                    outliers = filtered_data[np.abs(filtered_data['Angle'] - filtered_data['Rolling']) > self.threshold]
                    self.ax.scatter(outliers['TimeDelta'], outliers['Angle'], color=color, marker='o', s=(30/self.time_window))

                    # Draw horizontal lines to the plot for each outlier
                    for index, outlier in outliers.iterrows():
                        rolling_value = filtered_data.loc[index, 'Rolling']
                        self.ax.plot([outlier['TimeDelta'], outlier['TimeDelta']], [outlier['Angle'], rolling_value], color=color, linestyle='--', linewidth=(5/self.time_window))

                    # Update scatter plot data
                    outliers = filtered_data[np.abs(filtered_data['Angle'] - filtered_data['Rolling']) > self.threshold]
 
            self.ax.set_xlabel('Δt (seconds)')
            self.ax.set_ylabel('Angle')
            self.ax.set_title(f'{self.joint_name}')
            self.ax.set_ylim(-10, 190)
            self.ax.set_xlim(-self.time_window, 0)
            self.ax.yaxis.set_major_locator(MultipleLocator(20))
            if self.show_legend:
                self.ax.legend(loc='upper left')
            self.canvas.draw()

    def showEvent(self, event):
        super().showEvent(event)
        self.on_update()
        self.shown.emit()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.hidden.emit()
