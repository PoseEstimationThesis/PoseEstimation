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
        columns = ['x', 'y', 'z', 'visibility']
        self.landmark_data = pd.DataFrame(columns=columns)
        self.landmark_data.index = pd.MultiIndex(levels=[[], [], []], 
                                                 codes=[[], [], []], 
                                                 names=['Device Number', 'Timestamp', 'Joint ID'])

        self.world_landmark_data = pd.DataFrame(columns=columns)
        self.world_landmark_data.index = pd.MultiIndex(levels=[[], [], []], 
                                                 codes=[[], [], []], 
                                                 names=['Device Number', 'Timestamp', 'Joint ID'])

        self.update_button_text_callback = None
        self.device_color_map = {}
        self.available_colors = self.get_shuffled_colors()

    def reset_dataframes(self):
        empty_data = pd.DataFrame(columns=self.landmark_data.columns)
        empty_data.index = pd.MultiIndex(levels=[[], [], []], 
                                         codes=[[], [], []], 
                                         names=self.landmark_data.index.names)
        self.landmark_data = empty_data

        empty_world_data = pd.DataFrame(columns=self.world_landmark_data.columns)
        empty_world_data.index = pd.MultiIndex(levels=[[], [], []], 
                                               codes=[[], [], []], 
                                               names=self.world_landmark_data.index.names)
        self.world_landmark_data = empty_world_data

    def set_update_button_text_callback(self, callback):
        self.update_button_text_callback = callback

    def switch_recording_data(self):
        self.record_data_running = not self.record_data_running
        if self.record_data_running:
            self.reset_dataframes()
            self.update_button_text_callback("Stop")
            print(self.landmark_data, self.world_landmark_data)
        else:
            self.update_button_text_callback("Run")
            print(self.landmark_data, self.world_landmark_data)

    def set_landmark_data(self, landmark_data):
        # Convert the dictionary into a DataFrame
        new_data = []
        for key, values in landmark_data.items():
            new_data.append((*key, values['x'], values['y'], values['z'], values['visibility']))

        new_df = pd.DataFrame(new_data, columns=self.landmark_data.index.names + self.landmark_data.columns.tolist())
        new_df.set_index(['Device Number', 'Timestamp', 'Joint ID'], inplace=True)
        if not self.landmark_data.empty and not new_df.empty:
            self.landmark_data = pd.concat([self.landmark_data, new_df])
        elif self.landmark_data.empty:
            self.landmark_data = new_df

    def set_world_landmark_data(self, world_landmark_data):
        new_data = []
        for key, values in world_landmark_data.items():
            new_data.append((*key, values['x'], values['y'], values['z'], values['visibility']))

        new_df = pd.DataFrame(new_data, columns=self.world_landmark_data.index.names + self.world_landmark_data.columns.tolist())
        new_df.set_index(['Device Number', 'Timestamp', 'Joint ID'], inplace=True)
        if not self.world_landmark_data.empty and not new_df.empty:
            self.world_landmark_data = pd.concat([self.world_landmark_data, new_df])
        elif self.world_landmark_data.empty:
            self.world_landmark_data = new_df

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
    # def set_data(self, device_number, joint_name, angle):
    #     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    #     new_entry = pd.DataFrame([[device_number, joint_name, angle, timestamp]],
    #                              columns=["Device Number", "Joint Name", "Angle", "Timestamp"])
    #     new_entry_cleaned = new_entry.dropna(axis=1, how='all') # Drop all NA columns
    #     self.data = pd.concat([self.data, new_entry_cleaned], ignore_index=True)

    # def export_to_ods(self, filename="Joint_Data.ods"):
    #     # Create an OpenDocument Spreadsheet
    #     ods = OpenDocumentSpreadsheet()
    #
    #     # Group data by 'Joint Name'
    #     grouped_data = self.data.groupby('Joint Name')
    #
    #     for joint_name, group in grouped_data:
    #         # Drop the 'Joint Name' column
    #         group = group.drop(columns=['Joint Name'])
    #
    #         # Create a table (sheet) for each joint name
    #         table = Table(name=joint_name)
    #         ods.spreadsheet.addElement(table)
    #
    #         # Add metadata row for the Joint Name
    #         metadata_row = TableRow()
    #         table.addElement(metadata_row)
    #         metadata_cell = TableCell()
    #         metadata_row.addElement(metadata_cell)
    #         metadata_paragraph = P(text=f"Joint Name: {joint_name}")
    #         metadata_cell.addElement(metadata_paragraph)
    #
    #         # Add header row
    #         header_row = TableRow()
    #         table.addElement(header_row)
    #         for col in group.columns:
    #             tc = TableCell()
    #             header_row.addElement(tc)
    #             p = P(text=str(col))
    #             tc.addElement(p)
    #
    #         # Add data rows to the table
    #         for _, row in group.iterrows():
    #             tr = TableRow()
    #             table.addElement(tr)
    #             for cell in row:
    #                 tc = TableCell()
    #                 tr.addElement(tc)
    #                 p = P(text=str(cell))
    #                 tc.addElement(p)
    #
    #     # Save the file
    #     ods.save(filename)


shared_data_instance = DataManager()
