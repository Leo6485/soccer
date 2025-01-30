import pygame as pg
from math import sqrt
from time import time

class Enemy():
    def __init__(self, id, name):
        self.id = id
        self.team = self.id%2 + 1
        self.size = 25
        self.pos = pg.Vector2(0, 0)
        self.interpolated_pos = pg.Vector2(0, 0)
        self.interpolation_lv = 2

        self.texture = None
        self.name = name
        self.name_text = pg.font.Font(None, 25).render(self.name, True, (255, 50, 50))

        self.respawn_ts = 0
        self.run = 0
        self.dir = 0
        self.last_update = time()
    
    def reset_name(self, name):
        self.name = name
        self.name_text = pg.font.Font(None, 25).render(self.name, True, (255, 50, 50))

    def update(self):
        crr_time = time()
        if (crr_time - self.respawn_ts < 1.5):
            self.interpolated_pos = self.pos
        else:
            self.interpolated_pos += (self.pos - self.interpolated_pos) / self.interpolation_lv

    def draw(self, screen, scale, padding):
        scaled_pos = self.interpolated_pos * scale + padding
        text_rect = self.name_text.get_rect(center=(int(scaled_pos.x), int(scaled_pos.y - self.size * scale - 10)))
        screen.blit(self.name_text, text_rect)
        frame_y = 64 if self.dir else 0
        frame_x = int((time() * 6) % 3) * 64
        frame_x = frame_x if self.run else 128

        texture_rect = pg.Rect(frame_x, frame_y, 64, 64)
        screen.blit(self.texture, (int(self.interpolated_pos.x - 32), int(self.interpolated_pos.y - 42)), texture_rect)

class Ball:
    def __init__(self, scale):
        self.size = 80
        self.pos = pg.Vector2(100, 100)
        self.interpolated_pos = pg.Vector2(100, 100)
        self.interpolation_lv = 2

        self.texture = pg.image.load("assets/textures/disc/disc.png")
        self.texture = pg.transform.scale(self.texture, (self.size * 4.5 * scale, self.size * 4.5 * scale))
    
    def update(self):
        self.interpolated_pos += (self.pos - self.interpolated_pos) / self.interpolation_lv

    def draw(self, screen, scale, padding):
        scaled_pos = self.interpolated_pos * scale + padding
        texture_rect = self.texture.get_rect(center=(int(scaled_pos.x), int(scaled_pos.y + 8 * scale)))
        screen.blit(self.texture, texture_rect)
        # pg.draw.circle(screen, (255, 255, 255), self.pos, self.size, width=2)

    def calc_dist(self, pos):
        d = pos - self.interpolated_pos
        return d, d.length()
