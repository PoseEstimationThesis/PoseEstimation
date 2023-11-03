from PySide6.QtWidgets import QApplication, QHBoxLayout, QWidget, QTabWidget, QGridLayout
from PySide6.QtCore import QThread, QSize
from worker import FrameProcessor, Camera
from camerawidget import CameraWidget
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
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        self.frame_processors = []
        self.threads = []

        cameras = discover_cameras()
        self.setup_camera_tabs(cameras)

        self.main_widget.show()

    def setup_camera_tabs(self, cameras):
        tab = None
        grid = None
        for i, camera in enumerate(cameras):
            if i % self.MAX_CAMERAS_PER_TAB == 0:
                tab = QWidget()
                grid = QGridLayout(tab)
                self.tab_widget.addTab(tab, f"Cameras {i+1}-{i+self.MAX_CAMERAS_PER_TAB}")
            cam_widget = CameraWidget(camera.camera_id)
            row = (i % self.MAX_CAMERAS_PER_TAB) // 2  # Change the divisor to adjust layout
            col = (i % self.MAX_CAMERAS_PER_TAB) % 2   # Change the modulus to adjust layout
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
