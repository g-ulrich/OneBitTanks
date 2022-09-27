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
        self.surface.fill((28, 28, 28))
        self.player.update(self.surface, controls, self.walls.internal_level_rect_hit_box)
        self.walls.update(self.surface)
        # cursor blits last
        self.cursor.update(self.surface)
