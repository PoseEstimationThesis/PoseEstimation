import pandas as pd
import atexit
import random
import matplotlib.colors as mcolors
from datetime import datetime
import numpy as np
from odf.opendocument import OpenDocumentSpreadsheet
from odf.table import Table, TableRow, TableCell
from odf.text import P
from PySide6.QtCore import QObject, Signal
from constants import JOINTS_ANGLES_TO_CALCULATE, VISIBILITY_THRESHOLD

class DataManager(QObject):
    angles_updated = Signal(object)
    def __init__(self):
        super().__init__()
        columns = ['x', 'y', 'z', 'visibility']
        self.landmark_data = pd.DataFrame(columns=columns)
        self.landmark_data.index = pd.MultiIndex(levels=[[], [], []], 
                                                 codes=[[], [], []], 
                                                 names=['Device Number', 'Timestamp', 'Joint ID'])

        self.world_landmark_data = pd.DataFrame(columns=columns)
        self.world_landmark_data.index = pd.MultiIndex(levels=[[], [], []], 
                                                 codes=[[], [], []], 
                                                 names=['Device Number', 'Timestamp', 'Joint ID'])
        self.angle_data = pd.DataFrame(columns=['Device Number', 'Timestamp', 'Joint Pair', 'Angle'])
        self.world_angle_data = pd.DataFrame(columns=['Device Number', 'Timestamp', 'Joint Pair', 'Angle'])
        self.update_button_text_callback = None

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
        empty_angle_data= pd.DataFrame(columns=self.angle_data.columns)
        empty_world_angle_data= pd.DataFrame(columns=self.world_angle_data.columns)
        self.angle_data = empty_angle_data
        self.world_angle_data = empty_world_angle_data

    def set_update_button_text_callback(self, callback):
        self.update_button_text_callback = callback

    def switch_recording_data(self):
        self.record_data_running = not self.record_data_running
        if self.record_data_running:
            self.reset_dataframes()
            self.update_button_text_callback("Stop")
        else:
            self.calculate_and_store_angles(JOINTS_ANGLES_TO_CALCULATE)
            self.angles_updated.emit({'landmark_angles': self.angle_data, 'world_landmark_angles': self.world_angle_data})
            export_to_ods(self.landmark_data, "landmark_data.ods")
            export_to_ods(self.world_landmark_data, "world_landmark_data.ods")
            self.update_button_text_callback("Run")

    def calculate_and_store_angles(self, joints):
        landmark_data_copy = self.landmark_data
        world_landmark_data_copy = self.world_landmark_data
        for device_number in landmark_data_copy.index.levels[0]:
            device_data = landmark_data_copy.xs(device_number, level='Device Number')
            timestamps = device_data.index.get_level_values('Timestamp').unique()
            for timestamp in timestamps:
                if not (device_number, timestamp) in landmark_data_copy.index:
                    continue
                for angle_name, (pair1, pair2) in joints.items():  # Iterate through dictionary
                    # Check if all joints for both pairs are available at this timestamp
                    if all(joint in landmark_data_copy.loc[device_number, timestamp].index for joint in pair1 + pair2):
                        A = landmark_data_copy.loc[(device_number, timestamp, pair1[0])][['x', 'y', 'z', 'visibility']].values
                        A[2] = 0
                        B = landmark_data_copy.loc[(device_number, timestamp, pair1[1])][['x', 'y', 'z', 'visibility']].values
                        B[2] = 0
                        C = landmark_data_copy.loc[(device_number, timestamp, pair2[0])][['x', 'y', 'z', 'visibility']].values
                        C[2] = 0
                        D = landmark_data_copy.loc[(device_number, timestamp, pair2[1])][['x', 'y', 'z', 'visibility']].values
                        D[2] = 0
                        angle = calculate_3D_angle(A, B, C, D)  # Updated function call
                        new_df = pd.DataFrame([{
                            'Device Number': device_number, 
                            'Timestamp': timestamp, 
                            'Joint Pair': angle_name,
                            'Angle': angle
                        }])
                        if not self.angle_data.empty and not new_df.empty:
                            self.angle_data = pd.concat([self.angle_data, new_df], ignore_index=True)
                        elif self.angle_data.empty:
                            self.angle_data = new_df
        for device_number in world_landmark_data_copy.index.levels[0]:
            device_data = world_landmark_data_copy.xs(device_number, level='Device Number')
            timestamps = device_data.index.get_level_values('Timestamp').unique()
            for timestamp in timestamps:
                if not (device_number, timestamp) in world_landmark_data_copy.index:
                    continue
                for angle_name, (pair1, pair2) in joints.items():  # Iterate through dictionary
                    # Check if all joints for both pairs are available at this timestamp
                    if all(joint in world_landmark_data_copy.loc[device_number, timestamp].index for joint in pair1 + pair2):
                        A = world_landmark_data_copy.loc[(device_number, timestamp, pair1[0])][['x', 'y', 'z', 'visibility']].values
                        A[2] = 0
                        B = world_landmark_data_copy.loc[(device_number, timestamp, pair1[1])][['x', 'y', 'z', 'visibility']].values
                        B[2] = 0
                        C = world_landmark_data_copy.loc[(device_number, timestamp, pair2[0])][['x', 'y', 'z', 'visibility']].values
                        C[2] = 0
                        D = world_landmark_data_copy.loc[(device_number, timestamp, pair2[1])][['x', 'y', 'z', 'visibility']].values
                        D[2] = 0
                        angle = calculate_3D_angle(A, B, C, D)  # Updated function call
                        new_df = pd.DataFrame([{
                            'Device Number': device_number, 
                            'Timestamp': timestamp, 
                            'Joint Pair': angle_name,
                            'Angle': angle
                        }])
                        if not self.world_angle_data.empty and not new_df.empty:
                            self.world_angle_data = pd.concat([self.world_angle_data, new_df], ignore_index=True)
                        elif self.world_angle_data.empty:
                            self.world_angle_data = new_df

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
        self.landmark_data = self.landmark_data.sort_index()

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
        self.world_landmark_data = self.world_landmark_data.sort_index()

