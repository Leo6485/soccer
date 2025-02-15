import pygame as pg
from time import time

class Weapon:
    def __init__(self):
        self.texture = None
        self.sound = None
        self.sound_running = False
    
    def draw(self, screen, player_pos, cursor_pos, attack_ts):
        if not self.texture: return

        weapon_pos = player_pos + (cursor_pos / 8)
        angle = (cursor_pos + player_pos - weapon_pos).angle_to(pg.Vector2(1, 0))

        elapsed_time = time() - attack_ts
        self.play_sound(elapsed_time)

        frame_x = 0 if elapsed_time < 0.05 else 64 if elapsed_time < 0.1 else 128
        frame_y = 32 * (cursor_pos.x < 0)
        
        weapon_texture = pg.transform.rotate(self.texture.subsurface(pg.Rect(frame_x, frame_y, 64, 32)), angle)
        
        screen.blit(weapon_texture, weapon_texture.get_rect(center=(weapon_pos.x, weapon_pos.y - 2)))

    def play_sound(self, elapsed_time):
        if self.sound is None: return
        
        if elapsed_time < 0.1 and not self.sound_running:
            self.sound.play()
        self.sound_running = elapsed_time < 0.1

class Granade:
    def __init__(self):
        self.texture = None
        self.sound = None
        self.sound_running = False

        self.vel = pg.Vector2(10, 1)
        self.pos = pg.Vector2(0, 0)
        self.launch_pos = pg.Vector2(0, 0)
        self.launch_ts = 0

    def update(self):
        if not self.texture: return

        elapsed_time = time() - self.launch_ts
        
        if elapsed_time < 0.5:
            self.vel.x *= 0.98
            self.vel.y *= 0.98
            
            self.pos += self.vel

    def draw(self, screen):
        if not self.texture: return

        elapsed_time = time() - self.launch_ts
        
        if elapsed_time < 0.5:
            pg.draw.circle(screen, (255, 255, 255), self.pos, 5)
            screen.blit(pg.transform.rotate(self.texture, elapsed_time * 10), (self.pos.x - 32, self.pos.y - 32, 64, 64))
        elif elapsed_time < 0.6:
            pg.draw.circle(screen, (255, 255, 100), self.pos, 100)
        # self.play_sound(elapsed_time)

    def play_sound(self, elapsed_time):
        if self.sound is None: return
        
        if elapsed_time < 0.1 and not self.sound_running:
            self.sound.play()
        self.sound_running = elapsed_time < 0.1