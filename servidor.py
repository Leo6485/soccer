from time import sleep, time
from os import _exit
import modules.jsonbin as jsonbin
from modules.net import Server
from pygame import Vector2
from threading import Lock
from modules.entity import CharacterBaseData

class GamePlayer:
    def __init__(self):
        self.timestamps = {}
        self.data = {}
        self.lock = Lock()
    
    def get(self):
        with self.lock:
            data = self.data.copy()
        return data

class Ball:
    def __init__(self):
        self.pos = Vector2(50, 650)
        self.vel = Vector2(0, 0)
        self.size = 85
    
    def update(self, players, display, IDs, delta_time):
        self.update_collision(display)
        for id, player in players.items():
            if IDs[id]:
                self.update_move(player, delta_time)
    
    def update_move(self, player, delta_time):
        d, distancia = self.calc_dist(player.pos)
        if distancia == 0:
            return
        d /= distancia * 1200 * delta_time
        if distancia < 110:
            self.vel -= d
    
    def update_collision(self, display):

        # Colisão com os limites da tela
        if self.pos.x - self.size < 0:
            self.vel.x *= -0.5
            self.pos.x = self.size
        if self.pos.y - self.size < 0:
            self.vel.y *= -0.5
            self.pos.y = self.size
        if self.pos.x + self.size > display.x:
            self.vel.x *= -0.5
            self.pos.x = display.x - self.size
        if self.pos.y + self.size > display.y:
            self.vel.y *= -0.5
            self.pos.y = display.y - self.size

        raio = self.size - 5
        traves = [
            (0, 130, 230, 240),    # Trave esquerda superior
            (0, 130, 500, 510),    # Trave esquerda inferior
            (1236, 1366, 230, 240), # Trave direita superior
            (1236, 1366, 500, 510)  # Trave direita inferior
        ]

        for x_min, x_max, y_min, y_max in traves:
            nearest_x = max(x_min, min(self.pos.x, x_max))
            nearest_y = max(y_min, min(self.pos.y, y_max))
            nearest = Vector2(nearest_x, nearest_y)

            diff = self.pos - nearest
            d = diff.length()

            if d < raio:
                if d == 0:
                    normal = Vector2(1, 0)
                else:
                    normal = diff.normalize()

                penetration = raio - d

                self.pos += normal * penetration * 1.1

                self.vel = self.vel - 2 * self.vel.dot(normal) * normal
                self.vel *= 0.5

    def calc_dist(self, pos):
        d = pos - self.pos
        return d, d.length()

class Game:
    def __init__(self):
        self.crr_screen = "mainmenu"
        self.players = {}
        self.ball = Ball()
        self.clients = {}
        self.IDs = [False] * 4
        self.display = Vector2(1366, 768)
        self.placar = [0, 0]
        self.started = False
        self.game_end_ts = 0
    
    def restart(self):
        print("\033cReiniciando o servidor")
        self.__init__()
    
    def get_free_id(self):
        try:
            id = self.IDs.index(False)
            self.IDs[id] = True
            return id
        except ValueError:
            return None

    def update(self, delta_time):
        crr_time = time()

        for id, player in self.players.items():
            self.check_inactive_player(id, player, crr_time)
            self.handle_attack(id, player, crr_time)

        self.ball.update(self.players, self.display, self.IDs, delta_time)
        self.check_goal(crr_time)
        self.ball.pos += self.ball.vel
        self.ball.vel *= 0.98
        self.update_screens(crr_time)

    def check_inactive_player(self, id, player, crr_time):
        if crr_time - player.last_update > 1:
            self.IDs[id] = False
            if not any(self.IDs):
                self.restart()

    def handle_attack(self, id, player, crr_time):
        att_ts = player.attack_ts
        last_att = player.last_attack
        attack_target = player.attack_target
        if crr_time - att_ts < 0.5 and att_ts - last_att > 0.5:
            if attack_target is not None:
                target_player = self.players.get(attack_target)
                if target_player:
                    target = target_player.pos
                    cursor = player.cursor_pos
                    distancia = (target - cursor).length()
                    if distancia < 50:
                        print(f"Player {id}:{player.id} atacou player {target_player.id}")
                        id = target_player.id
                        pos = respawn_points[id]
                        self.players[id].pos = pos   
                        self.players[id].respawn_ts = crr_time
            player.last_attack = crr_time

    def check_goal(self, crr_time):
        gol = 0
        if self.ball.pos.x < 150 and 250 < self.ball.pos.y < 518:
            self.reset_ball()
            self.placar[1] += 1
            gol = 1
        if self.ball.pos.x > 1216 and 250 < self.ball.pos.y < 518:
            self.reset_ball()
            self.placar[0] += 1
            gol = 1
        if gol:
            for player in self.players.values():
                player.respawn_ts = crr_time
                player.pos = respawn_points[player.id]

    def reset_ball(self):
        self.ball.pos = Vector2(683, 382)
        self.ball.vel = Vector2(0, 0)

    def update_screens(self, crr_time):
        if 1 in self.placar and self.crr_screen == "ingame":
            self.crr_screen = "gameover"
            self.game_end_ts = crr_time
        if self.crr_screen == "gameover" and crr_time - self.game_end_ts > 5:
            self.placar = [0, 0]
            self.crr_screen = "mainmenu"