def calculate_3D_angle(A, B, C, D):
    """
    Accepts A, B, C, D as a list of x, y, z values and visibility
    A = (x1, y1, z1, visibility)
    B = (x2, y2, z2, visibility)
    C = (x3, y3, z3, visibility)
    D = (x4, y4, z4, visibility)
    Returns NaN if visibility of any point is less than VISIBILITY_THRESHOLD.
    """
    # Check visibility for each point
    if A[3] < VISIBILITY_THRESHOLD or B[3] < VISIBILITY_THRESHOLD or \
       C[3] < VISIBILITY_THRESHOLD or D[3] < VISIBILITY_THRESHOLD:
        return np.nan

    # Convert to numpy arrays without visibility
    A = np.array(A[:3])
    B = np.array(B[:3])
    C = np.array(C[:3])
    D = np.array(D[:3])

    # Create vectors
    vector_BA = A - B
    vector_CD = D - C

    # Calculate the dot product
    dot_product = np.dot(vector_BA, vector_CD)

    # Calculate the magnitudes of the vectors
    magnitude_BA = np.linalg.norm(vector_BA)
    magnitude_CD = np.linalg.norm(vector_CD)

    # Calculate the cosine of the angle
    cosine_angle = dot_product / (magnitude_BA * magnitude_CD)

    # Handle potential floating point errors that might cause acos to be out of range
    cosine_angle = np.clip(cosine_angle, -1, 1)

    # Calculate the angle in radians and then convert it to degrees
    angle = np.arccos(cosine_angle)
    angle_degrees = np.degrees(angle)

    return angle_degrees


def export_to_ods(df, file_name):
    # Pivot and restructure the DataFrame
    df_pivot = df.pivot_table(index=["Device Number", "Timestamp"], columns="Joint ID", values=['x', 'y', 'z', 'visibility'])
    df_pivot = df_pivot.swaplevel(i=0, j=1, axis=1).sort_index(axis=1)
    df_pivot.sort_index(inplace=True)

    # Create a new OpenDocument Spreadsheet
    doc = OpenDocumentSpreadsheet()

    # Iterate over each 'Device Number' and create a separate sheet
    for device_number, group_df in df_pivot.groupby(level=0):
        table = Table(name=f"Device_{device_number}")

        # Add column headers
        tr = TableRow()
        tc = TableCell()  # Empty cell for Timestamp header
        tr.addElement(tc)
        for col in group_df.columns:
            tc = TableCell()
            header = f"{col[1]}_{col[0]}"  # Joint ID followed by x, y, z, or visibility
            tc.addElement(P(text=header))
            tr.addElement(tc)
        table.addElement(tr)

        # Add data rows
        for index, row in group_df.iterrows():
            tr = TableRow()

            # Add Timestamp cell, index[1] is the Timestamp
            tc = TableCell()
            tc.addElement(P(text=str(index[1])))
            tr.addElement(tc)

            # Add data cells
            for cell in row:
                tc = TableCell()
                tc.addElement(P(text=str(cell) if pd.notna(cell) else ""))
                tr.addElement(tc)
            table.addElement(tr)

        # Add table to the document
        doc.spreadsheet.addElement(table)

    # Save the file
    doc.save(file_name)


shared_data_instance = DataManager()
