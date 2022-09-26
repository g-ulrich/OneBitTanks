import pygame
from player import Player
from assets import Cursor


class SpriteGroup:
    def __init__(self, general, colors):
        self.colors = colors
        self.cursor = Cursor()
        self.surface = general.screen_surface
        self.player = Player(general)

    def update(self, controls):
        self.surface.fill((0, 0, 0))
        self.player.update(self.surface, controls)
        self.cursor.update(self.surface)
