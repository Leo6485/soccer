import pygame as pg
from game import Game
from main_menu import MainMenu
from modules.player import Player
from modules.entity import Ball, Enemy

pg.init()
pg.mouse.set_visible(1)
d = pg.display.Info()
DW, DH = d.current_w, d.current_h
del d

class GameManager:
    def __init__(self, app, name):
        self.app = app
        self.crr_screen = "mainmenu"
        self.IDs = [False]*4
        self.placar = [0, 0]
        self.player = Player(-1, name)
        self.players = {}
        self.ball = Ball()
        self.running = True

        self.DD = pg.Vector2(1366, 768)
        self.scale = min(DW / self.DD.x, DH / self.DD.y)
        self.padding = pg.Vector2((DW - self.DD.x * self.scale) / 2, (DH - self.DD.y * self.scale) / 2)

        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.map_texture = self.load_map_texture()
        self.player_textures = self.load_player_textures()
        
        self.server_msg = ""
        self.server_error = 0
        data = {"type": "CONNECT", "data": {"name": self.player.name}}
        self.app.send(data)
        self.game = Game(self.app, self)
        self.main_menu = MainMenu(self.app, self)

    def load_map_texture(self):
        map_texture = pg.image.load("assets/textures/map/campo.png").convert()
        return pg.transform.scale(map_texture, (int(DW * self.scale), int(DH * self.scale)))

    def load_player_textures(self):
        texture_path = "assets/textures/player"
        textures = [pg.image.load(texture_path + "/pato1.png").convert_alpha(), pg.image.load(texture_path + "/pato2.png").convert_alpha()]
        return [pg.transform.scale(texture, (int(192 * self.scale), int(128 * self.scale))) for texture in textures]

    def run(self):
        self.clock = pg.time.Clock()
        while self.running:
            pg.mouse.set_visible(1)
            while self.crr_screen == "mainmenu" and self.running:
                self.main_menu.update()
                self.main_menu.draw()
            pg.mouse.set_visible(0)
            while self.crr_screen == "ingame" and self.running:
                
                self.game.update()
                self.game.draw()

    def update_game_state(self, data, crr_time):
        self.ball.pos = pg.Vector2(data["ball"])
        self.IDs[:] = data["IDs"]
        for player in data["players"].values():
            id = player["id"]
            if id != self.player.id:
                self.update_enemies(player, id, crr_time)
            else:
                self.player.respawn_ts = player.get("respawn_ts")
                if crr_time - player.get("respawn_ts", 0) < 0.5:
                    self.player.pos = player["pos"]
        self.placar = data["placar"]
        self.crr_screen = data["crr_screen"]

    def update_enemies(self, player, id, crr_time):
        if id in self.players:
            enemy = self.players[id]
            enemy.pos = player["pos"]
            enemy.run = player.get("run", 0)
            enemy.dir = player.get("dir", False)
            enemy.respawn_ts = player.get("respawn_ts", 0)
            enemy.last_update = crr_time
            if crr_time - enemy.respawn_ts < 1:
                enemy.reset_name(player["name"])
            if enemy.name != player["name"]:
                enemy.reset_name(player["name"])
        else:
            enemy = Enemy(id, player["name"])
            enemy.pos = player["pos"]
            enemy.texture = self.player_textures[id % len(self.player_textures)]
            enemy.last_update = crr_time
            self.players[id] = enemy