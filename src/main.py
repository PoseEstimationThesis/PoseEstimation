from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget, QTabWidget, QGridLayout, QPushButton, \
    QFileDialog
from PySide6.QtCore import QThread, QSize, QCoreApplication
from logic.DataManager import shared_data_instance
from worker import FrameProcessor, Camera
from camerawidget import CameraWidget
from anglewidget import AngleWidget
from graphwidget import GraphWidget
from feature import JointDict
import sys


def discover_cameras():
    # Simple camera discovery
    cameras = []
    for i in range(10):
        cam = Camera(i)
        if cam.is_valid():
            cameras.append(cam)
    return cameras


class ApplicationManager:
    MAX_CAMERAS_PER_TAB = 4
    MAX_ANGLES_PER_TAB = 8
    MAX_GRAPHS_PER_TAB = 8

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.tab_widget = QTabWidget()

        # Create tabs for Cameras and Statistics
        self.camera_tab = QTabWidget()
        self.statistics_tab = QTabWidget()

        self.main_layout.addWidget(self.tab_widget)
        self.tab_widget.addTab(self.camera_tab, "Live Feeds")
        self.tab_widget.addTab(self.statistics_tab, "Statistics")

        self.frame_processors = []
        self.threads = []
        self.angle_widgets = []
        self.graph_widgets = []

        self.cameras = discover_cameras()
        self.setup_camera_tabs(self.cameras)

        self.setup_angle_tabs()
        self.setup_graph_tabs()

        self.main_widget.show()

    def setup_camera_tabs(self, cameras):
        grid = None
        for i, camera in enumerate(cameras):
            if i % self.MAX_CAMERAS_PER_TAB == 0:
                tab = QWidget()
                grid = QGridLayout(tab)
                self.camera_tab.addTab(tab, f"Cameras {i + 1}-{i + self.MAX_CAMERAS_PER_TAB}")
            cam_widget = CameraWidget(camera.camera_id)
            row = (i % self.MAX_CAMERAS_PER_TAB) // 2  # Change the divisor to adjust layout
            col = (i % self.MAX_CAMERAS_PER_TAB) % 2  # Change the modulus to adjust layout
            grid.addWidget(cam_widget, row, col)

            frame_processor = FrameProcessor(camera)
            thread = QThread()
            frame_processor.moveToThread(thread)

            thread.started.connect(frame_processor.start_processing)
            frame_processor.finished.connect(self.thread_cleanup(thread))
            frame_processor.frameProcessedSignal.connect(cam_widget.update_image)

            self.frame_processors.append(frame_processor)
            self.threads.append(thread)

            thread.start()

    def setup_angle_tabs(self):
        for camera in self.cameras:
            self.angle_widgets.append(
                AngleWidget(camera.camera_id, JointDict.shared_joint_dict.get_reverse({"11", "13", "15"})))
            self.angle_widgets.append(
                AngleWidget(camera.camera_id, JointDict.shared_joint_dict.get_reverse({"12", "14", "16"})))
        grid = None
        for i, angle_widget in enumerate(self.angle_widgets):
            if i % self.MAX_ANGLES_PER_TAB == 0:
                tab = QWidget()
                grid = QGridLayout(tab)
            row = (i % self.MAX_ANGLES_PER_TAB) // 2
            col = (i % self.MAX_ANGLES_PER_TAB) % 2
            grid.addWidget(angle_widget, row, col)
            self.statistics_tab.addTab(tab, f"Angles {i + 1}-{i + self.MAX_ANGLES_PER_TAB}")

            thread = QThread()
            angle_widget.moveToThread(thread)
            self.threads.append(thread)

        self.export_button = QPushButton("Export Data")
        self.export_button.clicked.connect(self.export_data)
        grid.addWidget(self.export_button)

    def setup_graph_tabs(self):
        for camera in self.cameras:
            self.graph_widgets.append(GraphWidget(camera.camera_id))

        grid = None
        for i, graph_widget in enumerate(self.graph_widgets):
            if i % self.MAX_GRAPHS_PER_TAB == 0:
                tab = QWidget()
                layout = QVBoxLayout(tab)
                grid = QGridLayout()
                layout.addLayout(grid)

            grid.addWidget(graph_widget, i % self.MAX_GRAPHS_PER_TAB, 0)

            if i % self.MAX_GRAPHS_PER_TAB == self.MAX_GRAPHS_PER_TAB - 1 or i == len(self.graph_widgets) - 1:
                self.statistics_tab.addTab(tab, f"Graphs {i - self.MAX_GRAPHS_PER_TAB + 2}-{i + 1}")

            thread = QThread()
            graph_widget.moveToThread(thread)
            self.threads.append(thread)

    def run(self):
        return self.app.exec()

    def thread_cleanup(self, thread):
        def cleanup():
            thread.quit()
            thread.wait()

        return cleanup

    def export_data(self):
        shared_data_instance.export_to_csv()
        print("Data exported to CSV file!")


if __name__ == '__main__':
    manager = ApplicationManager()
    sys.exit(manager.run())
