import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import timedelta
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Signal
from logic.datamanager import shared_data_instance
from constants import JOINTS_ANGLES_TO_CALCULATE

class GraphWidget(QWidget):
    def __init__(self, joint_name, show_legend=False, is_world=False):
        super().__init__()
        self.joint_name = joint_name
        self.show_legend = show_legend
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.is_world = is_world
        if self.is_world:
            self.widget_title = 'world_landmarks 'f'{self.joint_name}'
        else:
            self.widget_title = 'landmarks 'f'{self.joint_name}'
        self.window_size = 20 # In samples
        self.threshold = 20
        self.time_window = 25 # In seconds
        self.nth_point = 3

        # Set up axes, labels, and title
        self.ax.set_xlabel('Δt (seconds)')
        self.ax.set_ylabel('Angle')
        self.ax.set_title(self.widget_title)
        self.ax.set_ylim(-10, 190)
        self.ax.set_xlim(-self.time_window, 0)
        self.ax.yaxis.set_major_locator(MultipleLocator(20))


        shared_data_instance.angles_updated.connect(self.update_graph)

        # # Set up the QTimer
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.on_update)
        # self.shown.connect(lambda: self.timer.start(25))
        # self.hidden.connect(lambda: self.timer.stop())

        self.canvas.draw()

    def update_graph(self, in_data):
        if self.is_world:
            angles_df = in_data['world_landmark_angles']
        else:
            angles_df = in_data['landmark_angles']
        angles_df = angles_df[angles_df['Joint Pair'] == self.joint_name]
        # world_angles_df = in_data['world_landmark_angles']
        # world_angles_df = world_angles_df[world_angles_df['Joint Pair'] == self.joint_name]
        
        # Convert Timestamps to datetime objects for plotting
        angles_df['Timestamp'] = pd.to_datetime(angles_df['Timestamp'])

        # Clear previous plot
        self.ax.clear()

        # Set up axes, labels, and title
        self.ax.set_xlabel('Timestamp')
        self.ax.set_ylabel('Angle')
        self.ax.set_title(self.widget_title)
        self.ax.set_ylim(-10, 190)
        self.ax.grid(True)

        # Get unique device numbers
        device_numbers = angles_df['Device Number'].unique()

        # Plot data for each device number
        for device_number in device_numbers:
            df_subset = angles_df[angles_df['Device Number'] == device_number]
            self.ax.plot(df_subset['Timestamp'], df_subset['Angle'], label=f'Device {device_number}')

        # Show legend if required
        if self.show_legend:
            self.ax.legend()

        # Redraw the canvas
        self.canvas.draw()
