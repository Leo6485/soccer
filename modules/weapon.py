import pygame as pg
from time import time

class Weapon:
    def __init__(self):
        self.texture = None
    
    def draw(self, screen, player_pos, p_id, cursor_pos, attack_ts, opacity=255):
        if self.texture is None: return
        
        # Set alpha for texture if opacity is different from 255
        weapon_texture = self.texture.copy()
        if opacity != 255:
            weapon_texture.set_alpha(opacity)
        
        r_cursor_pos = cursor_pos + player_pos
        weapon_pos = player_pos + cursor_pos / 8
        angle = (r_cursor_pos - weapon_pos).angle_to(pg.Vector2(1, 0))
        
        elapsed_time = time() - attack_ts
        if elapsed_time < 0.1:
            frame_x = 0
        elif elapsed_time < 0.2:
            frame_x = 64
        else:
            frame_x = 128
        
        frame_y = 32 if cursor_pos.x < 0 else 0
        
        texture_rect = pg.Rect(frame_x, frame_y, 64, 32)
        weapon_texture = weapon_texture.subsurface(texture_rect)
        
        weapon_texture = pg.transform.rotate(weapon_texture, angle)
        texture_rect = weapon_texture.get_rect(center=weapon_pos)
        screen.blit(weapon_texture, texture_rect)