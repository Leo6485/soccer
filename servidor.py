from time import sleep
from os import _exit
from time import time
import modules.jsonbin as jsonbin
from modules.net import Server
from pygame import Vector2
from threading import Lock

class GamePlayer:
    def __init__(self):
        self.timestamps = {}
        self.data = {}
        self.lock = Lock()
    
    def get(self):
        with self.lock:
            data = self.data.copy()
        
        return data

respawn_points = [Vector2(50, 50), Vector2(1316, 50), Vector2(50, 718), Vector2(1316, 718)]

class Ball:
    def __init__(self):
        self.pos = Vector2(500, 500)
        self.vel = Vector2(0, 0)
        self.size = 85
    
    def update(self, players, display, IDs, delta_time):
        for id, player in players.items():
            if IDs[id]:
                self.update_move(player, delta_time)

        self.update_collision(display)
    
    def update_move(self, player, delta_time):
        d, distancia = self.calc_dist(player["pos"])
        
        # Evita a divisão por 0
        if distancia == 0:
            return

        d /= distancia * 1200 * delta_time

        if distancia < 110:
            self.vel -= d
    
    def update_collision(self, display):
        if self.pos.x < self.size:
            self.vel.x *= -0.5
            self.pos.x = self.size

        if self.pos.y < self.size:
            self.vel.y *= -0.5
            self.pos.y = self.size

        if self.pos.x > display.x - self.size:
            self.vel.x *= -0.5
            self.pos.x = display.x - self.size

        if self.pos.y > display.y - self.size:
            self.vel.y *= -0.5
            self.pos.y = display.y - self.size

    def calc_dist(self, pos):
        d = pos - self.pos
        return d, d.length()

class Game:
    def __init__(self):
        self.crr_screen = "mainmenu"
        self.players = {}
        self.ball = Ball()
        self.clients = {}
        self.IDs = [False]*4
        self.display = Vector2(1366, 768)
        self.placar = [0, 0]
        self.started = False
    
    def restart(self):
        print("Reiniciando o servidor")
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
            ############################## Desconecta clientes inativos ##############################
            if crr_time - player.get("last_update") > 0.5:
                self.IDs[id] = False
                
                # Reinicia o servidor caso todos os jogadores tenham saído
                if not any(self.IDs):
                    self.restart()
                    return

            ############################## Ataque ##############################
            att_ts = player.get("attack_ts", 0)
            last_att = player.get("last_attack", 0)
            attack_target = player.get("attack_target", None)

            # Delay aceito e cooldown
            if crr_time - att_ts < 0.5 and att_ts - last_att > 0.5:
                if attack_target is not None:
                    target_player = self.players.get(attack_target)
                    
                    if target_player:
                        target = target_player["pos"]
                        cursor = player["cursor_pos"]
                        distancia = (target - cursor).length()
                        if distancia < 50:
                            print(f"Player {id}:{player['id']} atacou player {target_player['id']}")
                            id = target_player["id"]
                            pos = respawn_points[id]
                            self.players[id]["pos"] = pos   
                            self.players[id]["respawn_ts"] = crr_time

                player["last_attack"] = crr_time

        self.ball.update(self.players, self.display, self.IDs, delta_time)
        ############################## Detecção dos gols ##############################
        gol = 0
        if self.ball.pos.x < 150 and 200 < self.ball.pos.y < 568:
            self.ball.pos = Vector2(683, 382)
            self.ball.vel = Vector2(0, 0)
            self.placar[1] += 1
            gol = 1
        if self.ball.pos.x > 1216 and 200 < self.ball.pos.y < 568:
            self.ball.pos = Vector2(683, 382)
            self.ball.vel = Vector2(0, 0)
            self.placar[0] += 1
            gol = 1

        if gol:
            for player in self.players.values():
                player["respawn_ts"] = crr_time
                player["pos"] = respawn_points[player["id"]]

        self.ball.pos += self.ball.vel
        self.ball.vel *= 0.98

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
    if player_id is None or game.crr_screen == "ingame":
        return {"type": "servermsg", "data": {"text": "O servidor está lotado ou em partida", "error": 1}}

    player_data = {
        "addr": addr,
        "pos": respawn_points[player_id],
        "name": data["name"],
        "id": player_id,
        "attack_ts": 0,
        "last_attack": 0,
        "respawn_ts": crr_time,
        "last_update": crr_time
    }
    game.players[player_id] = player_data
    game.clients[player_id] = addr
    print(game.clients)
    print(f"Novo jogador conectado: {data}")

    return {"type": "ID", "data": {"id": player_id, "respawn_ts": time()}}

@app.route("UPDATE")
def update(data, addr):
    crr_time = time()
    id = data["id"]
    player = game.players[id]
    
    if crr_time - game.players[id].get("respawn_ts", 0) > 1.5:
        player["pos"] = Vector2(data["pos"])
        player["attack_ts"] = data["attack_ts"]
        player["cursor_pos"] = Vector2(data["cursor_pos"])
        player["attack_target"] = data["attack_target"]
        player["run"] = data["run"]
        player["dir"] = data["dir"]
        player["name"] = data["name"]

        # Variáveis setadas pelo servidor
    player["last_update"] = crr_time

@app.route("QUIT")
def quit(data, addr):
    global game, app
    for c in game.clients.values():
        app.send({"type": "QUIT"}, c)

    game = Game()
    app.stop()
    _exit(0)
    
    print("Reiniciando o servidor...")

# Rota para manter a conexão ativa sem definir um update
@app.route("PING")
def ping(data, addr):
    game.players[data["id"]]["last_update"] = time()

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

app.stop()
