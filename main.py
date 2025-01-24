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
        pg.draw.line(surface, color, (x, 0), (x, height), width=1)
    for y in range(0, height, cell_size):
        pg.draw.line(surface, color, (0, y), (width, y), width=1)

pg.init()
pg.mouse.set_visible(0)
d = pg.display.Info()
DW, DH = d.current_w, d.current_h
del d

GREEN = (0, 255, 0)
GRID_COLOR = (50, 50, 50)
BG_COLOR = (200, 200, 200)
BACKGROUND_COLOR = (0, 0, 0)

name = input("Insira seu nome: ")

class Game:
    def __init__(self, app, name):
        self.screen = pg.display.set_mode((1920, 1080), pg.FULLSCREEN)
        self.app = app
        self.placar = [0, 0]

        self.player = Player(-1, name)
        self.players = {}

        data = {"type": "CONNECT", "data": {"name": self.player.name}}
        self.app.send(data)

        self.ball = Ball()

        self.scale = min(DW / 1920, DH / 1080)
        self.padding = ((DW - 1920 * self.scale) / 2, (DH - 1080 * self.scale) / 2)
        self.running = True
        
        texture_path = "assets/textures/player"
        self.player_textures = [pg.image.load(texture_path + "/pato1.png"), pg.image.load(texture_path + "/pato2.png")]
        self.player_textures = [pg.transform.scale(texture, (192, 128)) for texture in self.player_textures]
        # Debug
        
        self.debug_font = pg.font.Font(None, 15)
        self.last_pkg = 0
        self.pkgs = 1

    def update(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.running = False

        pressed = pg.key.get_pressed()
        mouse_pressed = pg.mouse.get_pressed()

        if pressed[pg.K_q]:
            self.running = False

        self.player.update(pressed, mouse_pressed, self.ball, self.players)
        self.send_updates()

    def send_updates(self):
        
        player_data = {
                        "type": "update",
                        "data": self.player.data
                      }

        if self.player.id != -1:
            self.app.send(player_data)

    def draw(self):
        self.screen.fill(BG_COLOR)

        draw_grid(self.screen, GRID_COLOR, 40)
        
        pg.draw.rect(self.screen, ((20, 20, 20)), (0, 200, 150, 368), width=10)
        pg.draw.rect(self.screen, (20, 20, 20), (1216, 200, 150, 368), width=10)

        self.ball.draw(self.screen)

        for id, enemy in self.players.items():
            if id != self.player.id:
                enemy.draw(self.screen)
        self.player.draw(self.screen)

        
        # Debug
        self.debug(f"Player: {self.player.pos}", 0)
        self.debug(f"Ball: {self.ball.pos}", 1)
        self.debug(f"Placar: {self.placar}", 2)
        self.debug(f"FPS: {self.clock.get_fps():.2f}", 3)
        self.debug(f"PKG/s: {self.pkgs:.2f}", 4)
        pg.display.flip()

    def debug(self, text, offset):
        text = self.debug_font.render(text, True, (255, 0, 0))
        text_rect = text.get_rect(topleft=(10, 25*offset))
        self.screen.blit(text, text_rect)

    def run(self):
        self.clock = pg.time.Clock()
        while self.running:
            self.update()
            self.draw()
            self.clock.tick(60)

server_ip = jsonbin.get_ip()
app = Client(server_ip=server_ip)
game = Game(app, name)

app.run(wait=False)

@app.route("id")
def id(data, addr):
    game.player.id = data["id"]
    game.player.texture = game.player_textures[data["id"]%2]
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
                enemy = Enemy(player["id"], player["name"])
                enemy.pos = player["pos"]
                enemy.texture = game.player_textures[id%2]
                
                game.players[id] = enemy
        
        else:
            game.player.respawn_ts = player.get("respawn_ts")
            if time() - player.get("respawn_ts", 0) < 0.5:
                game.player.pos = pg.Vector2(player["pos"])
    
    game.placar = data["placar"]

    # Debug
    t = time()
    d = (t - game.last_pkg)
    game.pkgs = 1.0/ d if d else 1
    game.last_pkg = t
    game.last_pkg = time()
    ##############################

game.run()
pg.quit()
app.stop()