from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QTabWidget, QGridLayout, QPushButton
from PySide6.QtCore import QThread
from logic.datamanager import shared_data_instance
from logic.worker import Camera
from gui.camerawidget import CameraWidget
from gui.graphwidget import GraphWidget
from gui.modelwidget import ModelWidget
import sys
from constants import MAX_CAMERAS_PER_TAB, MAX_GRAPHS_PER_TAB, MAX_MODELS_PER_TAB, JOINTS_ANGLES_TO_CALCULATE

def discover_cameras():
    """
    Scans for available camera devices and re-indexes them sequentially.
    """
    cameras = []
    camera_ids = []
    camera_id_counter = 1
    for i in range(0,50):
        cam = Camera(i)
        if cam.is_valid():
            cam.create_id(camera_id_counter)
            cameras.append(cam)
            camera_ids.append(camera_id_counter)
            camera_id_counter += 1
        else:
            del cam
    return cameras, camera_ids

class ApplicationManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.tab_widget = QTabWidget()

        # Create tabs for Cameras and Statistics
        self.camera_tab = QTabWidget()
        self.statistics_tab = QTabWidget()
        self.models_tab = QTabWidget()

        self.main_layout.addWidget(self.tab_widget)
        self.tab_widget.addTab(self.camera_tab, "Live Feed")
        self.tab_widget.addTab(self.statistics_tab, "Statistics")
        self.tab_widget.addTab(self.models_tab, "3D model")

        self.data_record_button = QPushButton("Run")
        self.data_record_button.clicked.connect(shared_data_instance.switch_recording_data)
        self.main_layout.addWidget(self.data_record_button)
        
        shared_data_instance.set_update_button_text_callback(self.update_button_text)
        shared_data_instance.record_data_running = False

        self.threads = []
        self.angle_widgets = []
        self.graph_widgets = []
        self.model_widgets = []

        self.cameras, shared_data_instance.device_numbers = discover_cameras()
        self.setup_camera_tabs(self.cameras)

        # self.setup_angle_tabs()
        self.setup_graph_tabs()
        self.setup_model_tabs()

        self.main_widget.show()

    def update_button_text(self, text):
        self.data_record_button.setText(text)
    
    def setup_camera_tabs(self, cameras):
        grid = None
        for i, camera in enumerate(cameras):
            if i % MAX_CAMERAS_PER_TAB == 0:
                tab = QWidget()
                grid = QGridLayout(tab)
                if MAX_CAMERAS_PER_TAB > len(self.cameras):
                    self.camera_tab.addTab(tab, f"Cameras {i + 1}-{len(self.cameras)}")
                else:
                    self.camera_tab.addTab(tab, f"Cameras {i + 1}-{i + MAX_CAMERAS_PER_TAB}")
            cam_widget = CameraWidget(camera.camera_id)
            row = (i % MAX_CAMERAS_PER_TAB) // 2  # Change the divisor to adjust layout
            col = (i % MAX_CAMERAS_PER_TAB) % 2  # Change the modulus to adjust layout
            grid.addWidget(cam_widget, row, col)

            thread = QThread()
            camera.moveToThread(thread)

            thread.started.connect(camera.start_processing)
            camera.finished.connect(self.thread_cleanup(thread))
            camera.frameProcessedSignal.connect(cam_widget.draw_landmarks)

            self.threads.append(thread)

            thread.start()
            thread.setPriority(QThread.HighPriority)

    def setup_graph_tabs(self):
        joints = list(JOINTS_ANGLES_TO_CALCULATE.keys())
        for i, key in enumerate(joints):
            # Create a new tab for each key
            tab = QWidget()
            grid = QGridLayout(tab)
            self.statistics_tab.addTab(tab, f"Graph - {key}")

            # Create two GraphWidgets for each key: one for world and one for non-world
            for n in range(2):
                is_world = n == 1
                show_legend = n == 0
                graph_widget = GraphWidget(key, show_legend, is_world)
                self.graph_widgets.append(graph_widget)

                # Position the widget in the grid: two rows, one column
                grid.addWidget(graph_widget, n, 0)  # Row `n`, column 0

                # Move the widget to a new thread
                thread = QThread()
                graph_widget.moveToThread(thread)
                self.threads.append(thread)

    def setup_model_tabs(self):
        tab_index = 0
        for i, camera in enumerate(self.cameras):
            model_widget = ModelWidget(camera.camera_id)
            self.model_widgets.append(model_widget)

            if i % MAX_MODELS_PER_TAB == 0:
                tab = QWidget()
                grid = QGridLayout(tab)
                self.models_tab.addTab(tab, f"Model {tab_index * MAX_MODELS_PER_TAB + 1}")
                tab_index += 1

            row = (i % MAX_MODELS_PER_TAB) // 2
            col = (i % MAX_MODELS_PER_TAB) % 2

            grid.addWidget(model_widget, row, col)

            thread = QThread()
            model_widget.moveToThread(thread)
            self.threads.append(thread)

    def run(self):
        return self.app.exec()

    def thread_cleanup(self, thread):
        def cleanup():
            thread.quit()
            thread.wait()

        return cleanup

if __name__ == '__main__':
    manager = ApplicationManager()
    sys.exit(manager.run())
