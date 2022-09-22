import pygame
from sounds import Sounds
from assets import Font


class General:
    def __init__(self):
        full_screen = False
        self.run = True
        # set screen width and height
        display = pygame.display.Info()
        if full_screen:
            self.screen_width = display.current_w
            self.screen_height = display.current_h
        else:
            self.screen_width = 1000
            self.screen_height = 800
        # declare surface object
        self.screen_surface = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.fps = 60
        pygame.display.set_caption('One Bit Tanks - by Gabe U.')
        # pygame.display.set_icon(pygame.image.load('assets/favicon.png'))
        self.clock = pygame.time.Clock()
        self.sounds = Sounds()
        self.font_25 = Font(25)