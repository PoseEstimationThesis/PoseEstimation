import mediapipe as mp

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

MAX_CAMERAS_PER_TAB = 2
MAX_GRAPHS_PER_TAB = 1
MAX_MODELS_PER_TAB = 1

VISIBILITY_THRESHOLD = 0.6
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.3


CONNECTIONS = mp.solutions.pose.POSE_CONNECTIONS

body_parts_indices = {
    "Head": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "Torso": [11, 12, 23, 24],
    "Left Arm": [13, 15, 17, 19, 21],
    "Right Arm": [14, 16, 18, 20, 22],
    "Left Leg": [25, 27, 29, 31],
    "Right Leg": [26, 28, 30, 32]
    }
BODY_PARTS_NAME = {idx: part for part, indices in body_parts_indices.items() for idx in indices}
JOINTS_TO_DRAW = set(BODY_PARTS_NAME.keys())


body_part_colors_hex = {
    "Head": "#2dd726",
    "Torso": "#f81f21",
    "Right Arm": "#fe9100",
    "Right Leg": "#ffda17",
    "Left Arm": "#eb00db",
    "Left Leg": "#8C31FF"
    }
landmark_color = "#0580fc"

LANDMARK_COLOR = hex_to_rgb(landmark_color)
BODY_PARTS_COLORS = {part: hex_to_rgb(color) for part, color in body_part_colors_hex.items()}

JOINTS_ANGLES_TO_CALCULATE = {
        "Prawy Kolanowy": ((24, 26), (26, 28)),
        "Lewy Kolanowy": ((23, 25), (25, 27)),
        "Prawy Skokowy": ((26, 28), (30, 32)),
        "Lewy Skokowy": ((25, 27), (29, 31)),
        "Prawy Biodrowy": ((12, 24), (24, 26)),
        "Lewy Biodrowy": ((11, 23), (23, 25))
        }
