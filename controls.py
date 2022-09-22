import pygame
from datetime import datetime
from assets import ControlsAssets


class Controls:
    def __init__(self, general):
        self.assets = ControlsAssets()
        self.sounds = general.sounds
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count()) if
                          "xbox" in pygame.joystick.Joystick(i).get_name().lower()]
        self.controller_type = [i.get_name() for i in self.joysticks][0] if self.joysticks else "Keyboard"
        pos = pygame.mouse.get_pos()
        self.joy_mouse = pygame.math.Vector2((0, 0))
        self.general = general
        self.screen_surface = self.general.screen_surface
        self.screen_surface_size = pygame.math.Vector2(self.screen_surface.get_size())
        self.level_rect = self.general.screen_surface.get_rect()
        self.screen_center_pos = pygame.math.Vector2((self.screen_surface.get_width() / 2, self.screen_surface.get_height() / 2))
        self.obj = {'pressed': [],
                    '1': {'up': False, 'down': False, 'right': False,
                           'left': False, 'space': False, 'run': False, 'esc': False,
                           'restart': False, 'zoom_in': False, 'zoom_out': False, 'mouse': self.screen_center_pos},
                    '2': {'up': False, 'down': False, 'right': False,
                           'left': False, 'space': False, 'run': False, 'esc': False,
                           'restart': False, 'zoom_in': False, 'zoom_out': False, 'mouse': self.screen_center_pos}
                    }
        self.message_rect_outer = pygame.Rect(200, self.screen_surface_size[1] - 200, self.screen_surface_size[0] - 400, 190)
        self.message_rect_inner = pygame.Rect(205, self.screen_surface_size[1] - 195, self.screen_surface_size[0] - 410, 180)
        self.message_start_pos = pygame.Rect(215, self.screen_surface_size[1] - 185, self.screen_surface_size[0] - 410, 180)

        self.message = ""
        self.title_obj = ""
        self.message_timer = datetime.now()
        self.message_sound_count = 0

    def update_controller_message(self, title, message):
        self.message = message
        self.title_obj = self.assets.large_font.bold.render(title, True, (0, 0, 0))
        self.message_timer = datetime.now()
        text_height = len(self.message.split("\n")) * (self.title_obj.get_height() + 10)
        self.message_rect_outer = pygame.Rect(200, self.screen_surface_size[1] - (text_height - 10),
                                              self.screen_surface_size[0] - 400, text_height + 15)
        self.message_rect_inner = pygame.Rect(205, self.screen_surface_size[1] - (text_height - 20),
                                              self.screen_surface_size[0] - 410, text_height - 30)
        self.message_start_pos = pygame.Rect(215, self.screen_surface_size[1] - (text_height - 70),
                                             self.screen_surface_size[0] - 410, text_height - 50)

    def blit_controller_message(self):
        if self.message != "":
            seconds = (datetime.now() - self.message_timer).total_seconds()
            if seconds < 2:
                if self.message_sound_count == 0:
                    self.sounds.play_bla()
                self.message_sound_count += 1
                collapse = (seconds * 200) if seconds > .1 else 0
                self.message_rect_outer.y += collapse
                self.message_rect_outer.h -= collapse
                self.message_rect_inner.y += collapse
                self.message_rect_inner.h -= collapse
                self.message_start_pos.y += collapse
                self.message_start_pos.h -= collapse
                pygame.draw.rect(self.screen_surface, (200, 200, 200), self.message_rect_outer)
                pygame.draw.rect(self.screen_surface, (255, 255, 255), self.message_rect_inner)
                self.screen_surface.blit(self.title_obj, (self.message_start_pos.x, self.message_start_pos.y - 40))
                for index, txt in enumerate(self.message.split("\n"), 0):
                    text = self.assets.font.bold.render(txt, True, (0, 0, 0))
                    self.screen_surface.blit(text, (self.message_start_pos.x, self.message_start_pos.y + (text.get_height() * index)))

                if self.message_rect_outer.h <= 0:
                    self.sounds.stop_bla()
                    self.message_sound_count = 0
                    # reset message
                    self.message = ""
                    # reset message boxes
                    self.message_rect_outer = pygame.Rect(200, self.screen_surface_size[1] - 200,
                                                          self.screen_surface_size[0] - 400, 190)
                    self.message_rect_inner = pygame.Rect(205, self.screen_surface_size[1] - 195,
                                                          self.screen_surface_size[0] - 410, 180)
                    self.message_start_pos = pygame.Rect(215, self.screen_surface_size[1] - 185,
                                                         self.screen_surface_size[0] - 410, 180)

    def start_rumble(self, duration=1):
        [i.rumble(1.0, 1.0, duration) for i in self.joysticks]

    def stop_rumble(self):
        [i.stop_rumble() for i in self.joysticks]

    def update_joysticks(self, event):
        if event.type == pygame.JOYDEVICEADDED:
            self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            self.controller_type = [i.get_name() for i in self.joysticks][0] if self.joysticks else "Keyboard"
        if event.type == pygame.JOYDEVICEREMOVED:
            self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            self.controller_type = [i.get_name() for i in self.joysticks][0] if self.joysticks else "Keyboard"

    def activated_pressed(self, pressed):
        # computer keys pressed
        self.obj['pressed'] = pressed
        if not self.joysticks:
            # player 1
            self.obj['1']['left'] = True if pressed[pygame.K_LEFT] else False
            self.obj['1']['down'] = True if pressed[pygame.K_DOWN] else False
            self.obj['1']['up'] = True if pressed[pygame.K_UP] else False
            self.obj['1']['right'] = True if pressed[pygame.K_RIGHT] else False
            self.obj['1']['run'] = True if pressed[pygame.K_c] else False
            self.obj['1']['space'] = True if pressed[pygame.K_SPACE] else False

            # player 2
            self.obj['2']['left'] = True if pressed[pygame.K_a] else False
            self.obj['2']['down'] = True if pressed[pygame.K_s] else False
            self.obj['2']['up'] = True if pressed[pygame.K_w] else False
            self.obj['2']['right'] = True if pressed[pygame.K_d] else False
            self.obj['2']['run'] = True if pressed[pygame.K_z] else False
            self.obj['2']['space'] = True if pressed[pygame.K_x] else False

            # both p1 and p2
            if pressed[pygame.K_r]:
                self.obj['1']['restart'] = True
                self.obj['2']['restart'] = True
            else:
                self.obj['1']['restart'] = False
                self.obj['2']['restart'] = False
            if pressed[pygame.K_1]:
                self.obj['1']['zoom_in'] = True
                self.obj['2']['zoom_in'] = True
            else:
                self.obj['1']['zoom_in'] = False
                self.obj['2']['zoom_in'] = False
            if pressed[pygame.K_2]:
                self.obj['1']['zoom_out'] = True
                self.obj['2']['zoom_out'] = True
            else:
                self.obj['1']['zoom_out'] = False
                self.obj['2']['zoom_out'] = False
            if pressed[pygame.K_ESCAPE]:
                self.obj['1']['esc'] = True
                self.obj['2']['esc'] = True
            else:
                self.obj['1']['esc'] = False
                self.obj['2']['esc'] = False

    def activated_controler(self, event):
        # xbox controller
        if self.joysticks:
            if event.type == pygame.JOYBUTTONDOWN:
                player_num = event.joy + 1
                if event.button == 1:
                    self.obj[f'{player_num}']['space'] = True
                if event.button == 3:
                    self.obj[f'{player_num}']['run'] = True
                if event.button == 4:
                    self.obj[f'{player_num}']['zoom_in'] = True
                if event.button == 5:
                    self.obj[f'{player_num}']['zoom_out'] = True
                if event.button == 6:
                    self.obj[f'{player_num}']['esc'] = True
                if event.button == 7:
                    self.obj[f'{player_num}']['restart'] = True
            if event.type == pygame.JOYBUTTONUP:
                player_num = event.joy + 1
                if event.button == 1:
                    self.obj[f'{player_num}']['space'] = False
                if event.button == 3:
                    self.obj[f'{player_num}']['run'] = False
                if event.button == 4:
                    self.obj[f'{player_num}']['zoom_in'] = False
                if event.button == 5:
                    self.obj[f'{player_num}']['zoom_out'] = False
                if event.button == 6:
                    self.obj[f'{player_num}']['esc'] = False
                if event.button == 7:
                    self.obj[f'{player_num}']['restart'] = False
            if event.type == pygame.JOYHATMOTION:
                # d pad
                player_num = event.joy + 1
                self.obj[f'{player_num}']['right'] = True if event.value == (1, 0) else False
                self.obj[f'{player_num}']['left'] = True if event.value == (-1, 0) else False
                self.obj[f'{player_num}']['up'] = True if event.value == (0, 1) else False
                self.obj[f'{player_num}']['down'] = True if event.value == (0, -1) else False
            if event.type == pygame.JOYAXISMOTION:
                # only use right joystick
                if event.axis == 2 or event.axis == 3:
                    self.joy_mouse[event.axis - 2] = event.value

    def update_mouse(self):
        if self.joysticks:
            if abs(self.joy_mouse.x) < 0.1:
                self.joy_mouse.x = 0
            if abs(self.joy_mouse.y) < 0.1:
                self.joy_mouse.y = 0
            self.obj[f'1']['mouse'].x += round(self.joy_mouse.x * 10, 4)
            self.obj[f'1']['mouse'].y += round(self.joy_mouse.y * 10, 4)
        else:
            pos = pygame.mouse.get_pos()
            self.obj[f'1']['mouse'].x = pos[0]
            self.obj[f'1']['mouse'].y = pos[1]
