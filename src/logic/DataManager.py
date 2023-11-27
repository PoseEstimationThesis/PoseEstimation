import pandas as pd
import atexit
from datetime import datetime
from odf.opendocument import OpenDocumentSpreadsheet
from odf.table import Table, TableRow, TableCell
from odf.text import P

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
            self.export_to_ods()
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
