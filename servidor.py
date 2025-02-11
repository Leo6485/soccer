from time import sleep, time
from os import _exit
import modules.jsonbin as jsonbin
from shared.net import Server
from pygame import Vector2
from threading import Lock
from random import randint
from modules.entity import CharacterBaseData
from server_modules.player import Player

class Ball:
    def __init__(self):
        self.pos = Vector2(1366/2, 768/2)
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

class SkillItem:
    def __init__(self):
        self.pos = Vector2(-1000, -1000)
    
    def check(self, player_pos):
        if self.pos.distance_to(player_pos) < 20:
            print(self.pos)
            self.pos = Vector2(-1000, -1000)
            print(f"Habilidade {self.__class__.__name__} coletada")
            return True
        return False
    
    def spawn(self, spawn_pos):
        print(f"Habilidade {self.__class__.__name__} spawnada na posição {spawn_pos}")
        self.pos = spawn_pos
    
class JailItem(SkillItem):
    pass

class InvisibilityItem(SkillItem):
    pass

class Game:
    def __init__(self):
        self.crr_screen = "mainmenu"
        self.started = False
        self.game_end_ts = 0

        self.players = {}
        self.clients = {}
        self.IDs = [False] * 4

        self.ball = Ball()
        self.jail_item = JailItem()
        self.invisibility_item = InvisibilityItem()

        self.display = Vector2(1366, 768)
        self.placar = [0, 0]
        self.respawn_points = [
            Vector2(100, 100), 
            Vector2(1266, 100), 
            Vector2(100, 668), 
            Vector2(1266, 668)
        ]

    def restart_server(self):
        print("\033cReiniciando o servidor")
        self.__init__()

    def restart(self):
        self.placar = [0, 0]
        self.reset_ball()
        self.crr_screen = "mainmenu"
        self.jail_item.pos = Vector2(-1000, -1000)
        for p_id in self.players.keys():
            self.players[p_id].skills["jail"] = [0, 0, 0]
            self.players[p_id].skills["invisibility"] = [0, 0, 0]

    def get_free_id(self):
        try:
            free_id = self.IDs.index(False)
            self.IDs[free_id] = True
            return free_id
        except ValueError:
            return None

    def update(self, delta_time):
        crr_time = time()
        self.update_players(crr_time)
        self.update_ball(delta_time)
        self.check_goal(crr_time)
        self.update_screen(crr_time)

    def update_players(self, crr_time):
        for player in self.players.values():
            player.check_inactive(crr_time, self)
            player.handle_attack(crr_time, self)
            player.handle_skills(crr_time, self)
            player.collect_skills(self)

    def update_ball(self, delta_time):
        self.ball.update(self.players, self.display, self.IDs, delta_time)
        self.ball.pos += self.ball.vel
        self.ball.vel *= 0.98

    def check_goal(self, crr_time):
        gol = False
        
        # Gol
        if self.ball.pos.x < 150 and 250 < self.ball.pos.y < 518:
            self.reset_ball()
            self.placar[1] += 1
            gol = True
        elif self.ball.pos.x > 1216 and 250 < self.ball.pos.y < 518:
            self.reset_ball()
            self.placar[0] += 1
            gol = True

        # Atualiza o respawn em caso de gol
        if gol:
            for player in self.players.values():
                player.respawn_ts = crr_time
                player.pos = self.respawn_points[player.id]

    def reset_ball(self):
        self.ball.pos = Vector2(683, 382)
        self.ball.vel = Vector2(0, 0)

    def update_screen(self, crr_time):
        if 5 in self.placar and self.crr_screen == "ingame":
            self.crr_screen = "gameover"
            self.game_end_ts = crr_time
        if self.crr_screen == "gameover" and crr_time - self.game_end_ts > 5:
            self.restart()

    def kill(self, player_id, crr_time):
        target_player = self.players[player_id]
        
        print(f"Target player pos: {target_player.pos}")
        op = randint(1, 4)
        if op == 2:
            self.jail_item.spawn(target_player.pos)
        elif op == 4:
            self.invisibility_item.spawn(target_player.pos)
        
        target_player.pos = self.respawn_points[player_id]
        target_player.respawn_ts = crr_time

        # Limpa efeitos do player alvo
        target_player.skills["jail"]["effect_ts"] = 0
        target_player.skills["invisibility"]["effect_ts"] = 0

class App:
    def __init__(self):
        self.server = Server()
        jsonbin.set_ip(self.server.ip)
        self.game = Game()
        self.delta_time = 1/60

    def run(self):
        self.server.run(wait=False)
        self.setup_routes()
        try:
            self.update()
        except KeyboardInterrupt:
            self.server.stop()
        except Exception:
            pass
        self.server.stop()
    
    def update(self):
        while True:
            try:
                start = time()

                self.game.update(self.delta_time)
                self.send_updates()
                sleep(1/120)

                end = time()
                self.delta_time = end - start
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(e)

    def send_updates(self):
        data = {
            "type": "UPDATE",
            "data": {
                "crr_screen": self.game.crr_screen,
                "ball": [round(i, 2) for i in self.game.ball.pos],
                "players": {p_id: player.__dict__ for p_id, player in self.game.players.items()},
                "IDs": self.game.IDs,
                "placar": self.game.placar,
                "skills_items": {"jail": self.game.jail_item.pos, "invisibility": self.game.invisibility_item.pos}
            }
        }
        for id, c in self.game.clients.items():
            if self.game.IDs[id]:
                self.server.send(data, c)

    def setup_routes(self):
        @app.server.route("SETSCREEN")
        def set_screen(data, addr):
            if self.game.crr_screen != data["crr_screen"]:
                print(f"Alterando tela para {data['crr_screen']}")
            self.game.crr_screen = data["crr_screen"]

        @app.server.route("CONNECT")
        def connect(data, addr):
            crr_time = time()
            player_id = self.game.get_free_id()
            if player_id is None:
                return {"type": "servermsg", "data": {"text": "O servidor está lotado", "error": 1}}
            if self.game.crr_screen == "ingame":
                self.game.IDs[player_id] = False
                return {"type": "servermsg", "data": {"text": "O servidor está em partida", "error": 1}}

            player_data = Player(
                addr=addr,
                pos=self.game.respawn_points[player_id],
                name=data["name"],
                id=player_id
            )
            self.game.players[player_id] = player_data
            self.game.clients[player_id] = addr
            print(f"Novo jogador conectado: {data}")
            return {"type": "ID", "data": {"id": player_id, "respawn_ts": time()}}

        @app.server.route("UPDATE")
        def update(data, addr):
            crr_time = time()

            # Identificação
            id = data["id"]
            player = self.game.players[id]

            player.cursor_pos = Vector2(data["cursor_pos"])
            player.last_update = crr_time

            # Recusa no respawn
            if not player.in_respawn() and not player.in_jail():
                player.pos = Vector2(data["pos"])
                player.name = data["name"]
                player.run = data["run"]
                player.dir = data["dir"]
                player.attack_ts = data["attack_ts"]
                player.attack_target = data["attack_target"]
                player.skills = data["skills"]

        @app.server.route("QUIT")
        def quit(data, addr):
            for c in self.game.clients.values():
                self.server.send({"type": "QUIT"}, c)
            self.game = self.game()
            app.stop()
            _exit(0)
            print("Reiniciando o servidor...")

        @app.server.route("PING")
        def ping(data, addr):
            self.game.players[data["id"]].last_update = time()

app = App()
app.run()
app.server.stop()