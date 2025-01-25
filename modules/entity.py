import pygame as pg
from math import sqrt
from time import time

class Enemy():
    def __init__(self, id, name):
        self.id = id
        self.size = 25
        self.pos = pg.Vector2(0, 0)
        self.name = name
        self.name_text = pg.font.Font(None, 25).render(self.name, True, (255, 50, 50))
        self.texture = None
        self.run = 0
        self.dir = 0
    
    def draw(self, screen):
        # pg.draw.circle(screen, (255, 0, 0), (int(self.pos[0]), int(self.pos[1])), self.size)
        text_rect = self.name_text.get_rect(center=(self.pos[0], self.pos[1] - self.size - 10))
        screen.blit(self.name_text, text_rect)
        frame_y = 64 if self.dir else 0
        frame_x = int((time() * 6) % 3) * 64
        
        frame_x = frame_x if self.run else 128

        texture_rect = pg.Rect(frame_x, frame_y, 64, 64)
        screen.blit(self.texture, (self.pos[0]-32, self.pos[1]-42), texture_rect)

class Ball:
    def __init__(self):
        self.size = 80
        self.pos = (100, 100)
        self.interpolated_pos = [100, 100]
        self.texture = pg.image.load("assets/textures/disc/disc.png")
        self.texture = pg.transform.scale(self.texture, (self.size * 4.5, self.size * 4.5))

    def draw(self, screen):
        self.interpolated_pos[0] += self.pos[0] - self.interpolated_pos[0]
        self.interpolated_pos[1] += self.pos[1] - self.interpolated_pos[1]

        texture_rect = self.texture.get_rect(center=self.interpolated_pos)
        screen.blit(self.texture, texture_rect)
        # pg.draw.circle(screen, (255, 255, 255), self.pos, self.size, width=2)

    def calc_dist(self, pos):
        d = [pos[0] - self.pos[0], pos[1] - self.pos[1]]
        return d, sqrt(d[0]**2 + d[1]**2)
