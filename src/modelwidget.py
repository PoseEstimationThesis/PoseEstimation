import matplotlib.pyplot as plt
import numpy as np
import mediapipe as mp
import pandas as pd
# import datetime
# import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Signal
from logic.DataManager import shared_data_instance
from mpl_toolkits.mplot3d import Axes3D
from constants import VISIBILITY_THRESHOLD, CONNECTIONS, BODY_PARTS_NAME, BODY_PARTS_COLORS, LANDMARK_COLOR

class ModelWidget(QWidget):
    shown = Signal()
    hidden = Signal()

    def __init__(self, camera_id):
        super().__init__()
        self.mp_pose = mp.solutions.pose
        self.camera_id = camera_id
        self.figure = plt.figure()
        self.figure.tight_layout()
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.scale_level = 1

        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_zlim(-1, 1)

        # matplotlib expects its colors to be nomalized in range [0,1]
        self.landmark_color_normalized = color_normalized = tuple(c/255 for c in LANDMARK_COLOR)

        # Set up the QTimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_update)
        self.shown.connect(lambda: self.timer.start(50))
        self.hidden.connect(lambda: self.timer.stop())

        self.canvas.draw()

    def on_update(self):
        if self.isVisible():
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            zlim = self.ax.get_zlim()
            self.ax.clear()
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
            self.ax.set_zlim(zlim)
            self.scale_level = self.calculate_zoom(xlim, ylim, zlim)
            
            # Dataframe could be empty if just cleared by pressing "Run"
            try:
                camera_data = shared_data_instance.world_landmark_data.xs(self.camera_id, level='Device Number')
            except:
                pass
            if not camera_data.empty:
                # Get the latest timestamp's data
                latest_timestamp = camera_data.index.get_level_values('Timestamp').max()
                filtered_data = camera_data.xs(latest_timestamp, level='Timestamp')

                # Check if there are landmarks for this timestamp
                if not filtered_data.empty:
                    self.figure.tight_layout()
                    self.plot_landmarks(filtered_data, self.ax)
                    self.canvas.draw()


    def plot_landmarks(self, filtered_data, ax):
        visible_landmarks = filtered_data[filtered_data['visibility'] > VISIBILITY_THRESHOLD]
        xs = visible_landmarks['x'].tolist()
        zs = [-y for y in visible_landmarks['y'].tolist()]  # Swapped Z (previously Y)
        ys = visible_landmarks['z'].tolist()  # Swapped and inverted Y (previously Z)

        # Plot connections between landmarks
        for connection in CONNECTIONS:
            start_idx, end_idx = connection
            start_joint = f'world_landmark_{start_idx}'
            end_joint = f'world_landmark_{end_idx}'

            if start_joint in visible_landmarks.index.get_level_values('Joint ID') and end_joint in visible_landmarks.index.get_level_values('Joint ID'):
                start_landmark = visible_landmarks.loc[start_joint]
                end_landmark = visible_landmarks.loc[end_joint]

                if start_landmark['visibility'] > VISIBILITY_THRESHOLD and end_landmark['visibility'] > VISIBILITY_THRESHOLD:
                    part_name = BODY_PARTS_NAME.get(end_idx, None)
                    color = BODY_PARTS_COLORS.get(part_name)  # default to white if part name not found
                    color_normalized = tuple(c/255 for c in color)  # Normalize color for Matplotlib
                    ax.plot([start_landmark['x'], end_landmark['x']], 
                            [start_landmark['z'], end_landmark['z']],  # Swapped and inverted Z (previously Y)
                            [-start_landmark['y'], -end_landmark['y']],  # Swapped Y (previously Z)
                            color=color_normalized, marker='o',linewidth = 0.05 * self.scale_level)

        ax.scatter(xs, ys, zs, color=self.landmark_color_normalized, marker='o', s = 0.5 * self.scale_level)

        ax.set_xlabel('X Axis')
        ax.set_ylabel('Z Axis')
        ax.set_zlabel('Y Axis')

    def calculate_zoom(self, xlim, ylim, zlim):
        xrange = abs(xlim[1] - xlim[0])
        yrange = abs(ylim[1] - ylim[0])
        zrange = abs(zlim[1] - zlim[0])

        size = 100 / max(xrange, yrange, zrange)
        return size

    def showEvent(self, event):
        super().showEvent(event)
        self.on_update()
        self.shown.emit()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.hidden.emit()
