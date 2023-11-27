import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QWidget, QVBoxLayout
import pandas as pd
from logic.DataManager import shared_data_instance

class GraphWidget(QWidget):
    def __init__(self, joint_name):
        super().__init__()
        self.joint_name = joint_name
        # self.data_manager = data_manager

        # Set up the matplotlib figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        
        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Plot the data
        self.plot_data()

    def plot_data(self):
        # Filter data for the specific joint
        data = shared_data_instance.data
        joint_data = data[data['Joint Name'] == self.joint_name]

        # Group by device number and plot each as a separate line
        for device_number, group in joint_data.groupby('Device Number'):
            # Convert timestamps to a plottable format
            timestamps = pd.to_datetime(group['Timestamp'])
            angles = group['Angle']

            self.ax.plot(timestamps, angles, label=f'Device {device_number}')

        # Set labels and legend
        self.ax.set_xlabel('Timestamp')
        self.ax.set_ylabel('Angle')
        self.ax.set_title(f'Angles over Time for {self.joint_name}')
        self.ax.legend()

        # Redraw the canvas
        self.canvas.draw()
