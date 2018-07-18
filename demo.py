import cv2
import numpy as np

from manipulator import Manipulator
from picker import Picker, EARTH_LEVEL, RESOLUTION

VIDEO_FPS = 25
VIDEO_FOURCC = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
FRAME_RES = (RESOLUTION[1], RESOLUTION[0])

def collect_items(show_video=True, record_video=False):
    manipulator = Manipulator()

    # set up items to be collected
    items = [{'size': 30, 'place': (210, EARTH_LEVEL), 'name': 'red', 'color': (35, 35, 215)},
             {'size': 40, 'place': (250, EARTH_LEVEL), 'name': 'green', 'color': (50, 150, 0)},
             {'size': 50, 'place': (300, EARTH_LEVEL), 'name': 'yellow', 'color': (25, 220, 230)}]
    dest_range = (350, 640)
    # generate random positions within dest_range
    # To make items not to be overlapping, first point positions in [0, free_size) interval are
    # generated, then every point expands to the required size (with spaces between points saved)
    range_size = dest_range[1] - dest_range[0]
    sum_size = sum(item['size'] for item in items)
    free_size = range_size - sum_size
    x_positions = dest_range[0] + np.random.randint(free_size, size=len(items))
    for i, (item, pos) in enumerate(zip(items, x_positions)):
        x_positions[x_positions > pos] += item['size']
        x_positions[i] += item['size'] // 2
    positions = [(x, EARTH_LEVEL - items[i]['size'] // 2) for i, x in enumerate(x_positions)]
    for item, position in zip(items, positions):
        item['position'] = position

    # set up video showing and recording
    window = "collect items demo" if show_video else None
    writer = cv2.VideoWriter("collect items demo.avi",
                             VIDEO_FOURCC,
                             VIDEO_FPS,
                             FRAME_RES) if record_video else None

    # collect items
    picker = Picker(manipulator, items, window, writer)
    picker.collect()

    if show_video:
        cv2.destroyWindow(window)
    if record_video:
        writer.release()

if __name__ == '__main__':
    collect_items()
