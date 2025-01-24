import json
from math import sqrt
from time import sleep
from os import _exit
from time import time
import jsonbin
from net import Server

respawn_points = [[50, 50], [1316, 50], [50, 718], [1316, 718]]
class Ball:
    def __init__(self):
        self.pos = [500, 500]
        self.vel = [0, 0]
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

        d[0] = (d[0]) / (distancia * 20)
        d[1] = (d[1]) / (distancia * 20)

        if distancia < 110:
            self.vel[0] -= d[0]
            self.vel[1] -= d[1]
    
    def update_collision(self, display):
        if self.pos[0] < self.size:
            self.vel[0] *= -0.5
            self.pos[0] = self.size

        if self.pos[1] < self.size:
            self.vel[1] *= -0.5
            self.pos[1] = self.size

        if self.pos[0] > display.x - self.size:
            self.vel[0] *= -0.5
            self.pos[0] = display.x - self.size

        if self.pos[1] > display.y - self.size:
            self.vel[1] *= -0.5
            self.pos[1] = display.y - self.size

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
        self.display = Vector2(1366, 768)
        self.placar = [0, 0]

    def update(self):
        for id, player in self.players.items():
            ############################## Ataque ##############################
            att_ts = player.get("attack_ts", 0)
            last_att = player.get("last_attack", 0)
            attack_target = player.get("attack_target", None)

            # Delay aceito e cooldown
            if time() - att_ts < 0.5 and att_ts - last_att > 0.5:
                if attack_target is not None:
                    target_player = self.players[attack_target]
                    target = target_player["pos"]
                    cursor = player["cursor_pos"]
                    distancia = sqrt((target[0] - cursor[0])**2 + (target[1] - cursor[1])**2)
                    if distancia < 50:
                        print(f"Player {id}:{player['id']} atacou player {target_player['id']}")
                        id = target_player["id"]
                        pos = respawn_points[id]
                        self.players[id]["pos"] = pos   
                        self.players[id]["respawn_ts"] = time()

                player["last_attack"] = time()
        
        self.ball.update(self.players, self.display)
        ############################## Detecção dos gols ##############################
        gol = 0
        if self.ball.pos[0] < 150 and self.ball.pos[1] > 200 and self.ball.pos[1] < 568:
            self.ball.pos = [683, 382]
            self.ball.vel = [0, 0]
            self.placar[1] += 1
            gol = 1
        if self.ball.pos[0] > 1216 and self.ball.pos[1] > 200 and self.ball.pos[1] < 568:
            self.ball.pos = [683, 382]
            self.ball.vel = [0, 0]
            self.placar[0] += 1
            gol = 1
        
        ts = time()
        # print(self.players)
        if gol:
            for player in self.players.values():
                player["respawn_ts"] = ts
                player["pos"] = respawn_points[player["id"]]

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
    player_data = {"addr": addr, "pos": respawn_points[player_id], "name": data["name"], "id": player_id, "attack_ts": 0, "last_attack": 0, "respawn_ts": time()}
    game.players[player_id] = player_data
    game.clients.append(addr)

    print(f"Novo jogador conectado: {data}")

    return {"type": "ID", "data": {"id": player_id, "respawn_ts": time()}}

@app.route("UPDATE")
def update(data, addr):
    id = data["id"]
    player = game.players[id]
    
    if time() - game.players[id].get("respawn_ts", 0) > 1.5:
        player["pos"] = data["pos"]
        player["attack_ts"] = data["attack_ts"]
        player["cursor_pos"] = data["cursor_pos"]
        player["attack_target"] = data["attack_target"]

@app.route("QUIT")
def quit(data, addr):
    global game, app
    for c in game.clients:
        app.send({"type": "QUIT"}, c)

    game = Game()
    app.stop()
    _exit(0)
    
    print("Reiniciando o servidor...")

print("/033c", end="\r")
app.run(wait=False)

def send_updates():
    for c in game.clients:
        print(c)
        app.send({"type": "UPDATE", "data": {"ball": [round(i, 2) for i in game.ball.pos], "players": game.players, "placar": game.placar}}, c)

while True:
    try:
        game.update()
        send_updates()

        sleep(1 / 120)
    except KeyboardInterrupt:
            break

app.stop()
