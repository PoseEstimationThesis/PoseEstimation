import pandas as pd
import atexit
import random
import matplotlib.colors as mcolors
from datetime import datetime
from odf.opendocument import OpenDocumentSpreadsheet
from odf.table import Table, TableRow, TableCell
from odf.text import P

class DataManager:
    def __init__(self):
        self.data = pd.DataFrame(columns=["Device Number", "Joint Name", "Angle", "Timestamp"])
        self.update_button_text_callback = None
        self.device_color_map = {}
        self.available_colors = self.get_shuffled_colors()

    def get_shuffled_colors(self, seed=0):
        random.seed(seed)
        colors = list(mcolors.CSS4_COLORS.values())
        random.shuffle(colors)
        return colors

    def get_color_for_device(self, device_number):
        if device_number not in self.device_color_map:
            color = self.available_colors[len(self.device_color_map) % len(self.available_colors)]
            self.device_color_map[device_number] = color
        return self.device_color_map[device_number]

    def set_update_button_text_callback(self, callback):
        self.update_button_text_callback = callback

    def switch_recording_data(self):
        self.record_data_running = not self.record_data_running
        if self.record_data_running:
            self.update_button_text_callback("Stop")
        else:
            self.export_to_ods()
            self.update_button_text_callback("Run")

    def get_data(self, device_number, joint_name):
        self.data.reset_index(drop=True, inplace=True)
        mask = (self.data["Device Number"] == device_number) & (self.data["Joint Name"] == joint_name)
        return self.data[mask]

    def set_data(self, device_number, joint_name, angle):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        new_entry = pd.DataFrame([[device_number, joint_name, angle, timestamp]],
                                 columns=["Device Number", "Joint Name", "Angle", "Timestamp"])
        self.data = pd.concat([self.data, new_entry], ignore_index=True)

    def get_device_numbers(self):
        return self.data["Device Number"].unique().tolist()

    def export_to_ods(self, filename="Joint_Data.ods"):
        # Create an OpenDocument Spreadsheet
        ods = OpenDocumentSpreadsheet()

        # Group data by 'Joint Name'
        grouped_data = self.data.groupby('Joint Name')

        for joint_name, group in grouped_data:
            # Drop the 'Joint Name' column
            group = group.drop(columns=['Joint Name'])

            # Create a table (sheet) for each joint name
            table = Table(name=joint_name)
            ods.spreadsheet.addElement(table)

            # Add metadata row for the Joint Name
            metadata_row = TableRow()
            table.addElement(metadata_row)
            metadata_cell = TableCell()
            metadata_row.addElement(metadata_cell)
            metadata_paragraph = P(text=f"Joint Name: {joint_name}")
            metadata_cell.addElement(metadata_paragraph)

            # Add header row
            header_row = TableRow()
            table.addElement(header_row)
            for col in group.columns:
                tc = TableCell()
                header_row.addElement(tc)
                p = P(text=str(col))
                tc.addElement(p)

            # Add data rows to the table
            for _, row in group.iterrows():
                tr = TableRow()
                table.addElement(tr)
                for cell in row:
                    tc = TableCell()
                    tr.addElement(tc)
                    p = P(text=str(cell))
                    tc.addElement(p)

        # Save the file
        ods.save(filename)


shared_data_instance = DataManager()
