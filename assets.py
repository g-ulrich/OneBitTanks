import pygame
from math import hypot
import json
from random import randint, choice
from datetime import datetime
import numpy as np


class Walls:
    def __init__(self, general):
        self.general = general
        self.show_debug = True
        self.screen_rect = general.level_rect
        self.upper_level_img, self.lower_level_img, self.level_rect, self.level_outline_rect, self.level_wall_hit_box_rect, self.tank_border_box_rect = self.get_desert_rects()

    def get_desert_rects(self):
        #  only called in def __init__()
        upper_level_img = pygame.image.load('assets/images/levels/desert/upper_level.png').convert()
        upper_level_img.set_colorkey((0, 0, 0))
        lower_level_img = pygame.image.load('assets/images/levels/desert/lower_level.png').convert()
        lower_level_img.set_colorkey((0, 0, 0))
        rect = upper_level_img.get_rect()
        outline_rect = pygame.Rect(
            self.screen_rect.centerx - (rect.w / 2),
            self.screen_rect.centery - (rect.h / 2),
            rect.w, rect.h)
        size = 64
        wall_hit_box_rect = pygame.Rect(
            self.screen_rect.centerx - (rect.w / 2) + size + 2,
            self.screen_rect.centery - (rect.h / 2) + size,
            rect.w - (size * 2) + 8,
            rect.h - (size * 2) + 12)
        rect.center = (self.screen_rect.centerx - (rect.w / 2), self.screen_rect.centery - (rect.h / 2))
        tank_border_box_rect = pygame.Rect(
            wall_hit_box_rect.x + 25,
            wall_hit_box_rect.y + 20,
            wall_hit_box_rect.w - 50,
            wall_hit_box_rect.h - 50
        )
        return upper_level_img, lower_level_img, rect, outline_rect, wall_hit_box_rect, tank_border_box_rect

    def blit_debug(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), self.level_rect, 2)
        pygame.draw.rect(surface, (255, 0, 0), self.level_outline_rect, 2)
        pygame.draw.rect(surface, (255, 0, 0), self.level_wall_hit_box_rect, 2)
        pygame.draw.rect(surface, (255, 0, 0), self.tank_border_box_rect, 2)

    def blit_upper_level(self, surface):
        surface.blit(self.upper_level_img, self.level_rect.center)

    def blit_lower_level(self, surface):
        surface.blit(self.lower_level_img, self.level_rect.center)


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


class Cursor:
    def __init__(self):
        pygame.mouse.set_visible(False)
        self.pos = pygame.mouse.get_pos()
        self.sheet = SpriteSheet('assets/images/cursor/cursor.png')
        self.images = [
            self.sheet.get_image(0, 0, 11, 11),
            self.sheet.get_image(0, 11, 11, 11)
        ]
        self.images = [pygame.transform.scale(i, (32, 32)) for i in self.images]
        self.index = 0
        self.timer = datetime.now()

    def update(self, surface):
        if (datetime.now() - self.timer).total_seconds() > 1:
            self.timer = datetime.now()
            self.index = self.index + 1 if self.index < len(self.images) - 1 else 0
        x, y = pygame.mouse.get_pos()
        surface.blit(self.images[self.index], (x - 16, y - 16))


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
        self.size = 50
        self.idle, self.up, self.gun, self.gun_hit, self.tank_hit, _, self.shadow, self.gun_shadow = self.get_sprite_list(
            'assets/images/tanks/tank')
        self.tracks = self.get_tracks()

    def get_tracks(self):
        tracks = pygame.image.load('assets/images/tanks/desert_tracks.png').convert()
        tracks.set_colorkey((0, 0, 0))
        tracks = pygame.transform.scale(tracks, (self.size, self.size))
        return tracks

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
        images = [pygame.transform.scale(i, (self.size, self.size)) for i in images]
        return images[0:3], images[4:7], images[8], images[9], images[10], images[11], images[12], images[13]


class ExplosionAssets:
    def __init__(self):
        self.small_explosion_1_images = self.get_sprite_list(size=64,
                                                             path='assets/images/tanks/small_explosion_1',
                                                             file_name='small_explosion_1')

    def read_json_file(self, path):
        output = ""
        with open(path) as f:
            for line in f:
                output += line
        return json.loads(output)

    def get_sprite_list(self, size, path, file_name):
        sheet = SpriteSheet(f"{path}/{file_name}.png")
        sheet_map = self.read_json_file(f"{path}/{file_name}.json")
        frames = [sheet_map['frames'][key]['frame'] for key in sheet_map['frames'].keys()]
        images = [sheet.get_image(i['x'], i['y'], i['w'], i['h'], color_key=(0, 0, 0)) for i in frames]
        images = [pygame.transform.scale(i, (size, size)) for i in images]
        return images


class ExplosionSprite:
    def __init__(self, images):
        """
        takes array of images
        """
        self.images = images
        self.rect = self.images[0].get_rect()
        self.index = 0
        self.timer = datetime.now()
        self.center = pygame.math.Vector2()

    def start(self, center, slope):
        self.center.x = center[0] - (self.rect.w /2) + (slope[0] * 30)
        self.center.y = center[1] - (self.rect.h/2) + (slope[1] * 30)
        self.rect.center = center

    def update(self, surface):
        if (datetime.now() - self.timer).total_seconds() > .02:
            self.timer = datetime.now()
            self.index += 1
        if self.index <= len(self.images) - 1:
            surface.blit(self.images[self.index], self.center)


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
