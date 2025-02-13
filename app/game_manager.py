import pygame as pg

from game_windows.game import Game
from game_windows.main_menu import MainMenu
from game_windows.gameover import GameOver

from modules.player import Player
from modules.entity import Ball, Enemy

pg.init()
pg.mouse.set_visible(1)
d = pg.display.Info()
DW, DH = min((1366, 768), (d.current_w, d.current_h))
print(DW, DH)
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
        self.skills_items = {"jail": pg.Vector2(-1000, -1000), "invisibility": pg.Vector2(-1000, -1000)}
        self.skulls_points = [[pg.Vector2(-10000, -10000), 0] for i in range(4)]
        self.running = True
        
        # Telas
        
        # Resoluções de (1366, 768) para baixo
        res = min((1366, 768), (DW, DH))
        self.final_screen = pg.display.set_mode(res, pg.SCALED | pg.FULLSCREEN)
        self.screen = pg.Surface((1366, 768)).convert()
        
        self.screen = pg.display.set_mode(res, pg.SCALED | pg.FULLSCREEN)
        
        
        # Display design e escalas
        self.D = pg.Vector2(res)
        self.DD = pg.Vector2(1366, 768)
        self.scale = min(self.D.x / self.DD.x, self.D.y / self.DD.y)
        self.padding = pg.Vector2((self.D.x - self.DD.x * self.scale) / 2, (self.D.y - self.DD.y * self.scale) / 2)
        
        # Se for menor do que 1, preciso desenhar em uma surface para reescalar posteriormente
        if self.scale < 1:
            self.screen = pg.Surface((1366, 768)).convert()

        # Carrega as texturas
        self.load_textures()

        pg.mixer.init()
        self.music = pg.mixer.music.load("assets/sounds/letx27s-get-this-done-154533.mp3")
        pg.mixer.music.play(-1)
        
        self.shotgun_sound = pg.mixer.Sound("assets/sounds/shotgun.mp3")
        print(f"Resolução: {res}")
        print(f"Escala: {self.scale}")

        # Servidor e primeira conexão
        self.server_msg = ""
        self.server_error = 0
        data = {"type": "CONNECT", "data": {"name": self.player.name}}
        self.app.send(data)
        
        # Janelas
        self.game = Game(self.app, self)
        self.main_menu = MainMenu(self.app, self)
        self.gameover = GameOver(self.app, self)

    def flip(self):
        if self.scale < 1:
            frame = pg.transform.scale(self.screen, (self.DD.x*self.scale, self.DD.y*self.scale))
            self.final_screen.blit(frame, self.padding)
        pg.display.flip()

    def load_textures(self):
        # Game
        self.map_texture = self.load_texture("assets/textures/map/campo.png", (6830, 768))
        self.player_textures = self.load_textures_from_path("assets/textures/player/v2", ["duck_1.png", "duck_2.png"], (192, 128))
        self.weapon_textures = self.load_textures_from_path("assets/textures/player/v2", ["shotgun_1.png", "shotgun_2.png"], (192, 64))
        self.jail_textures = self.load_textures_from_path("assets/textures/items", ["jail_back.png", "jail_front.png"], (128, 128))
        self.granade = self.load_texture("assets/textures/player/v2/granade.png", (64, 64))
        
        # UI
        self.UI_player_textures = self.load_textures_from_path("assets/textures/UI", ["UI_duck_1.png", "UI_duck_2.png"], (2048, 256))
        self.UI_start_button_texture = self.load_texture("assets/textures/UI/start_button.png", (768, 128))
        self.UI_background = self.load_texture("assets/textures/UI/background.png", (1366, 768))

    def load_texture(self, path, size):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, size)

    def load_textures_from_path(self, base_path, filenames, size):
        textures = [pg.image.load(f"{base_path}/{filename}").convert_alpha() for filename in filenames]
        return [pg.transform.scale(texture, size) for texture in textures]

    def run(self):
        self.clock = pg.time.Clock()
        while self.running:

            pg.mouse.set_visible(1)
            pg.mixer.music.stop()
            self.music = pg.mixer.music.load("assets/sounds/letx27s-get-this-done-154533.mp3")
            pg.mixer.music.play(-1)
            while self.crr_screen == "mainmenu" and self.running:
                self.main_menu.update()
                self.main_menu.draw()

            pg.mouse.set_visible(0)
            pg.mixer.music.stop()
            pg.mixer.music.load("assets/sounds/brutal.mp3")
            pg.mixer.music.play(-1)
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
        self.skills_items = data["skills_items"]
        self.skulls_points = data["skulls_points"]

        for player in data["players"].values():
            id = player["id"]
            if id != self.player.id:
                self.update_enemies(player, id, crr_time)
            else:
                self.player.respawn_ts = player["respawn_ts"]
                self.player.skills = player["skills"]

                # O Servidor controla a posição nessas situações
                if crr_time - player["respawn_ts"] < 1.5 or crr_time - player["skills"]["jail"]["effect_ts"] < 1.5:
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
            enemy.skills = player["skills"]
            if crr_time - enemy.respawn_ts < 1:
                enemy.reset_name(player["name"])
            if enemy.name != player["name"]:
                enemy.reset_name(player["name"])
        else:
            enemy = Enemy(id, player["name"])
            enemy.pos = player["pos"]
            enemy.texture = self.player_textures[id % 2]
            enemy.weapon.texture = self.weapon_textures[id % 2]
            enemy.weapon.sound = self.shotgun_sound
            enemy.jail_textures = self.jail_textures
            enemy.last_update = crr_time
            self.players[id] = enemy