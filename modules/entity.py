import pygame as pg
from math import sqrt

class Enemy:
    def __init__(self, id, name):
        self.id = id
        self.size = 25
        self.pos = pg.Vector2(0, 0)
        self.name = name
        self.name_text = pg.font.Font(None, 25).render(self.name, True, (255, 255, 255))
    
    def draw(self, screen):
        pg.draw.circle(screen, (255, 0, 0), (int(self.pos[0]), int(self.pos[1])), self.size)
        text_rect = self.name_text.get_rect(center=(self.pos[0], self.pos[1] - self.size - 10))
        screen.blit(self.name_text, text_rect)

class Ball:
    def __init__(self):
        self.size = 80
        self.pos = (100, 100)

    def draw(self, screen):        
        pg.draw.circle(screen, (150, 150, 150), self.pos, self.size)

    def calc_dist(self, pos):
        d = [pos[0] - self.pos[0], pos[1] - self.pos[1]]
        return d, sqrt(d[0]**2 + d[1]**2)
