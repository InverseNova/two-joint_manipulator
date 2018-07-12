from collections import namedtuple
import math

import cv2
import numpy as np

ManipulatorConfig = namedtuple('ManipulatorConfig',
                               ['base_x', 'base_y', 'L1', 'L2', 'ang1', 'ang2', 'max_speed',
                                'pick_distance', 'joint_size', 'holds'])

INITIAL_CONFIG = ManipulatorConfig(base_x = 100,
                                   base_y = 400,
                                   L1 = 300,
                                   L2 = 270,
                                   ang1 = 4.5,
                                   ang2 = 2.8,
                                   max_speed = 0.02,
                                   pick_distance = 1,
                                   joint_size = 10,
                                   holds = None)

# some constants for drawing
HALF_BASE_WIDTH = 30
HALF_BASE_HEIGHT = 30
BASE_COLOR = (50, 150, 200)
ARM_COLOR_1 = (50, 0, 0)
ARM_COLOR_2 = (200, 80, 40)
ARM_THICKNESS_1 = 20
ARM_THICKNESS_2 = 18
JOINT_COLOR = (160, 55, 175)
JOINT_SIZE_INNER = 8

def distance(a, b):
    return np.linalg.norm((a[0] - b[0], a[1] - b[1]))

class Manipulator(object):
    '''Class, emulating two-joint manipulator work'''
    def __init__(self, config=INITIAL_CONFIG):
        self.base_x = config.base_x
        self.base_y = config.base_y
        self.L1 = config.L1
        self.L2 = config.L2
        self.ang1 = (config.ang1 - math.pi) % (2 * math.pi) + math.pi
        self.ang2 = config.ang2 % (2 * math.pi)
        self.max_speed = config.max_speed
        self.pick_distance = config.pick_distance
        self.joint_size = config.joint_size
        self.holds = config.holds
        if self.pick_distance <= 0:
            raise ValueError('Manipulator picking distance must be positive')
        if self.max_speed <= 0:
            raise ValueError('Manipulator maximum speed must be positive')
        self.compute_joints_positions()

    def compute_joints_positions(self):
        self.joint1 = (self.base_x + self.L1 * math.cos(self.ang1),
                       self.base_y + self.L1 * math.sin(self.ang1))
        res_ang2 = self.ang1 + self.ang2
        self.joint2 = (self.joint1[0] + self.L2 * math.cos(res_ang2),
                       self.joint1[1] + self.L2 * math.sin(res_ang2))

    def move(self, speed):
        '''Processes manipulator moves (one move per fixed time interval).
        speed --- tuple of desired angular speeds of manipulator joints, they will be reduced (with
                  proportion saved) if one of them exceeds maximum speed allowed by self.max_speed
        '''
        speed1, speed2 = speed
        if abs(speed1) > self.max_speed or abs(speed2) > self.max_speed:
            div = max(abs(speed1), abs(speed2)) / self.max_speed
            speed1 /= div
            speed2 /= div
        self.ang1 += speed1
        self.ang2 += speed2
        self.compute_joints_positions()

    def hold(self, item_name, pick_point):
        '''Holds item if it's pick point is close to picking joint.
        Returns True if succeeded, False otherwise.
        '''
        if distance(self.joint2, pick_point) <= self.joint_size + self.pick_distance:
            self.holds = item_name
            return True
        return False

    def unhold(self):
        '''Releases item'''
        item_name = self.holds
        self.holds = None
        return item_name

    def draw(self, image):
        ''' Draws manipulator on the given image'''
        cv2.rectangle(image,
                      (self.base_x - HALF_BASE_WIDTH, self.base_y - HALF_BASE_HEIGHT),
                      (self.base_x + HALF_BASE_WIDTH, self.base_y + HALF_BASE_HEIGHT),
                      BASE_COLOR,
                      cv2.FILLED)

        joint1 = tuple(map(int, self.joint1))
        cv2.line(image, (self.base_x, self.base_y), joint1, ARM_COLOR_1, ARM_THICKNESS_1)
        cv2.line(image, (self.base_x, self.base_y), joint1, ARM_COLOR_2, ARM_THICKNESS_2)

        joint2 = tuple(map(int, self.joint2))
        cv2.line(image, joint1, joint2, ARM_COLOR_1, ARM_THICKNESS_1)
        cv2.line(image, joint1, joint2, ARM_COLOR_2, ARM_THICKNESS_2)

        cv2.circle(image, (self.base_x, self.base_y), JOINT_SIZE_INNER, JOINT_COLOR, cv2.FILLED)
        cv2.circle(image, joint1, JOINT_SIZE_INNER, JOINT_COLOR, cv2.FILLED)
        cv2.circle(image, joint2, JOINT_SIZE_INNER, JOINT_COLOR, cv2.FILLED)
