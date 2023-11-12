import pandas as pd
import atexit
from datetime import datetime


class DataManager:
    def __init__(self):
        self.data = pd.DataFrame(columns=["Device Number", "Joint Name", "Angle", "Timestamp"])

    def get_data(self, device_number, joint_name):
        mask = (self.data["Device Number"] == device_number) & (self.data["Joint Name"] == joint_name)
        subset = self.data[mask]
        if not subset.empty:
            latest_angle = subset["Angle"].iloc[-1]
            return latest_angle
        else:
            return None

    def set_data(self, device_number, joint_name, angle):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = pd.DataFrame([[device_number, joint_name, angle, timestamp]],
                                 columns=["Device Number", "Joint Name", "Angle", "Timestamp"])
        self.data = pd.concat([self.data, new_entry], ignore_index=True)


    def export_to_csv(self, file_path="data.csv"):
        self.data.to_csv(file_path, index=False)



shared_data_instance = DataManager()

