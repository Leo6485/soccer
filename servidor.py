import json
from math import sqrt
from time import sleep
from os import _exit
from time import time
import jsonbin
from net import Server

class Ball:
    def __init__(self):
        self.pos = [500, 500]
        self.vel = [0, 0]
        self.size = 85
    
    def calc_dist(self, pos):
        d = [pos[0] - self.pos[0], pos[1] - self.pos[1]]
        return d, sqrt(d[0]**2 + d[1]**2)

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Game:
    def __init__(self):
        self.players = {}
        self.ball = Ball()
        self.clients = []
        self.display = Vector2(1200, 720)

    def update(self):
        for id, player in self.players.items():
            d, distancia = self.ball.calc_dist(player["pos"])

            if distancia == 0:
                continue

            d[0] = (d[0]) / (distancia * 20)
            d[1] = (d[1]) / (distancia * 20)
            if distancia < 110:
                self.ball.vel[0] -= d[0]
                self.ball.vel[1] -= d[1]
            
            att_ts = player.get("attack_ts", 0)
            last_att = player.get("last_attack", 0)

            # Delay aceito e cooldown
            if time() - att_ts < 0.5 and att_ts - last_att > 1:
                for target_player in self.players.values():
                    if target_player["id"] == id:
                        continue
                    
                    target = target_player["pos"]
                    cursor = player["cursor_pos"]
                    distancia = sqrt((target[0] - cursor[0])**2 + (target[1] - cursor[1])**2)

                    if distancia < 50:
                        print(f"Player {id} atacou player {target_player['id']}")
                        id = target_player["id"]
                        pos = [50, 360] if id%2 else [1150, 360]
                        self.players[id]["pos"] = pos
                        self.players[id]["force_pos"] = time()

                player["last_attack"] = time()

        if self.ball.pos[0] < self.ball.size:
            self.ball.vel[0] *= -0.5
            self.ball.pos[0] = self.ball.size
        
        if self.ball.pos[1] < self.ball.size:
            self.ball.vel[1] *= -0.5
            self.ball.pos[1] = self.ball.size

        if self.ball.pos[0] > self.display.x - self.ball.size:
            self.ball.vel[0] *= -0.5
            self.ball.pos[0] = self.display.x - self.ball.size

        if self.ball.pos[1] > self.display.y - self.ball.size:
            self.ball.vel[1] *= -0.5
            self.ball.pos[1] = self.display.y - self.ball.size

        self.ball.pos[0] += self.ball.vel[0]
        self.ball.pos[1] += self.ball.vel[1]

        self.ball.vel[0] *= 0.98
        self.ball.vel[1] *= 0.98

app = Server()
jsonbin.set_ip(app.ip)
game = Game()

@app.route("CONNECT")
def connect(data, addr):
    player_id = len(game.players)
    player_data = {"addr": addr, "pos": [0, 0], "name": data["name"], "id": player_id, "attack_ts": 0, "last_attack": 0}
    game.players[player_id] = player_data
    game.clients.append(addr)

    print(f"Novo jogador conectado: {data}")
    print(game.players)
    return json.dumps({"type": "ID", "data": {"id": player_id}})

@app.route("UPDATE")
def update(data, addr):
    id = data["id"]
    player = game.players[id]
    
    if time() - game.players[id].get("force_pos", 0) > 0.5:
        player["pos"] = data["pos"]
        player["attack_ts"] = data["attack_ts"]
        player["cursor_pos"] = data["cursor_pos"]

@app.route("QUIT")
def quit(data, addr):
    global game, app
    for c in game.clients:
        app.send(json.dumps({"type": "QUIT"}), c)

    game = Game()
    app.stop()
    _exit(0)
    
    print("Reiniciando o servidor...")

print("/033c", end="\r")
app.run(wait=False)

def send_updates():
    for c in game.clients:
        app.send(json.dumps({"type": "UPDATE", "data": {"ball": game.ball.pos, "players": game.players}}), c)

while True:
    try:
        game.update()
        send_updates()

        sleep(1 / 120)
    except KeyboardInterrupt:
            break

app.stop()
