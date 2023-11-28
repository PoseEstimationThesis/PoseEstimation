from PySide6.QtCore import QObject, Signal, Slot, QTimer
import cv2
from logic.BodyEstimation import BodyEstimator
from logic.DataManager import shared_data_instance

class Camera:
    def __init__(self, camera_addr):
        self.camera_addr = camera_addr
        self.cap = cv2.VideoCapture(self.camera_addr)
        self.valid = self.cap.isOpened()

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

class FrameProcessor(QObject):
    FRAMES_PER_SECOND = 120
    
    frameProcessedSignal = Signal(int, object, object)
    finished = Signal(int)

    def start_processing(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(1000/self.FRAMES_PER_SECOND)  # Adjust as necessary

    def __init__(self, camera):
        super().__init__()
        self.camera = camera


    @Slot()
    def process_frame(self):
        # print(f"Attempting to process frame from camera {self.camera.camera_id}")
        ret, frame = self.camera.read_frame()
        if ret:
            # Process the frame
            # Here insert mediapipe logic
            processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.camera.body_estimator.estimate_body(processed_frame)
            # Calculate joint values and append them to DataFrame only when recording
            if shared_data_instance.record_data_running:
                self.camera.body_estimator.calculate_all()
            self.frameProcessedSignal.emit(self.camera.camera_id, self.camera.body_estimator.landmarks, processed_frame)
        else:
            # print(f"Camera {self.camera.camera_id} finished or failed to read frame.")
            self.finished.emit(self.camera.camera_id)
