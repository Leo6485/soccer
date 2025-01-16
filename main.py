import pygame as pg
from time import time
from math import sqrt
import json
from server import Client

def draw_grid(surface, color, cell_size):
    width, height = surface.get_size()
    for x in range(0, width, cell_size):
        pg.draw.line(surface, color, (x, 0), (x, height), width=4)
    for y in range(0, height, cell_size):
        pg.draw.line(surface, color, (0, y), (width, y), width=4)

pg.init()
pg.mouse.set_visible(1)
d = pg.display.Info()
DW, DH = d.current_w, d.current_h
del d

GREEN = (0, 255, 0)
GRID_COLOR = (0, 0, 0)
BG_COLOR = (20, 20, 20)
BACKGROUND_COLOR = (0, 0, 0)

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

        self.last_cursor_pos = pg.Vector2(pg.mouse.get_pos())
        print(self.last_cursor_pos.x)
        if not (DW/8 < self.last_cursor_pos.x < DW/8) or not (DH/8 < self.last_cursor_pos.y < DH/8):
            pg.mouse.set_pos(DW / 2, DH / 2)
            self.last_cursor_pos = pg.Vector2(DW / 2, DH / 2)

class Player:
    vel = 0.05

    def __init__(self, id):
        self.pos = pg.Vector2(100, 100)
        self.size = 25
        self.life = 100
        self.attack_ts = 0
        self.cursor = Cursor()
        self.name = "Osvaldo"
        self.name_text = pg.font.Font(None, 25).render(self.name, True, (255, 255, 255))
        self.id = id
        self.team = self.id % 2 + 1
        self.current_frame = 0

    def update(self, pressed, mouse_pressed, ball):
        self.cursor.update()
        run = pressed[pg.K_w]
        coll = ball.calc_dist(self.pos)
        if run:
            self.pos.y += self.cursor.delta.y * self.vel
            self.pos.x += self.cursor.delta.x * self.vel
        
        if coll[1] < 105:
            if coll[1] != 0:
                nx = coll[0][0] / coll[1]
                ny = coll[0][1] / coll[1]
            else:
                nx, ny = 1, 0
            d = 105 - coll[1]

            self.pos.x += nx * d
            self.pos.y += ny * d
        
        if pressed[pg.K_a]:
            self.attack_ts = time()

    def draw(self, screen):
        pg.draw.circle(screen, (0, 255, 0), ((self.pos.x + self.cursor.pos.x), (self.pos.y + self.cursor.pos.y)), 5)
        pg.draw.circle(screen, GREEN, (int(self.pos.x), int(self.pos.y)), self.size)
        text_rect = self.name_text.get_rect(center=(self.pos.x, self.pos.y - self.size - 10))
        screen.blit(self.name_text, text_rect)

class Enemy:
    def __init__(self, id):
        self.id = id
        self.size = 25
        self.pos = pg.Vector2(0, 0)
    
    def draw(self, screen):
        pg.draw.circle(screen, (255, 0, 0), (int(self.pos[0]), int(self.pos[1])), self.size)

class Ball:
    def __init__(self):
        self.size = 80
        self.pos = (DW/2, DH/2)

    def draw(self, screen):        
        pg.draw.circle(screen, (150, 150, 150), self.pos, self.size)

    def calc_dist(self, pos):
        d = [pos[0] - self.pos[0], pos[1] - self.pos[1]]
        return d, sqrt(d[0]**2 + d[1]**2)

class Game:
    def __init__(self, app):
        self.screen = pg.display.set_mode((1920, 1080), pg.FULLSCREEN)
        self.app = app
        self.player = Player(-1)
        self.players = {}

        data = {"type": "CONNECT", "data": {}}
        self.app.send(json.dumps(data), ("172.18.1.92", 5454))

        self.ball = Ball()

        self.scale = min(DW / 1920, DH / 1080)
        self.padding = ((DW - 1920 * self.scale) / 2, (DH - 1080 * self.scale) / 2)
        self.running = True

    def update(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.running = False

        pressed = pg.key.get_pressed()
        mouse_pressed = pg.mouse.get_pressed()

        if pressed[pg.K_q]:
            self.running = False

        self.player.update(pressed, mouse_pressed, self.ball)
        
        player_data = {
                        "type": "update",
                        "data": {
                                    "pos": list(self.player.pos),
                                    "id": self.player.id,
                                    "attack_ts": self.player.attack_ts, 
                                    "cursor_pos": list(self.player.cursor.pos)
                                }
                      }

        self.app.send(json.dumps(player_data), ("172.18.1.92", 5454))

    def draw(self):
        self.screen.fill(BG_COLOR)

        draw_grid(self.screen, GRID_COLOR, 40)

        for id, enemy in self.players.items():
            if id != self.player.id:
                enemy.draw(self.screen)
        self.player.draw(self.screen)

        self.ball.draw(self.screen)

        pg.display.flip()

    def run(self):
        clock = pg.time.Clock()
        while self.running:
            self.update()
            self.draw()
            clock.tick(60)

app = Client()
app.run(wait=False)

@app.route("id")
def id(data, addr):
    game.player.id = data["id"]
    game.players[data["id"]] = game.player

game = Game(app)
@app.route("update")
def update(data, addr):
    game.ball.pos = data["ball"]
    for player in data["players"]:
        id = player["id"]
        if id != game.player.id:
            if id in game.players.keys():
                game.players[id].pos = player["pos"]
            else:
                print("OK", id)
                game.players[id] = Enemy(player["id"])
                game.players[id].pos = player["pos"]

game.run()
pg.quit()
app.stop()