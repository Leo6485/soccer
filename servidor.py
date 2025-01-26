import json
from math import sqrt
from time import sleep
from os import _exit
from time import time
import jsonbin
from net import Server
from pygame import Vector2

respawn_points = [Vector2(50, 50), Vector2(1316, 50), Vector2(50, 718), Vector2(1316, 718)]

class Ball:
    def __init__(self):
        self.pos = Vector2(500, 500)
        self.vel = Vector2(0, 0)
        self.size = 85
    
    def update(self, players, display):
        for player in players.values():
            self.update_move(player)
        
        self.update_collision(display)
    
    def update_move(self, player):
        d, distancia = self.calc_dist(player["pos"])
        
        # Evita a divisão por 0
        if distancia == 0:
            return

        d /= distancia * 20

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
        self.players = {}
        self.ball = Ball()
        self.clients = {}
        self.display = Vector2(1366, 768)
        self.placar = [0, 0]
        self.started = False
    
    def restart(self):
        self.__init__(self)
    
    def get_free_id(self):
        for i in range(4):
            if not self.players.get(i):
                return i

    def update(self):
        crr_time = time()
        to_delete = []
        for id, player in self.players.items():
            ############################## Desconecta clientes inativos ##############################
            if crr_time - player.get("last_update") > 1:
                to_delete.append(id)
                continue

            ############################## Ataque ##############################
            att_ts = player.get("attack_ts", 0)
            last_att = player.get("last_attack", 0)
            attack_target = player.get("attack_target", None)

            # Delay aceito e cooldown
            if crr_time - att_ts < 0.5 and att_ts - last_att > 0.5:
                if attack_target is not None:
                    target_player = self.players[attack_target]
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
        
        for id in to_delete:
            del self.clients[id]
            del self.players[id]

        self.ball.update(self.players, self.display)
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

@app.route("CONNECT")
def connect(data, addr):
    crr_time = time()
    player_id = game.get_free_id()
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

@app.route("STARTGAME")
def startgame(data, addr):
    game.started = True

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

print("/033c", end="\r")
app.run(wait=False)

def send_updates():
    for c in game.clients.values():
        app.send({
            "type": "UPDATE",
            "data": {
                "ball": [round(i, 2) for i in game.ball.pos],
                "players": game.players,
                "placar": game.placar
            }
        }, c)

while True:
    try:
        game.update()
        send_updates()
        sleep(1/120)
    except KeyboardInterrupt:
        break

app.stop()
