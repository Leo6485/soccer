import pygame as pg

from game_windows.game import Game
from game_windows.main_menu import MainMenu
from game_windows.gameover import GameOver

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
        self.jail_item = pg.Vector2(-1000, -1000)
        self.running = True

        self.final_screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.screen = pg.Surface((1366, 768))
        self.map_texture = self.load_map_texture()
        self.player_textures = self.load_player_textures()
        self.weapon_textures = self.load_weapon_textures()
        self.jail_textures = self.load_jail_textures()

        self.DD = pg.Vector2(1366, 768)
        self.scale = min(DW / self.DD.x, DH / self.DD.y)
        self.padding = pg.Vector2((DW - self.DD.x * self.scale) / 2, (DH - self.DD.y * self.scale) / 2)
        
        self.server_msg = ""
        self.server_error = 0
        data = {"type": "CONNECT", "data": {"name": self.player.name}}
        self.app.send(data)
        self.game = Game(self.app, self)
        self.main_menu = MainMenu(self.app, self)
        self.gameover = GameOver(self.app, self)
    
    def flip(self):
        frame = pg.transform.scale(self.screen, (DW, DH))
        self.final_screen.blit(frame, self.padding)
        pg.display.flip()

    def load_map_texture(self):
        map_texture = pg.image.load("assets/textures/map/campo.png").convert()
        return pg.transform.scale(map_texture, (1366, 768))

    def load_player_textures(self):
        texture_path = "assets/textures/player"
        textures = [pg.image.load(texture_path + "/duck_1.png").convert_alpha(), pg.image.load(texture_path + "/duck_2.png").convert_alpha()]
        return [pg.transform.scale(texture, (192, 128)) for texture in textures]

    def load_jail_textures(self):
        texture_path = "assets/textures/items"
        textures = [pg.image.load(texture_path + "/jail_back.png").convert_alpha(), pg.image.load(texture_path + "/jail_front.png").convert_alpha()]
        return [pg.transform.scale(texture, (128, 128)) for texture in textures]

    def load_weapon_textures(self):
        path = "assets/textures/player"
        textures = [pg.image.load(path + "/shotgun_1.png").convert_alpha(), pg.image.load(path + "/shotgun_2.png").convert_alpha()]
        return [pg.transform.scale(texture, (192, 64)) for texture in textures]

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
            
            pg.mouse.set_visible(1)
            while self.crr_screen == "gameover" and self.running:
                self.gameover.update()
                self.gameover.draw()

    def update_game_state(self, data, crr_time):
        self.ball.pos = pg.Vector2(data["ball"])
        self.IDs[:] = data["IDs"]
        self.jail_item = data["jail_item"]

        for player in data["players"].values():
            id = player["id"]
            if id != self.player.id:
                self.update_enemies(player, id, crr_time)
            else:
                self.player.respawn_ts = player["respawn_ts"]
                self.player.jail_ts = player["jail_ts"]
                self.player.has_jail = player["has_jail"]
                
                # O Servidor controla a posição nessas situações
                if crr_time - player["respawn_ts"] < 1.5 or crr_time - player["jail_ts"] < 1.5:
                    self.player.pos = player["pos"]

        self.placar[:] = data["placar"]
        self.crr_screen = data["crr_screen"]

    def update_enemies(self, player, id, crr_time):
        if id in self.players:
            enemy = self.players[id]
            enemy.pos = player["pos"]
            enemy.cursor_pos = player["cursor_pos"]
            enemy.run = player["run"]
            enemy.dir = player["dir"]
            enemy.respawn_ts = player["respawn_ts"]
            enemy.last_update = crr_time
            enemy.attack_ts = player["attack_ts"]
            enemy.jail_ts = player["jail_ts"]
            if crr_time - enemy.respawn_ts < 1:
                enemy.reset_name(player["name"])
            if enemy.name != player["name"]:
                enemy.reset_name(player["name"])
        else:
            enemy = Enemy(id, player["name"])
            enemy.pos = player["pos"]
            enemy.texture = self.player_textures[id % 2]
            enemy.weapon.texture = self.weapon_textures[id % 2]
            enemy.jail_textures = self.jail_textures
            enemy.last_update = crr_time
            self.players[id] = enemy