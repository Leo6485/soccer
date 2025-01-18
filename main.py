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
        self.screen = pg.display.set_mode((1920, 1080), pg.FULLSCREEN)
        self.app = app
        self.player = Player(-1)
        self.players = {}

        data = {"type": "CONNECT", "data": {}}
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
                game.players[id] = Enemy(player["id"])
                game.players[id].pos = player["pos"]

game.run()
pg.quit()
app.stop()