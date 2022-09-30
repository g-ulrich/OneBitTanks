import pygame
from assets import TankAssets, get_angle, Explosion, ExplosionAssets, ExplosionSprite
from datetime import datetime
from math import cos, sin
from random import randint, choice


class Player:
    def __init__(self, general):
        self.general = general
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
        self.tank_hit_box_rect = pygame.Rect(self.tank_rect.x + 5,
                                             self.tank_rect.y + 5,
                                             self.tank_rect.w - 10,
                                             self.tank_rect.h - 10)
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
        self.tank_exhaust = []
        self.tank_exhaust_timer = datetime.now()
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
        self.show_debug = False
        # bullets
        self.player_hit = False
        self.bullets = []
        self.bullet_color = (255, 255, 255)  # (60, 121, 202)
        self.max_bullets = 5
        self.bullet_speed = 5
        self.bullet_radius = 4
        self.bullet_timer = datetime.now()
        self.bullet_delete_timer = datetime.now()
        self.bullet_expolsion = Explosion()
        # explosions
        self.explosion_assets = ExplosionAssets()

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

    def check_tank_hit_boundary(self, border_rect, dot_array):
        tr = self.tank_hit_box_rect
        dot_in = False, 0
        for index, dot in enumerate(dot_array, 1):
            if not border_rect.collidepoint(dot):
                dot_in = True, index
                break
        if tr.top <= border_rect.top:
            return True, dot_in
        if tr.bottom >= border_rect.bottom:
            return True, dot_in
        if tr.left <= border_rect.left:
            return True, dot_in
        if tr.right >= border_rect.right:
            return True, dot_in

        return False, dot_in

    def movement(self, surface, controls, slope, border_rect, tank_border_box_rect, dot_array):
        obj = controls.obj['1']
        if (datetime.now() - self.timer).total_seconds() > .05:
            self.timer = datetime.now()
            self.sprite_index = self.sprite_index + 1 if self.sprite_index < self.index_max else 0
        if obj['right'] or obj['left'] or obj['up'] or obj['down']:
            if obj['up']:
                self.forward_motor_sound()
                self.dir = pygame.math.Vector2((slope[0] * self.tank_speed, slope[1] * self.tank_speed))
                hit, dot_in = self.check_tank_hit_boundary(tank_border_box_rect, dot_array)
                if not hit or dot_in[1] != 1:
                    self.tank_center += self.dir
            if obj['left']:
                self.motor_turn_sound()
                self.tank_angle += self.tank_speed
                self.dot_index -= self.tank_speed / (self.tank_circle_radius + self.tank_speed + .5)
            if obj['down']:
                self.backward_motor_sound()
                self.dir = pygame.math.Vector2(slope)
                hit, dot_in = self.check_tank_hit_boundary(border_rect, dot_array)
                if not hit or dot_in[1] != 2:
                    self.tank_center -= self.dir
            if obj['right']:
                self.motor_turn_sound()
                self.tank_angle -= self.tank_speed
                self.dot_index += self.tank_speed / (self.tank_circle_radius + self.tank_speed + .5)
        else:
            self.img = self.assets.idle[self.sprite_index]

        if obj['right'] or obj['left'] or obj['up'] or obj['down']:
            self.img = self.assets.up[self.sprite_index]

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

    def blit_tracks(self, surface, angle, rect, controls):
        # blit tracks
        obj = controls.obj['1']
        if obj['right'] or obj['left'] or obj['up'] or obj['down']:
            if (datetime.now() - self.tracks_timer).total_seconds() > .1:
                self.tracks_timer = datetime.now()
                self.tracks.append([angle - 90, rect, datetime.now()])
        for index, arr in enumerate(self.tracks, 0):
            surface.blit(pygame.transform.rotate(self.assets.tracks, arr[0]), arr[1].topleft)
            if (datetime.now() - arr[2]).total_seconds() > 5:
                try:
                    del self.tracks[index]
                except:
                    del self.tracks[index]

    def blit_player_debug(self, surface, controls, angle, slope, dot_array):
        text_array = [f'Tank Angle: {round(angle, 3)}',
                      f'Tank Slope: {[round(i, 3) for i in slope]}',
                      f'Tank Center: {self.tank_rect.center}',
                      f'Cursor Pos: {[round(i, 3) for i in controls.obj["1"]["mouse"]]}']
        for index, text in enumerate(text_array, 0):
            t = self.assets.font.bold.render(text, True, (255, 255, 255))
            surface.blit(t, (10, (t.get_height() * index) + 10))
        pygame.draw.rect(surface, (255, 255, 0), self.tank_rect, 2)
        pygame.draw.rect(surface, (0, 255, 0), self.tank_hit_box_rect, 2)
        pygame.draw.circle(surface, (0, 255, 0), self.tank_rect.center, self.tank_circle_radius, 1)
        for dot in dot_array:
            pygame.draw.line(surface, (255, 0, 0), self.tank_rect.center, dot)
            pygame.draw.circle(surface, (0, 255, 0), dot, 3)

    def hit_player_tank(self, arr):
        return True if self.tank_hit_box_rect.collidepoint(arr[2]) and (
                datetime.now() - arr[3]).total_seconds() > 1 else False

    def shoot(self, surface, controls, slope, angle, internal_level_rect_hit_box):
        if controls.obj['1']['left_click'] and not len(self.bullets) >= self.max_bullets:
            if (datetime.now() - self.bullet_timer).total_seconds() > .2:
                # center_vector = pygame.math.Vector2((new_bullet_rect.centerx - (new_bullet_rect.w / 2), new_bullet_rect.centery - (new_bullet_rect.h / 2)))
                center_vector = pygame.math.Vector2(self.tank_center)
                tank_explosion = ExplosionSprite(self.explosion_assets.small_explosion_1_images)
                tank_explosion.start(center_vector, slope)
                self.bullets.append([0, slope, center_vector, datetime.now(), tank_explosion, angle])
                self.sounds.play_shot()
                # new_bullet_rect.center = new_bullet_rect.center - (pygame.math.Vector2(slope) * 5)
                self.bullet_timer = datetime.now()
        for index, arr in enumerate(self.bullets, 0):
            slope = arr[1]
            center_v = arr[2]
            move_x, move_y = self.bullet_speed * slope[0], self.bullet_speed * slope[1]
            center_v.x += move_x
            center_v.y += move_y
            for blip in range(3):
                if choice([True, False]):
                    rand_int = randint(2, 6 - blip)
                    # dust shadow desert color
                    pygame.draw.circle(surface, (173, 156, 104),
                                       (center_v.x - (slope[0] * (blip * 10)), 8 + center_v.y - (slope[1] * (blip * 10))),
                                       rand_int)
                    pygame.draw.circle(surface, (230, 230, 230),
                                       (center_v.x - (slope[0] * (blip * 10)), center_v.y - (slope[1] * (blip * 10))),
                                       rand_int)
            # desert color shadow
            pygame.draw.circle(surface, (173, 156, 104), (center_v.x, center_v.y + 8), 6)
            pygame.draw.circle(surface,
                               choice([(57, 61, 71), (54, 69, 79), (67, 70, 75)]),
                               center_v, 6)
            pygame.draw.circle(surface,
                               choice([(57, 61, 71), (54, 69, 79), (67, 70, 75)]),
                               center_v, randint(2, 6))
            # Bounce bullets
            lr = internal_level_rect_hit_box
            if center_v.x <= lr.left or center_v.x >= lr.right:
                self.sounds.play_hit_wall() if arr[0] == 0 else ""
                arr[0] += 1
                arr[1] = (slope[0] * -1, slope[1])
                angle, _ = get_angle(center_v, arr[1])
            if arr[2].y <= lr.top or arr[2].y >= lr.bottom:
                self.sounds.play_hit_wall() if arr[0] == 0 else ""
                arr[0] += 1
                arr[1] = (slope[0], slope[1] * -1)
                angle, _ = get_angle(center_v, arr[1])
            # check if bullet hits player:
            self.player_hit = self.hit_player_tank(arr)
            # destroy bullets
            if index >= self.max_bullets or arr[0] > 1 or self.player_hit:
                pygame.draw.circle(surface, (255, 255, 255), arr[2], self.bullet_radius * 2)
                self.sounds.play_fart()
                try:
                    del self.bullets[index]
                except:
                    del self.bullets[index]
        # return new_bullet_rect

    def blit_tank_exhaust(self, surface):
        if (datetime.now() - self.tank_exhaust_timer).total_seconds() > .05:
            self.tank_exhaust_timer = datetime.now()
            self.tank_exhaust.append([self.tank_rect.center, randint(3, 8)])
        for index, arr in enumerate(self.tank_exhaust, 0):
            arr[1] -= .21
            pygame.draw.circle(surface, choice([(255, 255, 255), (200, 200, 200),
                                                (127, 127, 127)]), arr[0], arr[1])
            if arr[1] <= 0:
                try:
                    del self.tank_exhaust[index]
                except:
                    del self.tank_exhaust[index]

    def get_dot_array(self, center):
        # # top
        dots = []
        radius = 45
        top = pygame.math.Vector2(center)
        top.x = top.x + radius * cos(self.dot_index)
        top.y = top.y + radius * sin(self.dot_index)
        dots.append(top)
        bottom = pygame.math.Vector2(center)
        bottom.x = bottom.x - radius * cos(self.dot_index)
        bottom.y = bottom.y - radius * sin(self.dot_index)
        dots.append(bottom)
        return dots

    def blit_tracks_tank_gun(self, surface, controls, internal_level_rect_hit_box, tank_border_box_rect):
        # move dot around circumference of player circle.
        dot_array = self.get_dot_array(self.tank_rect.center)
        dot = dot_array[0]
        # find angle from player center to dot. (circle is stationary)
        angle, slope = get_angle(self.tank_rect.center, dot)
        # blit debug info
        self.blit_player_debug(surface, controls, angle, slope, dot_array) if self.show_debug else ""
        # move player based on simple player input. left right is axial and up down is positional movement
        self.movement(surface, controls, slope, internal_level_rect_hit_box, tank_border_box_rect, dot_array)
        # main tank
        tank_img, new_tank_rect = self.blit_rotate_center(self.img, angle - 90)
        new_tank_rect.center = self.tank_center
        # shadow tank
        tank_shadow_img, new_tank_shadow_rect = self.blit_rotate_center(self.assets.shadow, angle - 90)
        new_tank_shadow_rect.center = (self.tank_center[0], self.tank_center[1] + 4)
        # re-assign rect
        self.tank_rect = new_tank_rect
        self.tank_hit_box_rect.center = self.tank_rect.center
        # blit tracks
        self.blit_tracks(surface, angle, new_tank_rect, controls)
        # blit exhaust
        self.blit_tank_exhaust(surface)
        # blit tank shadow
        surface.blit(tank_shadow_img, new_tank_shadow_rect)
        # blit tank
        surface.blit(tank_img, new_tank_rect)
        self.tank_gun_rect.center = self.tank_center
        angle, slope = get_angle(self.tank_gun_rect.center, controls.obj['1']['mouse'])
        # - 90 to align with mouse
        new_gun_shadow_img, new_gun_shadow_rect = self.blit_rotate_center(self.assets.gun_shadow, angle - 90)
        new_gun_shadow_rect.center = (self.tank_center[0], self.tank_center[1] + 2)
        new_gun_img, new_gun_rect = self.blit_rotate_center(self.assets.gun, angle - 90)
        new_gun_rect.center = self.tank_center
        # blit bullet
        self.shoot(surface, controls, slope, angle,
                   internal_level_rect_hit_box)
        # blit gun image shadow
        surface.blit(new_gun_shadow_img, new_gun_shadow_rect)
        # blit gun image
        surface.blit(new_gun_img, new_gun_rect)
        # blit bullet_explosions
        for arr in self.bullets:
            arr[4].update(surface)

    def update(self, surface, controls, internal_level_rect_hit_box, tank_border_box_rect):
        self.blit_tracks_tank_gun(surface, controls, internal_level_rect_hit_box, tank_border_box_rect)
