class DataManager:
    def __init__(self):
        self.angle_data = {}

    def get_data(self, device_number, joint1, joint2, joint3):
        key = f"{device_number}_{joint1}_{joint2}_{joint3}"
        return self.angle_data.get(key, {"angle": None})

    def set_data(self, device_number, joint1, joint2, joint3, angle):
        key = f"{device_number}_{joint1}_{joint2}_{joint3}"
        self.angle_data[key] = {"angle": angle}



shared_data_instance = DataManager()