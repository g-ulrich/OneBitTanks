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
            self.screen_width = display.current_w - 100
            self.screen_height = display.current_h - 200
        # declare surface object
        self.screen_surface = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.level_rect = self.screen_surface.get_rect()
        self.fps = 60
        pygame.display.set_caption('One Bit Tanks - by Gabe U.')
        pygame.display.set_icon(pygame.image.load('assets/images/favicon.png'))
        self.clock = pygame.time.Clock()
        self.sounds = Sounds()
        self.font_25 = Font(25)

    def blit_fps(self, surface):
        txt = self.font_25.bold.render(f"FPS: {round(self.clock.get_fps(), 3)}", True, (255, 255, 255))
        surface.blit(txt, (10, self.screen_height - txt.get_height() - 10))
