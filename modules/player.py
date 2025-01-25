import pygame as pg
from math import sqrt
from time import time

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
        dx = self.pos.x + mouse_pos.x - self.last_cursor_pos.x
        dy = self.pos.y + mouse_pos.y - self.last_cursor_pos.y
        dist = sqrt(dx**2 + dy**2)

        if self.limit < dist < self.limit + max(DW, DH):
            self.pos.x = dx / (dist / 100)
            self.pos.y = dy / (dist / 100)
            self.delta = self.pos.copy()
        elif dist <= self.limit:
            self.pos.x = dx
            self.pos.y = dy
            if dist:
                self.delta.x = dx / (dist / 100)
                self.delta.y = dy / (dist / 100)
            else:
                self.delta.x = 0
                self.delta.y = 0

        cr = 10
        self.last_cursor_pos = pg.Vector2(pg.mouse.get_pos())
        if not (DW/cr < self.last_cursor_pos.x < (cr-1) * DW/cr) or not (DH/cr < self.last_cursor_pos.y < (cr-1) * DH/cr):
            pg.mouse.set_pos(DW / 2, DH / 2)
            self.last_cursor_pos = pg.Vector2(DW / 2, DH / 2)

class Player:
    vel = 0.05

    def __init__(self, id, name):
        self.pos = pg.Vector2(100, 100)
        self.size = 25
        self.life = 100
        self.run = 0
        self.dir = 0
        self.attack_ts = 0
        self.last_attack = 0
        self.attack_target = None
        self.respawn_ts = 0
        self.cursor = Cursor()
        self.name = name
        self.name_text = pg.font.Font(None, 25).render(self.name, True, (255, 255, 255))
        self.id = id
        self.team = self.id % 2 + 1
        self.data = {"pos": [0, 0], "id": id}
        self.texture = pg.image.load(f"assets/textures/player/pato{self.team}.png")
        self.texture = pg.transform.scale(self.texture, (192, 128))

    def update(self, pressed, mouse_pressed, ball, players):
        self.cursor.update()
        
        
        self.dir = self.cursor.pos.x < 0
        self.run = pressed[pg.K_w] and (time() - self.respawn_ts > 1.5)
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
                for player in players.values():
                    if player.id == self.id:
                        continue

                    target = player.pos
                    cursor = pg.Vector2(self.pos.x + self.cursor.pos.x, self.pos.y + self.cursor.pos.y)
                    distance = sqrt((target[0] - cursor.x)**2 + (target[1] - cursor.y)**2)

                    if distance < 100:
                        self.attack_target = player.id

                self.attack_ts = time()
                self.last_attack = time()

        
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
                     }

    def draw(self, screen):
        pg.draw.circle(screen, (0, 255, 0), ((self.pos.x + self.cursor.pos.x), (self.pos.y + self.cursor.pos.y)), 4)
        pg.draw.circle(screen, (0, 255, 0), ((self.pos.x + self.cursor.pos.x), (self.pos.y + self.cursor.pos.y)), 20, width=2)
        # pg.draw.circle(screen, (255, 255, 255), (int(self.pos.x), int(self.pos.y)), self.size+2)
        
        frame_y = 64 if self.cursor.pos.x < 0 else 0
        frame_x = int((time() * 6) % 3) * 64
        
        frame_x = frame_x if self.run else 128

        texture_rect = pg.Rect(frame_x, frame_y, 64, 64)
        screen.blit(self.texture, (self.pos.x-32, self.pos.y-50), texture_rect)

        # pg.draw.circle(screen, (0, 255, 0), (int(self.pos.x), int(self.pos.y)), self.size)
        text_rect = self.name_text.get_rect(center=(self.pos.x, self.pos.y - self.size - 10))
        screen.blit(self.name_text, text_rect)
