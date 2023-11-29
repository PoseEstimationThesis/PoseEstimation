from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget, QTabWidget, QGridLayout, QPushButton, QFileDialog
from PySide6.QtCore import QThread, QSize, QCoreApplication
from logic.DataManager import shared_data_instance
from worker import FrameProcessor, Camera
from camerawidget import CameraWidget
# from anglewidget import AngleWidget
from graphwidget import GraphWidget
from modelwidget import ModelWidget
from feature.JointDict import shared_joint_dict
import sys
from constants import MAX_CAMERAS_PER_TAB, MAX_GRAPHS_PER_TAB, MAX_MODELS_PER_TAB

def discover_cameras():
    cameras = []
    camera_ids = []
    camera_id_counter = 1
    for i in range(10):
        cam = Camera(i)
        if cam.is_valid():
            cam.create_id(camera_id_counter)
            cameras.append(cam)
            camera_ids.append(camera_id_counter)
            camera_id_counter += 1
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

        self.frame_processors = []
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
                print(len(self.cameras))
            cam_widget = CameraWidget(camera.camera_id)
            row = (i % MAX_CAMERAS_PER_TAB) // 2  # Change the divisor to adjust layout
            col = (i % MAX_CAMERAS_PER_TAB) % 2  # Change the modulus to adjust layout
            grid.addWidget(cam_widget, row, col)

            frame_processor = FrameProcessor(camera)
            thread = QThread()
            frame_processor.moveToThread(thread)

            thread.started.connect(frame_processor.start_processing)
            frame_processor.finished.connect(self.thread_cleanup(thread))
            frame_processor.frameProcessedSignal.connect(cam_widget.draw_landmarks)

            self.frame_processors.append(frame_processor)
            self.threads.append(thread)

            thread.start()
            thread.setPriority(QThread.HighPriority)

    # def setup_angle_tabs(self):
    #     for camera in self.cameras:
    #         self.angle_widgets.append(
    #             AngleWidget(camera.camera_id, shared_joint_dict.get_reverse({"11", "13", "15"})))
    #         self.angle_widgets.append(
    #             AngleWidget(camera.camera_id, shared_joint_dict.get_reverse({"12", "14", "16"})))
    #     grid = None
    #     for i, angle_widget in enumerate(self.angle_widgets):
    #         if i % MAX_ANGLES_PER_TAB == 0:
    #             tab = QWidget()
    #             grid = QGridLayout(tab)
    #         row = (i % MAX_ANGLES_PER_TAB) // 2
    #         col = (i % MAX_ANGLES_PER_TAB) % 2
    #         grid.addWidget(angle_widget, row, col)
    #         self.statistics_tab.addTab(tab, f"Angles {i + 1}-{i + MAX_ANGLES_PER_TAB}")
    #
    #         thread = QThread()
    #         angle_widget.moveToThread(thread)
    #         self.threads.append(thread)

    def setup_graph_tabs(self):
        joints = shared_joint_dict.get_all_keys()
        tab_index = 0
        for i, key in enumerate(joints):
            # Determine if the widget is the first in a tab
            show_legend = i % MAX_GRAPHS_PER_TAB == 0
            graph_widget = GraphWidget(key, show_legend)
            self.graph_widgets.append(graph_widget)

            if i % MAX_GRAPHS_PER_TAB == 0:
                tab = QWidget()
                grid = QGridLayout(tab)
                self.statistics_tab.addTab(tab, f"Graphs {tab_index * MAX_GRAPHS_PER_TAB + 1}-{min((tab_index + 1) * MAX_GRAPHS_PER_TAB, len(joints))}")
                tab_index += 1

            row = (i % MAX_GRAPHS_PER_TAB) // 2
            col = (i % MAX_GRAPHS_PER_TAB) % 2

            grid.addWidget(graph_widget, row, col)

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
                self.models_tab.addTab(tab, f"Model {tab_index * MAX_GRAPHS_PER_TAB + 1}")
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

    # def export_data(self):
    #     shared_data_instance.export_to_csv()
    #     print("Data exported to CSV file!")


if __name__ == '__main__':
    manager = ApplicationManager()
    sys.exit(manager.run())
