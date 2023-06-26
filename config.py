import numpy as np

def distance(point1, point2):
    """
    Возвращает расстояние между двумя точками в декартовой системе координат.
    """
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

GAUSSIAN_BLUR_KERNEL = (11, 11)
LINES_DISTANCE_THRESHOLD = 50
LINES_ENDPOINTS_DIFFERENCE = 10
THRESHOLD_MIN = 160
THRESHOLD_MAX = 255
NOTE_PITCH_DETECTION_MIDDLE_SNAPPING = 6