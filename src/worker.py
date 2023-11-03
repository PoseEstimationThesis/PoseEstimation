from PySide6.QtCore import QObject, Signal, Slot, QTimer
import cv2

class Camera:
    def __init__(self, camera_id):
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(self.camera_id)
        self.valid = self.cap.isOpened()

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
    
    frameProcessedSignal = Signal(object, int)
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
        print(f"Attempting to process frame from camera {self.camera.camera_id}")
        ret, frame = self.camera.read_frame()
        if ret:
            # Process the frame
            # Here insert mediapipe logic
            processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            print(f"Processing frame from camera {self.camera.camera_id}")
            self.frameProcessedSignal.emit(processed_frame, self.camera.camera_id)
        else:
            print(f"Camera {self.camera.camera_id} finished or failed to read frame.")
            self.finished.emit(self.camera.camera_id)