respawn_points = [Vector2(100, 100), Vector2(1266, 100), Vector2(100, 668), Vector2(1266, 668)]

app = Server()
jsonbin.set_ip(app.ip)
game = Game()

@app.route("SETSCREEN")
def set_screen(data, addr):
    if game.crr_screen != data["crr_screen"]:
        print(f"Alterando tela para {data['crr_screen']}")
    game.crr_screen = data["crr_screen"]

@app.route("CONNECT")
def connect(data, addr):
    crr_time = time()
    player_id = game.get_free_id()
    if player_id is None:
        return {"type": "servermsg", "data": {"text": "O servidor está lotado", "error": 1}}
    if game.crr_screen == "ingame":
        game.IDs[player_id] = False
        return {"type": "servermsg", "data": {"text": "O servidor está em partida", "error": 1}}
    
    player_data = CharacterBaseData(player_id, data["name"])
    player_data.addr = addr
    player_data.pos = respawn_points[player_id]
    player_data.respawn_ts = crr_time
    player_data.last_update = crr_time
    game.players[player_id] = player_data
    game.clients[player_id] = addr
    print(f"Novo jogador conectado: {data}")
    return {"type": "ID", "data": {"id": player_id, "respawn_ts": time()}}

@app.route("UPDATE")
def update(data, addr):
    crr_time = time()
    id = data["id"]
    player = game.players[id]
    player.cursor_pos = Vector2(data["cursor_pos"])
    if crr_time - player.respawn_ts > 1.5:
        player.pos = Vector2(data["pos"])
        player.attack_ts = data["attack_ts"]
        player.attack_target = data["attack_target"]
        player.run = data["run"]
        player.dir = data["dir"]
        player.name = data["name"]
    player.last_update = crr_time

@app.route("QUIT")
def quit(data, addr):
    global game, app
    for c in game.clients.values():
        app.send({"type": "QUIT"}, c)
    game = Game()
    app.stop()
    _exit(0)
    print("Reiniciando o servidor...")

@app.route("PING")
def ping(data, addr):
    game.players[data["id"]].last_update = time()

print("/033c", end="\r")
app.run(wait=False)

def send_updates():
    data = {
        "type": "UPDATE",
        "data": {
            "crr_screen": game.crr_screen,
            "ball": [round(i, 2) for i in game.ball.pos],
            "players": game.players,
            "IDs": game.IDs,
            "placar": game.placar
        }
    }
    for id, c in game.clients.items():
        if game.IDs[id]:
            app.send(data, c)

delta_time = 1/60
while True:
    try:
        start = time()
        game.update(delta_time)
        send_updates()
        sleep(1/120)
        end = time()
        delta_time = end - start
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(e)
        break
app.stop()
