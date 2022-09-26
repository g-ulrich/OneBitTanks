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
        self.forward_sound_timer = datetime.now()
        self.backward_sound_timer = datetime.now()
        self.turn_sound_timer = datetime.now()
        # player debug
        self.show_debug = True
        # bullets
        self.bullets = []
        self.bullet_color = (60, 121, 202)
        self.max_bullets = 5
        self.bullet_speed = 4
        self.bullet_radius = 4
        self.bullet_timer = datetime.now()
        self.bullet_delete_timer = datetime.now()

    def motor_turn_sound(self):
        if (datetime.now() - self.turn_sound_timer).total_seconds() > .08:
            self.turn_sound_timer = datetime.now()
            self.sounds.play_motor_turn()

    def forward_motor_sound(self):
        if (datetime.now() - self.forward_sound_timer).total_seconds() > .1:
            self.forward_sound_timer = datetime.now()
            self.sounds.play_motor()

    def backward_motor_sound(self):
        if (datetime.now() - self.backward_sound_timer).total_seconds() > .18:
            self.backward_sound_timer = datetime.now()
            self.sounds.play_motor()

    def movement(self, surface, controls, slope):
        obj = controls.obj['1']

        if (datetime.now() - self.timer).total_seconds() > .05:
            self.timer = datetime.now()
            self.sprite_index = self.sprite_index + 1 if self.sprite_index < self.index_max else 0
        if obj['right'] or obj['left'] or obj['up'] or obj['down']:
            if obj['up']:
                self.forward_motor_sound()
                self.tank_center += pygame.math.Vector2((slope[0] * self.tank_speed, slope[1] * self.tank_speed))
            if obj['left']:
                self.motor_turn_sound()
                self.tank_angle += self.tank_speed
                self.dot_index -= self.tank_speed / (self.tank_circle_radius + self.tank_speed + .5)
            if obj['down']:
                self.backward_motor_sound()
                self.tank_center -= pygame.math.Vector2(slope)
            if obj['right']:
                self.motor_turn_sound()
                self.tank_angle -= self.tank_speed
                self.dot_index += self.tank_speed / (self.tank_circle_radius + self.tank_speed + .5)
        else:
            self.img = self.assets.idle[self.sprite_index]
        if obj['right'] or obj['left'] or obj['up'] or obj['down']:
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

    def blit_tracks(self, surface, angle, rect):
        # blit tracks
        if (datetime.now() - self.tracks_timer).total_seconds() > .1:
            self.tracks_timer = datetime.now()
            self.tracks.append([angle - 90, rect, datetime.now()])
        for index, arr in enumerate(self.tracks, 0):
            surface.blit(pygame.transform.rotate(self.assets.tracks, arr[0]), arr[1].topleft)
            if (datetime.now() - arr[2]).total_seconds() > 20:
                try:
                    del self.tracks[index]
                except:
                    del self.tracks[index]

    def blit_player_debug(self, surface, angle, slope, dot):
        text = self.assets.font.bold.render(
            f"angle: {round(angle, 3)}, slope: {[round(i, 3) for i in slope]}, center: {self.tank_rect.center}", True,
            (255, 255, 255))
        surface.blit(text, (10, 10))
        pygame.draw.line(surface, (255, 0, 0), self.tank_rect.center, dot)
        pygame.draw.circle(surface, (0, 255, 0), self.tank_rect.center, self.tank_circle_radius, 1)
        pygame.draw.circle(surface, (0, 255, 0), dot, 3)

    def shoot(self, surface, controls, new_gun_rect, slope):
        if controls.obj['1']['left_click']:
            if (datetime.now() - self.bullet_timer).total_seconds() > .5:
                self.sounds.play_shot()
                new_gun_rect.center = new_gun_rect.center - (pygame.math.Vector2(slope) * 5)
                self.bullet_timer = datetime.now()
                self.bullets.append([0, slope, pygame.math.Vector2(new_gun_rect.center), datetime.now()])
        for index, arr in enumerate(self.bullets, 0):
            arr[2].x += self.bullet_speed * arr[1][0]
            arr[2].y += self.bullet_speed * arr[1][1]
            pygame.draw.circle(surface, self.bullet_color, arr[2], self.bullet_radius)
            # TODO check bullet collide with anything
            if index >= self.max_bullets - 1 or (datetime.now() - arr[-1]).total_seconds() > 2:
                try:
                    del self.bullets[index]
                except:
                    del self.bullets[index]
        return new_gun_rect

    def blit_tracks_tank_gun(self, surface, controls):
        # move dot around circumference of player circle.
        dot = pygame.math.Vector2(self.tank_rect.center)
        dot.x = dot.x + self.tank_circle_radius * cos(self.dot_index)
        dot.y = dot.y + self.tank_circle_radius * sin(self.dot_index)
        # find angle from player center to dot. (circle is stationary)
        angle, slope = get_angle(self.tank_rect.center, dot)
        # blit debug info
        self.blit_player_debug(surface, angle, slope, dot) if self.show_debug else ""
        # move player based on simple player input. left right is axial and up down is positional movement
        self.movement(surface, controls, slope)

        tank_img, new_tank_rect = self.blit_rotate_center(self.img, angle - 90)
        new_tank_rect.center = self.tank_center
        # blit tracks
        self.blit_tracks(surface, angle, new_tank_rect)
        # blit tank
        surface.blit(tank_img, new_tank_rect)
        self.tank_gun_rect.center = self.tank_center
        angle, slope = get_angle(self.tank_gun_rect.center, controls.obj['1']['mouse'])
        # - 90 to align with mouse
        new_gun_img, new_gun_rect = self.blit_rotate_center(self.assets.gun, angle - 90)
        new_gun_rect.center = self.tank_center
        # blit bullet
        new_gun_rect = self.shoot(surface, controls, new_gun_rect, slope)
        # if controls.obj['1']['left_click']:
        #     if (datetime.now() - self.bullet_timer).total_seconds() > .5:
        #         new_gun_rect.center = new_gun_rect.center - (pygame.math.Vector2(slope) * 3)
        # blit gun image
        surface.blit(new_gun_img, new_gun_rect)

    def update(self, surface, controls):
        self.blit_tracks_tank_gun(surface, controls)
        # self.movement(surface, controls)
