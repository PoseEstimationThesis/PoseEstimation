from PySide6.QtCore import QObject, Signal, Slot
import cv2
from logic.bodyestimation import BodyEstimator

class Camera(QObject):
    frameProcessedSignal = Signal(int, object, object)
    finished = Signal(int)

    def __init__(self, camera_addr):
        super().__init__()
        self.camera_addr = camera_addr
        self.cap = cv2.VideoCapture(self.camera_addr)
        self.valid = self.cap.isOpened()
        self.camera_id = None
        self.body_estimator = None
        self.running = True

    def create_id(self, camera_id):
        self.camera_id = camera_id
        self.body_estimator = BodyEstimator(self.camera_id)

    def read_frame(self):
        if self.is_valid():
            return self.cap.read()
        return False, None

    def release(self):
        if self.cap.isOpened():
            self.cap.release()

    def is_valid(self):
        return self.valid

    def start_processing(self):
        while self.running:
            self.process_frame()

    @Slot()
    def process_frame(self):
        ret, frame = self.read_frame()
        if ret:
            # Process the frame
            processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.body_estimator.estimate_body(processed_frame)
            self.frameProcessedSignal.emit(self.camera_id, self.body_estimator.landmarks, processed_frame)
        else:
            self.finished.emit(self.camera_id)
            self.running = False

    def stop_processing(self):
        self.running = False
