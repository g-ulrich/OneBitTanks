import pygame
from math import hypot
import json
from random import randint, choice
from datetime import datetime
import numpy as np


class Font:
    def __init__(self, size=15):
        # heart1 - U+005E
        # heart2 - U+005F
        # twitter - U+0060
        # patreon - U007B
        # facebook - U007C
        # twitch - U007D
        # smile1 - U007E
        # smile2 - U00A1
        # smile3 - U00A2
        # pacghost - U00A3
        # bob - U00A4
        # skull - U20A0
        self.bold = pygame.font.Font('assets/fonts/mago3.ttf', size)


class ControlsAssets:
    def __init__(self):
        self.font = Font(40)
        self.large_font = Font(50)


class SpriteSheet(object):
    """ Class used to grab images out of a sprite sheet. """

    def __init__(self, file_name):
        """ Constructor. Pass in the file name of the sprite sheet. """
        # Load the sprite sheet.
        self.sprite_sheet = pygame.image.load(file_name).convert()

    def get_image(self, x, y, width, height, color_key=(0, 0, 0)):
        """ Grab a single image out of a larger spritesheet
            Pass in the x, y location of the sprite
            and the width and height of the sprite. """
        # Create a new blank image
        image = pygame.Surface([width, height]).convert()
        # Copy the sprite from the large sheet onto the smaller image
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        # Assuming black works as the transparent color
        image.set_colorkey(color_key)
        # Return the image
        return image


class TankAssets:
    def __init__(self):
        self.font = Font(25)
        idle, up, right, gun, gun_hit, tank_hit, tracks = self.get_sprite_list('assets/images/light_yellow_tank')
        self.idle, self.up = idle, up
        self.right, self.gun = right, gun
        self.gun_hit, self.tank_hit = gun_hit, tank_hit
        self.tracks = tracks
        self.idle_flip = [pygame.transform.flip(i, flip_x=False, flip_y=True) for i in idle]
        self.down = [pygame.transform.flip(i, flip_x=False, flip_y=True) for i in up]
        self.left = [pygame.transform.flip(i, flip_x=True, flip_y=False) for i in right]
        self.down_right = [pygame.transform.flip(i, flip_x=True, flip_y=True) for i in up]
        self.down_left = [pygame.transform.flip(i, flip_x=False, flip_y=True) for i in right]
        self.down_tank_hit = pygame.transform.flip(tank_hit, flip_x=False, flip_y=True)

    def read_json_file(self, path):
        output = ""
        with open(path) as f:
            for line in f:
                output += line
        return json.loads(output)

    def get_sprite_list(self, path):
        name = "tank"
        sheet = SpriteSheet(f"{path}/{name}.png")
        sheet_map = self.read_json_file(f"{path}/{name}.json")
        frames = [sheet_map['frames'][key]['frame'] for key in sheet_map['frames'].keys()]
        images = [sheet.get_image(i['x'], i['y'], i['w'], i['h'], color_key=(0, 0, 0)) for i in frames]
        images = [pygame.transform.scale(i, (64, 64)) for i in images]
        return images[0:3], images[4:7], images[8:11], images[12], images[13], images[14], images[15]


class Explosion:
    def __init__(self, width=15, radius=1, color=(255, 255, 255), sec_color=(255, 200, 200)):
        self.color = color
        self.start = False
        self.width = width
        self.exp_index = -1
        self.center = pygame.math.Vector2()
        self.radius = radius
        self.second_color = sec_color
        self.hit_box_rect = pygame.Rect(0, 0, 0, 0)
        self.empty_rect = pygame.Rect(0, 0, 0, 0)

    def initiate(self, center_pos):
        self.center.x = center_pos[0]
        self.center.y = center_pos[1]
        self.start = True
        self.exp_index = 0

    def iterate(self, offset=(0, 0)):
        queue = {'layer': -100, 'type': 'circle', 'image': False, 'color': (255, 255, 255),
                 'rect': self.empty_rect, 'pos': self.center,
                 'radius': 0, 'angle': (0, 0), 'dir': -1, 'hit': 0, 'width': 0}
        if self.start:
            if self.width >= 1:
                complete_offset = self.center - offset
                self.radius += round(self.exp_index)
                self.width -= round(self.exp_index)
                self.exp_index = self.exp_index + .08 if self.width > 3 else self.exp_index + .01
                queue = {'layer': 99, 'type': 'circle', 'image': False,
                         'color': choice([self.color, self.second_color]),
                         'rect': self.empty_rect, 'pos': self.center if offset != (0, 0) else complete_offset,
                         'radius': self.radius, 'angle': (0, 0), 'dir': -1, 'hit': 0, 'width': self.width}
                self.hit_box_rect.x = complete_offset[0] - (self.radius / 2)
                self.hit_box_rect.y = complete_offset[1] - (self.radius / 2)
                self.hit_box_rect.w = self.radius
                self.hit_box_rect.h = self.radius

            elif self.width <= 0:
                self.start = False
                self.width = 15
                self.exp_index = 0
                self.center = pygame.math.Vector2()
                self.radius = 1
        return [queue]


class Colors:
    def __init__(self):
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.light_yellow = (244, 255, 69)
        self.green_forest = (85, 128, 85)
        self.green_plains = (139, 145, 80)
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)

    def flash(self):
        return choice([self.white, self.light_yellow, self.red])


class Point:
    def __init__(self, point):
        self.x = point[0]
        self.y = point[1]
        self.slope = 0

    def __add__(self, other):
        return Point((self.x + other.x, self.y + other.y))

    def __sub__(self, other):
        return Point((self.x - other.x, self.y - other.y))

    def __mul__(self, scalar):
        return Point((self.x * scalar, self.y * scalar))

    def __truediv__(self, scalar):
        if scalar == 0:
            scalar = .01
        return Point((self.x / scalar, self.y / scalar))

    def __len__(self):
        return int(hypot(self.x, self.y))

    def get(self):
        return (self.x, self.y)


def get_angle(start_pos, end_pos):
    origin = Point(start_pos)
    target = Point(end_pos)
    displacement = target - origin
    length = len(displacement)
    slope = displacement / length
    start = origin + (slope * 0)
    end = origin + (slope * (int(length) + 1))
    start = start.get()
    end = end.get()
    return np.rad2deg(np.arctan2(end[1] - start[1], end[0] - start[0])) * -1, slope.get()
