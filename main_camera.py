import pygame
from player import Player
from assets import Cursor, Walls


class SpriteGroup:
    def __init__(self, general, colors):
        self.general = general
        self.colors = colors
        self.cursor = Cursor()
        self.surface = general.screen_surface
        self.player = Player(general)
        self.walls = Walls(general)

    def update(self, controls):
        self.surface.fill((194, 178, 128))
        self.walls.blit_upper_level(self.surface)
        self.player.update(self.surface, controls, self.walls.level_wall_hit_box_rect)
        self.walls.blit_lower_level(self.surface)
        # self.walls.blit_debug(self.surface)
        # cursor blits last
        self.cursor.update(self.surface)
