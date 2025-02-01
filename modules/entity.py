import pygame as pg
from math import sqrt
from time import time
from modules.weapon import Weapon

class CharacterBaseData:
    def __init__(self, id, name):
        self.size = 25
        self.pos = pg.Vector2(100, 100)
        self.id = id
        self.name = name
        self.team = self.id%2
        
        # Timestamps
        self.respawn_ts = 0
        self.attack_ts = 0
        self.jail_ts = 0
        
        # Animações
        self.run = 0
        self.dir = 0
        
        self.weapon = Weapon()
        self.jail_textures = None

class Enemy(CharacterBaseData):
    def __init__(self, id, name):
        super().__init__(id, name)
        self.cursor_pos = pg.Vector2(0, 0)
        self.interpolated_pos = pg.Vector2(0, 0)
        self.interpolation_lv = 2

        self.texture = None
        self.name_text = pg.font.Font(None, 25).render(self.name, True, (255, 50, 50))

        self.last_update = time()
    
    def reset_name(self, name):
        self.name = name
        self.name_text = pg.font.Font(None, 25).render(self.name, True, (255, 50, 50))

    def update(self):
        crr_time = time()
        if crr_time - self.respawn_ts < 1.5:
            self.interpolated_pos = self.pos
        else:
            self.interpolated_pos += (self.pos - self.interpolated_pos) / self.interpolation_lv

    def draw(self, screen, player_pos=pg.Vector2(-1000, -1000)):
        distance = (self.interpolated_pos - player_pos).length()
        opacity = 128 if distance < 80 else 255

        # Draw textures
        draw_jail = time() - self.jail_ts < 1.5 and self.jail_textures
        if draw_jail:
            screen.blit(self.jail_textures[0], (self.interpolated_pos[0] - 64, self.interpolated_pos[1] - 80))

        text_rect = self.name_text.get_rect(center=(self.interpolated_pos[0], self.interpolated_pos[1] - self.size - 10))
        screen.blit(self.name_text, text_rect)

        frame_y = 64 if self.dir else 0
        frame_x = int((time() * 6) % 3) * 64
        frame_x = frame_x if self.run else 128

        texture_rect = pg.Rect(frame_x, frame_y, 64, 64)
        screen.blit(self.texture, (self.interpolated_pos[0] - 32, self.interpolated_pos[1] - 42), texture_rect)

        r_cursor_pos = self.cursor_pos - self.interpolated_pos
        self.weapon.draw(screen, self.interpolated_pos, self.id, r_cursor_pos, self.attack_ts)

        if draw_jail:
            screen.blit(self.jail_textures[1], (self.interpolated_pos[0] - 64, self.interpolated_pos[1] - 80))

class Ball:
    def __init__(self):
        self.size = 80
        self.pos = pg.Vector2(100, 100)
        self.interpolated_pos = pg.Vector2(100, 100)
        self.interpolation_lv = 2

        self.texture = pg.image.load("assets/textures/disc/disc.png")
        self.texture = pg.transform.scale(self.texture, (self.size * 4.5, self.size * 4.5))

    def update(self):
        self.interpolated_pos += (self.pos - self.interpolated_pos) / self.interpolation_lv

    def draw(self, screen):
        # Draw texture
        texture_rect = self.texture.get_rect(center=(self.interpolated_pos.x, self.interpolated_pos.y + 8))
        screen.blit(self.texture, texture_rect)
        # pg.draw.circle(screen, (255, 255, 255), self.pos, self.size, width=2)

    def calc_dist(self, pos):
        d = pos - self.interpolated_pos
        return d, d.length()
