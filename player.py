import pygame
from assets import TankAssets, get_angle
from datetime import datetime


class Player:
    def __init__(self, general):
        self.sounds = general.sounds
        self.assets = TankAssets()
        # iterating through images
        self.sprite_index = 0
        self.index_max = len(self.assets.idle) - 1
        # timer for frames
        self.timer = datetime.now()
        # store images
        self.img = self.assets.idle[0]
        # rect for movement
        self.tank_rect = self.img.get_rect()
        self.tank_gun_rect = self.assets.gun.get_rect()
        pos = (200, 200)
        self.tank_rect.topleft = pos
        self.tank_gun_rect.topleft = pos
        # dir of tank
        self.tank_angle = 0
        self.dir = pygame.math.Vector2()
        self.last_dir = pygame.math.Vector2()
        self.turning = []
        # tracks
        self.tracks = []
        self.tracks_timer = datetime.now()

    def update_tank_angle(self, desired_angle, neg=False):
        if self.tank_angle < 0:
            self.tank_angle = 0
        if self.tank_angle > 360:
            self.tank_angle = 360
        if desired_angle - 4 <= self.tank_angle <= desired_angle + 4:
            self.tank_angle = desired_angle
        else:
            self.tank_angle = self.tank_angle - 2 if neg else self.tank_angle + 2
        print(self.tank_angle)

    def movement(self, controls):
        obj = controls.obj['1']
        if (datetime.now() - self.timer).total_seconds() > .05:
            self.timer = datetime.now()
            self.sprite_index = self.sprite_index + 1 if self.sprite_index < self.index_max else 0
        self.dir = pygame.math.Vector2((0, 0))
        if obj['up'] or obj['right'] or obj['left'] or obj['down']:
            if obj['up']:
                self.dir = pygame.math.Vector2((0, -1))
                self.update_tank_angle(0, neg=True)
                # self.img = self.assets.up[self.sprite_index]
            if obj['left']:
                self.dir = pygame.math.Vector2((-1, 0))
                self.update_tank_angle(90, neg=True)
                # self.img = self.assets.left[self.sprite_index]
            if obj['down']:
                self.dir = pygame.math.Vector2((0, 1))
                self.update_tank_angle(180)
                # self.img = self.assets.up[self.sprite_index]
            if obj['right']:
                self.dir = pygame.math.Vector2((1, 0))
                self.update_tank_angle(270)
                # self.img = self.assets.right[self.sprite_index]
        else:
            self.img = self.assets.idle[self.sprite_index]
        if self.tank_angle % 90 == 0:
            self.tank_rect.topleft += 2 * self.dir
        self.tank_gun_rect.topleft = self.tank_rect.topleft
        if self.dir != (0, 0):
            self.img = self.assets.up[self.sprite_index]
            self.last_dir = self.dir

    def blit_rotate_center(self, image, angle, blit_obj=False):
        origin_pos = (self.tank_rect.w / 2, self.tank_rect.h / 2)
        pos = (self.tank_rect.x + origin_pos[0], self.tank_rect.y + origin_pos[1] / 2)
        # offset from pivot to center
        image_rect = image.get_rect(topleft=(pos[0] - origin_pos[0], pos[1] - origin_pos[1]))
        offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
        # roatated offset from pivot to center
        rotated_offset = offset_center_to_pivot.rotate(-angle)
        # roatetd image center
        rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
        # get a rotated image
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)
        # rotate and blit the image
        return rotated_image, rotated_image_rect

    def blit_tracks_tank_gun(self, surface, controls):
        if (datetime.now() - self.tracks_timer).total_seconds() > .05:
            if self.dir != (0, 0):
                self.sounds.play_motor()
            self.tracks_timer = datetime.now()
            self.tracks.append([self.blit_rotate_center(self.assets.tracks, self.tank_angle), datetime.now()])
        for index, arr in enumerate(self.tracks, 0):
            surface.blit(arr[0][0], arr[0][1])
            if (datetime.now() - arr[1]).total_seconds() > 1:
                try:
                    del self.tracks[index]
                except:
                    del self.tracks[index]
        # blit tank this way to center the spinner, for turning.
        img, rect = self.blit_rotate_center(self.img, self.tank_angle)
        surface.blit(img, rect)
        angle, slope = get_angle(self.tank_gun_rect.center, controls.obj['1']['mouse'])
        # - 90 to align with mouse
        img, rect = self.blit_rotate_center(self.assets.gun, angle - 90)
        surface.blit(img, rect)

    def update(self, surface, controls):
        self.movement(controls)
        self.blit_tracks_tank_gun(surface, controls)

