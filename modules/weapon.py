import pygame as pg
from time import time

class Weapon:
    def __init__(self):
        self.texture = None
    
    def draw(self, screen, player_pos, cursor_pos, attack_ts):
        if not self.texture: return

        weapon_pos = player_pos + (cursor_pos / 8)
        angle = (cursor_pos + player_pos - weapon_pos).angle_to(pg.Vector2(1, 0))
        
        elapsed_time = time() - attack_ts
        frame_x = 0 if elapsed_time < 0.05 else 64 if elapsed_time < 0.1 else 128
        frame_y = 32 * (cursor_pos.x < 0)
        
        weapon_texture = pg.transform.rotate(self.texture.subsurface(pg.Rect(frame_x, frame_y, 64, 32)), angle)
        
        screen.blit(weapon_texture, weapon_texture.get_rect(center=(weapon_pos.x, weapon_pos.y - 2)))
