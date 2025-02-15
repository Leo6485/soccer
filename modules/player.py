import pygame as pg
from time import time
from modules.weapon import Weapon
from modules.weapon import Granade
from shared.character import CharacterBaseData

pg.init()
d = pg.display.Info()
DW, DH = min((1366, 768), (d.current_w, d.current_h))

del d

class Cursor:
    def __init__(self):
        self.pos = pg.Vector2(0, 0)
        self.delta = pg.Vector2(0, 0)
        self.last_cursor_pos = pg.Vector2(pg.mouse.get_pos())
        self.limit = 100

    def update(self):
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        d = self.pos + mouse_pos - self.last_cursor_pos
        dist = d.length()

        if self.limit < dist < self.limit + max(DW, DH):
            self.pos = d / (dist / 100)
            self.delta = self.pos.copy()
        elif dist <= self.limit:
            self.pos = d
            self.delta = d / (dist / 100) if dist else pg.Vector2(0, 0)

        cr = 10
        self.last_cursor_pos = pg.Vector2(pg.mouse.get_pos())
        if not (DW/cr < self.last_cursor_pos.x < (cr-1) * DW/cr) or not (DH/cr < self.last_cursor_pos.y < (cr-1) * DH/cr):
            pg.mouse.set_pos(DW / 2, DH / 2)
            self.last_cursor_pos = pg.Vector2(DW / 2, DH / 2)
    
    def draw(self, screen, player_pos):
        pg.draw.circle(screen, (0, 255, 0), (player_pos + self.pos), 4)
        pg.draw.circle(screen, (0, 255, 0), (player_pos + self.pos), 20, width=2)

