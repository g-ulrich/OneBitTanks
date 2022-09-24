import pygame, os
from random import choice


class Sounds:
    def __init__(self):
        pygame.mixer.init()
        # music pygame object and string name
        self.music_objects = self.get_music_objects()
        self.song_obj = choice(self.music_objects)
        # self.play_menu_song()
        # character
        self.motor = pygame.mixer.Sound('assets/sounds/tank/motor.wav')
        self.gun_shot = pygame.mixer.Sound('assets/sounds/gun/shot.wav')
        self.gun_hit_wall = pygame.mixer.Sound('assets/sounds/gun/hit_wall.wav')
        self.gun_hit_wall.set_volume(.05)
        self.gun_farts = [pygame.mixer.Sound('assets/sounds/gun/fart.wav'), pygame.mixer.Sound('assets/sounds/gun/fart2.wav')]
        self.gun_hurt = pygame.mixer.Sound('assets/sounds/gun/hurt.wav')

    def get_music_objects(self):
        file_names = os.listdir("assets/sounds/music")
        items = []
        for name in file_names:
            items.append({'song': pygame.mixer.Sound(f"assets/sounds/music/{name}"), 'name': name})
        return items

    def skip_song(self):
        self.song_obj['song'].fadeout(1000)
        self.song_obj = choice(self.music_objects)
        self.play_song()

    def play_menu_song(self):
        song = [i['song'] for i in self.music_objects if "Easy Peasy" in i['name']][0]
        song.set_volume(.3)
        song.play(-1)

    def play_motor(self):
        self.motor.set_volume(.1)
        self.motor.play()

    def stop_motor(self):
        self.motor.stop()

    def play_shot(self):
        self.gun_shot.set_volume(choice([.2, .1]))
        self.gun_shot.play()

    def play_hit_wall(self):
        self.gun_hit_wall.play()

    def play_fart(self):
        fart = choice(self.gun_farts)
        fart.play()

    def play_hurt(self):
        self.gun_hurt.set_volume(choice([.2, .1]))
        self.gun_hurt.play()

