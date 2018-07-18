import math

import cv2
import numpy as np

from manipulator import distance

GAP = 10

# some constants for drawing
LATENCY = 40
BIG_LATENCY = 1500
RESOLUTION = (480, 640, 3)
BACKGROUND_COLOR = (170, 150, 120)
EARTH_LEVEL = 430
EARTH_COLOR = (100, 150, 200)

class Picker(object):
    '''Class, emulating object picking-and-replacing algorithm'''
    def __init__(self, manipulator, items, window=None, writer=None):
        self.manipulator = manipulator
        self.items = items
        self.window = window
        self.writer = writer

    def get_speed(self, dest_point):
        '''Computes speed for accessing destination point'''
        dx = dest_point[0] - self.manipulator.base_x
        dy = dest_point[1] - self.manipulator.base_y
        L1 = self.manipulator.L1
        L2 = self.manipulator.L2
        L = np.linalg.norm((dx, dy))
        des_cos_ang2 = (dx ** 2 + dy ** 2 - L1 ** 2 - L2 ** 2) / (2 * L1 * L2)
        des_ang2 = np.sign(dx) * math.acos(des_cos_ang2)
        des_ang1 = math.asin(dy / L) - \
                   np.sign(dx) * math.acos((L1 ** 2 + L ** 2 - L2 ** 2) / (2 * L * L1))
        speed1 = (des_ang1 - self.manipulator.ang1 + math.pi) % (2 * math.pi) - math.pi
        speed2 = (des_ang2 - self.manipulator.ang2 + math.pi) % (2 * math.pi) - math.pi
        return (speed1, speed2)

    def move_item(self, item, init_joint2):
        '''Return new item position after manipulator move (while it is holding item)'''
        return (item['position'][0] + self.manipulator.joint2[0] - init_joint2[0],
                item['position'][1] + self.manipulator.joint2[1] - init_joint2[1])

    def collect(self):
        '''Collects items to their places'''
        replaced_items = []
        max_item_size = max(item['size'] for item in self.items)
        min_item_pos_y = min(item['position'][1] for item in self.items)
        safe_height = min_item_pos_y - max_item_size - GAP
        transfer_height = safe_height - max_item_size - GAP
        image = np.zeros(RESOLUTION, dtype=np.uint8)

        while len(replaced_items) < len(self.items):
            item = self.items[len(replaced_items)]

            # place picking joint on safe_height
            dest_point = (self.manipulator.joint2[0], safe_height)
            while distance(dest_point, self.manipulator.joint2) > GAP:
                self.manipulator.move(self.get_speed(dest_point))
                self.draw(image)

            # place picking joint right over the item
            dest_point = (item['position'][0], safe_height)
            while distance(dest_point, self.manipulator.joint2) > GAP:
                self.manipulator.move(self.get_speed(dest_point))
                self.draw(image)

            # place picking joint in picking position and pick item
            pick_point = (item['position'][0], item['position'][1] - item['size'] // 2)
            dest_point = (pick_point[0], pick_point[1] - self.manipulator.joint_size)
            while not self.manipulator.hold(item['name'], pick_point):
                self.manipulator.move(self.get_speed(dest_point))
                self.draw(image)

            # place picking joint on transfer_height
            dest_point = (item['position'][0], transfer_height)
            while distance(dest_point, self.manipulator.joint2) > GAP:
                init_joint2 = self.manipulator.joint2
                self.manipulator.move(self.get_speed(dest_point))
                item['position'] = self.move_item(item, init_joint2)
                self.draw(image)

            # place picking joint right over the item's place
            dest_point = (item['place'][0], transfer_height)
            while distance(dest_point, self.manipulator.joint2) > GAP:
                init_joint2 = self.manipulator.joint2
                self.manipulator.move(self.get_speed(dest_point))
                item['position'] = self.move_item(item, init_joint2)
                self.draw(image)

            # place picking joint in unpicking position and release item
            dest_point = (item['place'][0],
                          item['place'][1] - item['size'] - self.manipulator.joint_size)
            while distance(dest_point, self.manipulator.joint2) > self.manipulator.pick_distance:
                init_joint2 = self.manipulator.joint2
                self.manipulator.move(self.get_speed(dest_point))
                item['position'] = self.move_item(item, init_joint2)
                self.draw(image)
            replaced_items.append(self.manipulator.unhold())

        # place picking joint on safe_height
        dest_point = (self.manipulator.joint2[0], safe_height)
        while distance(dest_point, self.manipulator.joint2) > GAP:
            self.manipulator.move(self.get_speed(dest_point))
            self.draw(image)

        if self.window:
            cv2.waitKey(BIG_LATENCY)

    def draw(self, image):
        '''Draws scene (manipulator, items and places for collecting) on the given image,
        optionally displays it and writes to the videofile
        '''
        height, width, _ = image.shape
        cv2.rectangle(image, (0, 0), (width, EARTH_LEVEL), BACKGROUND_COLOR, cv2.FILLED)
        cv2.rectangle(image, (0, EARTH_LEVEL), (width, height), EARTH_COLOR, cv2.FILLED)

        for item in self.items:
            item_position = tuple(map(int, item['position']))
            cv2.circle(image, item_position, item['size'] // 2, item['color'], cv2.FILLED)
            cv2.rectangle(image,
                          (item['place'][0] - item['size'] // 2, EARTH_LEVEL),
                          (item['place'][0] + item['size'] // 2, EARTH_LEVEL + GAP),
                          item['color'],
                          cv2.FILLED)

        self.manipulator.draw(image)

        if self.window:
            cv2.imshow(self.window, image)
            cv2.waitKey(LATENCY)

        if self.writer:
            self.writer.write(image)
