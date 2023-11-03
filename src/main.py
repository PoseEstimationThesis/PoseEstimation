from PySide6.QtWidgets import QApplication, QHBoxLayout, QWidget
from PySide6.QtCore import QThread
from worker import FrameProcessor, Camera
from camerawidget import CameraWidget
import sys

def discover_cameras():
    # Simple camera discovery
    cameras = []
    for i in range(5):  # check the first 5 indices
        cam = Camera(i)
        if cam.is_valid():
            cameras.append(cam)
    return cameras

class ApplicationManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)
        self.frame_processors = []
        self.threads = []

        cameras = discover_cameras()
        for camera in cameras:
            cam_widget = CameraWidget(camera.camera_id)
            self.main_layout.addWidget(cam_widget)

            frame_processor = FrameProcessor(camera)
            thread = QThread()
            frame_processor.moveToThread(thread)

            thread.started.connect(frame_processor.start_processing)
            frame_processor.finished.connect(self.thread_cleanup(thread))
            frame_processor.frameProcessedSignal.connect(cam_widget.update_image)

            self.frame_processors.append(frame_processor)
            self.threads.append(thread)

            thread.start()

        self.main_widget.show()

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
