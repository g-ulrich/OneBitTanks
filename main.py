import pygame, sys
from general import General
from controls import Controls
from assets import Colors
from main_camera import SpriteGroup


class Game:
    def __init__(self):
        pygame.init()
        self.general = General()
        self.controls = Controls(self.general)
        # self.colors = Colors()
        # # based off mini game select self main_group needs to be updated again TODO
        self.main_group = SpriteGroup(self.general, Colors())

    def run(self):
        while self.general.run:
            # check player events
            pressed = pygame.key.get_pressed()
            self.controls.activated_pressed(pressed)
            self.controls.update_mouse()
            for event in pygame.event.get():
                self.controls.activated_controler(event)
                self.controls.update_joysticks(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            # run camera group
            self.main_group.update(self.controls)

            # update visuals every loop
            self.general.blit_fps(self.general.screen_surface)
            pygame.display.update()
            self.general.clock.tick(self.general.fps)


if __name__ == '__main__':
    game = Game()
    game.run()
