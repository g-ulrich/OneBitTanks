import pygame
from assets import TankAssets, get_angle
from datetime import datetime
from math import cos, sin


class Player:
    def __init__(self, general):
        self.screen_rect = general.screen_surface.get_rect()
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
        pos = (
        (general.screen_width / 2) - (self.tank_rect.w / 2), (general.screen_height / 2) - (self.tank_rect.h / 2))
        self.tank_rect.topleft = pos
        self.tank_gun_rect.topleft = pos
        # for calculating angle and slope
        self.dot_index = 0
        self.tank_circle_radius = 55
        self.tank_slope = 0
        self.tank_speed = 2
        self.tank_center = pos
        # dir of tank
        self.tank_angle = 270
        self.dir = pygame.math.Vector2()
        self.last_dir = pygame.math.Vector2()
        # tracks
        self.tracks = []
        self.tracks_timer = datetime.now()

    def update_tank_angle(self, surface, neg=True):
        # if self.tank_angle < 0:
        #     self.tank_angle = 0
        # if self.tank_angle > 360:
        #     self.tank_angle = 360
        # if desired_angle - 4 <= self.tank_angle <= desired_angle + 4:
        #     self.tank_angle = desired_angle
        # else:
        #     self.tank_angle = self.tank_angle - 2 if neg else self.tank_angle + 2
        pass

    def movement(self, surface, controls):
        obj = controls.obj['1']
        if (datetime.now() - self.timer).total_seconds() > .05:
            self.timer = datetime.now()
            self.sprite_index = self.sprite_index + 1 if self.sprite_index < self.index_max else 0
        # self.dir = pygame.math.Vector2((0, 0))
        if obj['right'] or obj['left']:
            # if obj['up']:
            #     self.dir.y = -1
            if obj['left']:
                self.tank_angle += self.tank_speed
                self.dot_index -= self.tank_speed / (self.tank_circle_radius + self.tank_speed + .5)
            # elif obj['down']:
            #     self.dir.y = 1
            if obj['right']:
                self.tank_angle -= self.tank_speed
                self.dot_index += self.tank_speed / (self.tank_circle_radius + self.tank_speed + .5)
            self.update_tank_angle(surface)
        else:
            self.img = self.assets.idle[self.sprite_index]
        if self.dir != (0, 0) or obj['left'] or obj['right']:
            self.img = self.assets.up[self.sprite_index]
            self.last_dir = self.dir

    def blit_rotate_center(self, image, angle):
        origin_pos = (self.tank_rect.w / 2, self.tank_rect.h / 2)
        pos = (self.tank_rect.centerx + origin_pos[0], self.tank_rect.centery + origin_pos[1] / 2)
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
        dot = pygame.math.Vector2(self.tank_rect.center)
        dot.x = dot.x + self.tank_circle_radius * cos(self.dot_index)
        dot.y = dot.y + self.tank_circle_radius * sin(self.dot_index)
        angle, slope = get_angle(self.tank_rect.center, dot)
        text = self.assets.font.bold.render(
            f"angle: {round(angle, 3)}, slope: {[round(i, 3) for i in slope]}, center: {self.tank_rect.center}", True,
            (255, 255, 255))
        surface.blit(text, (10, 10))
        pygame.draw.line(surface, (255, 0, 0), self.tank_rect.center, dot)
        pygame.draw.circle(surface, (0, 255, 0), self.tank_rect.center, self.tank_circle_radius, 1)
        pygame.draw.circle(surface, (0, 255, 0), dot, 3)
        if controls.obj['1']['up']:
            self.tank_center += pygame.math.Vector2(slope)
        if controls.obj['1']['down']:
            self.tank_center -= pygame.math.Vector2(slope)
        tank_img, rect = self.blit_rotate_center(self.img, angle - 90)
        rect.center = self.tank_center

        # blit tracks
        if (datetime.now() - self.tracks_timer).total_seconds() > .1:
            if self.dir != (0, 0):
                self.sounds.play_motor()
            self.tracks_timer = datetime.now()
            self.tracks.append([angle - 90, rect, datetime.now()])
        for index, arr in enumerate(self.tracks, 0):
            surface.blit(pygame.transform.rotate(self.assets.tracks, arr[0]), arr[1].topleft)
            if (datetime.now() - arr[2]).total_seconds() > 10:
                try:
                    del self.tracks[index]
                except:
                    del self.tracks[index]

        surface.blit(tank_img, rect)

        #
        #
        self.tank_gun_rect.center = self.tank_center
        angle, slope = get_angle(self.tank_gun_rect.center, controls.obj['1']['mouse'])
        # - 90 to align with mouse
        img, rect = self.blit_rotate_center(self.assets.gun, angle - 90)
        # rect.center = self.tank_center
        rect.center = self.tank_center
        surface.blit(img, rect)

    def update(self, surface, controls):
        self.blit_tracks_tank_gun(surface, controls)
        self.movement(surface, controls)
