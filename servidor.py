import json
from math import sqrt
from time import sleep
from os import _exit

from server import Server

class Ball:
    def __init__(self):
        self.pos = [500, 500]
        self.vel = [0, 0]
    
    def calc_dist(self, pos):
        d = [pos[0] - self.pos[0], pos[1] - self.pos[1]]
        return d, sqrt(d[0]**2 + d[1]**2)

class Game:
    def __init__(self):
        self.players = []
        self.ball = Ball()
        self.clients = []

    def update(self):
        for player in self.players:
            d, distancia = self.ball.calc_dist(player["pos"])

            if distancia == 0:
                continue

            d[0] = (d[0]) / (distancia * 20)
            d[1] = (d[1]) / (distancia * 20)
            if distancia < 110:
                self.ball.vel[0] -= d[0]
                self.ball.vel[1] -= d[1]

        self.ball.pos[0] += self.ball.vel[0]
        self.ball.pos[1] += self.ball.vel[1]

        self.ball.vel[0] *= 0.98
        self.ball.vel[1] *= 0.98

app = Server()
game = Game()

@app.route("CONNECT")
def connect(data, addr):
    player_id = len(game.players)
    player_data = {"addr": addr, "pos": [0, 0], "id": player_id}
    game.players.append(player_data)
    game.clients.append(addr)

    print(f"Novo jogador conectado: {data}")
    
    return json.dumps({"type": "ID", "data": {"id": player_id}})

@app.route("UPDATE")
def update(data, addr):
    for player in game.players:
        if player["id"] == data["id"]:
            player["pos"] = data["pos"]

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
