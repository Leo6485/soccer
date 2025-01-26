import pygame as pg
from time import time
import modules.jsonbin as jsonbin
from modules.net import Client
from modules.entity import Enemy, Ball
from modules.player import Player
import traceback

pg.init()
pg.mouse.set_visible(0)
d = pg.display.Info()
DW, DH = d.current_w, d.current_h
del d

GREEN = (0, 255, 0)
GRID_COLOR = (50, 50, 50)
BG_COLOR = (200, 200, 200)
BACKGROUND_COLOR = (0, 0, 0)

class Game:
    def __init__(self, app, name):
        self.app = app
        
        # Tela
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)

        # Display design (ainda não utilizado)
        self.DD = pg.Vector2(1920, 1080)
        self.scale = min(DW / self.DD.x, DH / self.DD.y)
        self.padding = pg.Vector2((DW - self.DD.x * self.scale) / 2, (DH - self.DD.y * self.scale) / 2)

        # Variáveis do jogo
        self.IDs = [False]*4
        self.placar = [0, 0]
        self.player = Player(-1, name)
        self.players = {}
        self.ball = Ball()
        
        # Primeira conexão
        data = {"type": "CONNECT", "data": {"name": self.player.name}}
        self.app.send(data)

        self.running = True
        
        # Texturas
        self.map_texture = pg.image.load("assets/textures/map/campo.png").convert()
        self.map_texture = pg.transform.scale(self.map_texture, (DW, DH))

        texture_path = "assets/textures/player"
        self.player_textures = [pg.image.load(texture_path + "/pato1.png").convert_alpha(), pg.image.load(texture_path + "/pato2.png").convert_alpha()]
        self.player_textures = [pg.transform.scale(texture, (192, 128)) for texture in self.player_textures]

        # Debug
        self.debug_font = pg.font.Font(None, 15)
        self.last_pkg = 0
        self.pkg_ps = 1
        self.update_time = 1

    def update(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.running = False

        pressed = pg.key.get_pressed()
        mouse_pressed = pg.mouse.get_pressed()

        if pressed[pg.K_q]:
            self.running = False
        
        self.ball.update()
        for id, p in self.players.items():
            if id != self.player.id and self.IDs[id]:
                p.update()

        self.player.update(pressed, mouse_pressed, self.ball, self.players, self.IDs)
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

        self.screen.blit(self.map_texture, (0, 0))

        # draw_grid(self.screen, GRID_COLOR, 40)
        
        # Gols
        pg.draw.rect(self.screen, ((20, 20, 20)), (0, 200, 150, 368), width=10)
        pg.draw.rect(self.screen, (20, 20, 20), (1216, 200, 150, 368), width=10)

        self.ball.draw(self.screen)

        for id, p in self.players.items():
            if id != self.player.id and self.IDs[id]:
                p.draw(self.screen)
        self.player.draw(self.screen)

        # Debug
        self.debug(f"Player: {self.player.pos}", 0)
        self.debug(f"Ball: {self.ball.pos}", 1)
        self.debug(f"Placar: {self.placar}", 2)
        self.debug(f"FPS: {self.clock.get_fps():.2f}", 3)
        self.debug(f"PKG/s: {self.pkg_ps:.4f}", 4)
        self.debug(f"Update PS: {(1/self.update_time):.2f}", 5)
        pg.display.flip()

    def debug(self, text, offset):
        text = self.debug_font.render(text, True, (255, 0, 0))
        text_rect = text.get_rect(topleft=(10, 25*offset))
        self.screen.blit(text, text_rect)

    def run(self):
        self.clock = pg.time.Clock()
        while self.running:
            start_time = time()
            self.update()
            self.draw()
            end_time = time()
            self.update_time = end_time - start_time
            self.clock.tick(60)

server_ip = jsonbin.get_ip()
app = Client(server_ip=server_ip)

name = input("Insira seu nome: ")
game = Game(app, name)

app.run(wait=False)

@app.route("id")
def id(data, addr):
    game.player.id = data["id"]
    game.player.texture = game.player_textures[data["id"]%2]
    game.players[data["id"]] = game.player

@app.route("update")
def update(data, addr):
    crr_time = time()
    game.ball.pos = pg.Vector2(data["ball"])
    game.IDs = data["IDs"]
    for player in data["players"].values():
        id = player["id"]
        
        # Outros players
        if id != game.player.id:
            if id in game.players.keys():
                game.players[id].pos = player["pos"]
                game.players[id].run = player.get("run", 0)
                game.players[id].dir = player.get("dir", False)
                game.players[id].respawn_ts = player.get("respawn_ts", 0)
                game.players[id].last_update = crr_time
            # Caso o inimigo ainda não tenha sido instanciado
            else:
                enemy = Enemy(player["id"], player["name"])
                enemy.pos = player["pos"]
                enemy.texture = game.player_textures[id%2]
                game.players[id] = enemy
                game.players[id].last_update = player.get("last_update", 0)
        
        # Player atual
        else:
            game.player.respawn_ts = player.get("respawn_ts")
            if time() - player.get("respawn_ts", 0) < 0.5:
                game.player.pos = player["pos"]

    game.placar = data["placar"]

    # Debug
    t = time()
    d = (t - game.last_pkg)
    game.pkg_ps = (1/d + game.pkg_ps)/2 if d else 1
    game.last_pkg = t
    game.last_pkg = time()
    ##############################
try:
    game.run()
except Exception:
    traceback.print_exc()
pg.quit()
app.stop()