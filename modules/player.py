import pygame as pg
from time import time
from modules.weapon import Weapon
from modules.entity import CharacterBaseData

pg.init()
d = pg.display.Info()
DW, DH = d.current_w, d.current_h
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
        self.has_jail = 0
        self.put_jail_ts = 0
        self.cursor = Cursor()

        self.name_text = pg.font.Font(None, 25).render(self.name, True, (50, 50, 255))
        self.texture = pg.image.load(f"assets/textures/player/pato{self.team}.png")
        self.texture = pg.transform.scale(self.texture, (192, 128))
        
        self.data = {"pos": [0, 0], "id": id}

    def update(self, pressed, mouse_pressed, ball, players, IDs):
        self.cursor.update()
        
        self.dir = self.cursor.pos.x < 0
        self.run = pressed[pg.K_w] and (time() - self.respawn_ts > 1.5 and time() - self.jail_ts > 1.5)
        if self.run:
            self.pos.y += self.cursor.delta.y * self.vel
            self.pos.x += self.cursor.delta.x * self.vel
        
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
        
        if pressed[pg.K_d]:
            if self.has_jail:
                self.put_jail_ts = time()

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
                        "put_jail_ts": self.put_jail_ts
                     }

    def draw_progress_bar(self, screen, progress):
        bar_width = 50
        bar_height = 5
        x = self.pos.x - bar_width / 2
        y = self.pos.y + self.size + 10

        pg.draw.rect(screen, (0, 100, 0), (x, y, bar_width, bar_height))
        pg.draw.rect(screen, (0, 255, 0), (x, y, bar_width * progress, bar_height))

    def draw(self, screen):
        
        draw_jail = time() - self.jail_ts < 1.5 and self.jail_textures
        if draw_jail:
            screen.blit(self.jail_textures[0], (self.pos.x - 64, self.pos.y - 80))

        self.cursor.draw(screen, self.pos)

        frame_y = 64 if self.cursor.pos.x < 0 else 0
        frame_x = int((time() * 6) % 3) * 64 if self.run else 128

        texture_rect = pg.Rect(frame_x, frame_y, 64, 64)
        screen.blit(self.texture, (self.pos.x-32, self.pos.y-42), texture_rect)

        # pg.draw.circle(screen, (0, 255, 0), (int(self.pos.x), int(self.pos.y)), self.size)
        self.weapon.draw(screen, self.pos, self.id, self.cursor.pos, self.attack_ts)
        # Desenha o nome do player
        text_rect = self.name_text.get_rect(center=(self.pos.x, self.pos.y - self.size - 10))
        screen.blit(self.name_text, text_rect)

        # Desenha a barra de cooldown
        progress = min((time() - self.last_attack)/0.5, 1)
        self.draw_progress_bar(screen, progress)
        
        if draw_jail:
            screen.blit(self.jail_textures[1], (self.pos.x - 64, self.pos.y - 80))

    def reset_name(self, name):
        self.name = name
        self.name_text = pg.font.Font(None, 25).render(self.name, True, (255, 50, 50))