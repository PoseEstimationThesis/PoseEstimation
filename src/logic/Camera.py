import cv2 as cv


class CameraObject:

    def __init__(self, device_number):
        self.device_number = device_number


    def start_capturing(self):
        device = cv.VideoCapture(self.device_number)

        if not device.isOpened():
            print("Cannot open camera")
            exit()

        while True:

            ret, frame = device.read()

            cv.imshow('frame', frame)

            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        device.release()
        cv.destroyAllWindows()