class Player(CharacterBaseData):
    vel = 0.05

    def __init__(self, id, name):
        super().__init__(id, name)

        self.last_attack = 0
        self.attack_target = None
        self.cursor = Cursor()

        self.name_text = pg.font.Font(None, 25).render(self.name, True, (50, 50, 255))
        self.texture = pg.image.load(f"assets/textures/player/v2/duck_{self.team}.png")
        self.texture = pg.transform.scale(self.texture, (192, 128))
        
        self.data = {"pos": [0, 0], "id": id}
        
        self.weapon = Weapon()
        self.granade = Granade()
        self.jail_textures = None

    def update(self, pressed, mouse_pressed, ball, players, IDs):
        self.cursor.update()

        self.dir = self.cursor.pos.x < 0
        self.run = pressed[pg.K_w] and (time() - self.respawn_ts > 1.5 and time() - self.skills["jail"]["effect_ts"] > 1.5)
        if self.run:
            self.pos.y += self.cursor.delta.y * self.vel
            self.pos.x += self.cursor.delta.x * self.vel
        
        if time() - self.attack_ts  < 0.1 and not self.run and not self.in_jail() and not self.in_respawn():
            self.pos -= self.cursor.delta * 0.02
        ########## Reage com a bola ##########
        coll = ball.calc_dist(self.pos)

        if coll[1] < 105:
            if coll[1] != 0:
                normal_x = coll[0][0] / coll[1]
                normal_y = coll[0][1] / coll[1]
            else:
                normal_x, normal_y = 1, 0
            overlap = 105 - coll[1]

            self.pos.x += normal_x * overlap
            self.pos.y += normal_y * overlap
        
        ########## Ataca ##########
        if pressed[pg.K_a]:
            if time() - self.last_attack > 0.5:
                self.attack_target = None
                
                ########## Verifica se o cursor está em cima de um player ##########
                for id, player in players.items():
                    if player.team == self.team and IDs[id]:
                        continue

                    target = player.interpolated_pos
                    cursor = pg.Vector2(self.pos.x + self.cursor.pos.x, self.pos.y + self.cursor.pos.y)
                    distance = cursor.distance_to(target)
                    if distance < 100:
                        self.attack_target = player.id

                self.attack_ts = time()
                self.last_attack = self.attack_ts
        
        # Habilidades
        if pressed[pg.K_d]:
            if self.skills["jail"]["has"]:
                self.skills["jail"]["use_ts"] = time()
        if pressed[pg.K_s]:
            if self.skills["invisibility"]["has"]:
                self.skills["invisibility"]["use_ts"] = time()
        
        # Granada
        if pressed[pg.K_e] and time() - self.granade.launch_ts > 5 and not self.in_jail() and not self.in_respawn():
            self.granade.launch_ts = time()
            self.granade.pos = self.pos + (1, 1)
            self.granade.launch_pos = self.pos + (2, 2)
            self.granade.vel = pg.Vector2(self.cursor.pos.x / 4, self.cursor.pos.y / 4)
        
        if pressed[pg.K_r] and time() - self.granade.launch_ts > 5 and not self.in_jail() and not self.in_respawn():
            self.granade.launch_ts = time()
            self.granade.pos = self.pos + (1, 1)
            self.granade.launch_pos = self.pos + (2, 2)
            self.granade.vel = pg.Vector2(0, 0)

        self.granade.update()

        self.update_data()

    def update_data(self):
        self.data =  {
                        "pos": list(self.pos),
                        "id": self.id,
                        "attack_ts": self.attack_ts,
                        "cursor_pos": [self.cursor.pos.x + self.pos.x, self.cursor.pos.y + self.pos.y],
                        "attack_target": self.attack_target,
                        "run": self.run,
                        "dir": self.dir,
                        "name": self.name,
                        "skills": self.skills,
                        "granade_ts": self.granade.launch_ts,
                        "granade_pos": self.granade.pos
                     }

    def draw_progress_bar(self, screen, progress, color=(0, 255, 0), bg_color=(0, 100, 0), y_offset=10):
        bar_width = 50
        bar_height = 5
        x = self.pos.x - bar_width / 2
        y = self.pos.y + self.size + y_offset

        pg.draw.rect(screen, bg_color, (x, y, bar_width, bar_height))
        pg.draw.rect(screen, color, (x, y, bar_width * progress, bar_height))
    def draw(self, screen):
        crr_time = time()
        pos_jail = (self.pos.x - 64, self.pos.y - 80)
        draw_jail = (crr_time - self.skills["jail"]["effect_ts"] < 1.5) and self.jail_textures

        if draw_jail:
            screen.blit(self.jail_textures[0], pos_jail)
        
        # Cursor
        self.cursor.draw(screen, self.pos)
        
        # Frame do player
        frame_y = 64 if self.cursor.pos.x < 0 else 0
        frame_x = int((crr_time * 6) % 3) * 64 if self.run else 128
        texture_rect = pg.Rect(frame_x, frame_y, 64, 64)
        
        if not (crr_time - self.skills["invisibility"]["effect_ts"] < 4):
            screen.blit(self.texture, (self.pos.x - 32, self.pos.y - 42), texture_rect)
        
        # Arma
        self.weapon.draw(screen, self.pos, self.cursor.pos, self.attack_ts)
        
        # Granada
        self.granade.draw(screen)

        # Nome
        text_rect = self.name_text.get_rect(center=(self.pos.x, self.pos.y - self.size - 15))
        screen.blit(self.name_text, text_rect)

        # Barra de cooldown da arma
        progress = min((crr_time - self.last_attack) / 0.5, 1)
        self.draw_progress_bar(screen, progress)
        
        # Barra de cooldown da granada
        progress = min((crr_time - self.granade.launch_ts) / 5, 1)
        self.draw_progress_bar(screen, progress, (255, 255, 0), (100, 100, 0), 20)

        if draw_jail:
            screen.blit(self.jail_textures[1], pos_jail)
    
    def reset_name(self, name):
        self.name = name
        self.name_text = pg.font.Font(None, 25).render(self.name, True, (50, 50, 255))