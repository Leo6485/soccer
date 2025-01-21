import pygame as pg
from time import time
from math import sqrt
import json
import jsonbin
from net import Client
from modules.entity import *
from modules.player import Player

def draw_grid(surface, color, cell_size):
    width, height = surface.get_size()
    for x in range(0, width, cell_size):
        pg.draw.line(surface, color, (x, 0), (x, height), width=4)
    for y in range(0, height, cell_size):
        pg.draw.line(surface, color, (0, y), (width, y), width=4)

pg.init()
pg.mouse.set_visible(0)
d = pg.display.Info()
DW, DH = d.current_w, d.current_h
del d

GREEN = (0, 255, 0)
GRID_COLOR = (0, 0, 0)
BG_COLOR = (20, 20, 20)
BACKGROUND_COLOR = (0, 0, 0)

class Game:
    def __init__(self, app):
        self.screen = pg.display.set_mode((1200, 720))
        self.app = app
        self.player = Player(-1, input("Insira seu nome: "))
        self.players = {}

        data = {"type": "CONNECT", "data": {"name": self.player.name}}
        self.app.send(json.dumps(data))

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
        self.send_updates()

    def send_updates(self):
        
        player_data = {
                        "type": "update",
                        "data": self.player.data
                      }

        if self.player.id != -1:
            self.app.send(json.dumps(player_data))

    def draw(self):
        self.screen.fill(BG_COLOR)

        draw_grid(self.screen, GRID_COLOR, 40)

        for id, enemy in self.players.items():
            if id != self.player.id:
                enemy.draw(self.screen)
        self.player.draw(self.screen)

        self.ball.draw(self.screen)
        
        for player in self.players.values():
            if player.id != self.player.id and self.ball.calc_dist(player.pos)[1] < 110:
                pg.draw.line(self.screen, (0, 255, 255), player.pos, (player.pos[0], self.ball.pos[1]), width=2)
                pg.draw.line(self.screen, (0, 255, 255), (player.pos[0], self.ball.pos[1]), self.ball.pos, width=2)
                pg.draw.line(self.screen, (0, 255, 255), player.pos, self.ball.pos, width=2)

        if self.ball.calc_dist(self.player.pos)[1] < 110:
            pg.draw.line(self.screen, (0, 255, 255), self.player.pos, (self.player.pos.x, self.ball.pos[1]), width=2)
            pg.draw.line(self.screen, (0, 255, 255), (self.player.pos.x, self.ball.pos[1]), self.ball.pos, width=2)
            pg.draw.line(self.screen, (0, 255, 255), self.player.pos, self.ball.pos, width=2)

        pg.display.flip()

    def run(self):
        clock = pg.time.Clock()
        while self.running:
            self.update()
            self.draw()
            clock.tick(60)

server_ip = jsonbin.get_ip()
app = Client(server_ip=server_ip)
app.run(wait=False)
game = Game(app)

@app.route("id")
def id(data, addr):
    game.player.id = data["id"]
    game.players[data["id"]] = game.player

@app.route("update")
def update(data, addr):
    game.ball.pos = data["ball"]
    for player in data["players"].values():
        id = player["id"]
        if id != game.player.id:
            if id in game.players.keys():
                game.players[id].pos = player["pos"]
            else:
                game.players[id] = Enemy(player["id"], player["name"])
                game.players[id].pos = player["pos"]
        
        elif time() - player.get("force_pos", 0) < 0.5:
            game.player.pos = pg.Vector2(player["pos"])

game.run()
pg.quit()
app.stop()