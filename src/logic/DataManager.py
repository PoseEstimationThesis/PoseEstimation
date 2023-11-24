import pandas as pd
import atexit
from datetime import datetime

class DataManager:
    def __init__(self):
        self.data = pd.DataFrame(columns=["Device Number", "Joint Name", "Angle", "Timestamp"])
        self.update_button_text_callback = None

    def set_update_button_text_callback(self, callback):
        self.update_button_text_callback = callback

    def switch_recording_data(self):
        self.record_data_running = not self.record_data_running
        if self.record_data_running:
            self.update_button_text_callback("Stop")
        else:
            self.export_to_csv()
            self.update_button_text_callback("Run")

    def get_data(self, device_number, joint_name):
        mask = (self.data["Device Number"] == device_number) & (self.data["Joint Name"] == joint_name)
        subset = self.data[mask]
        if not subset.empty:
            latest_angle = subset["Angle"].iloc[-1]
            return latest_angle
        else:
            return None

    def set_data(self, device_number, joint_name, angle):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        new_entry = pd.DataFrame([[device_number, joint_name, angle, timestamp]],
                                 columns=["Device Number", "Joint Name", "Angle", "Timestamp"])
        self.data = pd.concat([self.data, new_entry], ignore_index=True)

    def export_to_csv(self):
        # Group data by 'Joint Name'
        grouped_data = self.data.groupby('Joint Name')

        for joint_name, group in grouped_data:
            # Filter data for each 'Joint Name' and create a DataFrame with specific columns
            filtered_data = group[["Timestamp", "Device Number", "Angle"]]

            # Export filtered data to CSV for each 'Joint Name'
            joint_csv_filename = f"{joint_name}_data.csv"
            filtered_data.to_csv(joint_csv_filename, index=False)


shared_data_instance = DataManager()
