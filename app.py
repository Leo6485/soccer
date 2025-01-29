import traceback
from os import _exit
from modules.jsonbin import get_ip
from modules.net import Client
from game_manager import GameManager
import pygame as pg
from time import time

# Inicia as rotas do cliente
class App:
    def __init__(self):
        self.server_ip = get_ip()
        self.client = Client(server_ip=self.server_ip)
        self.game_manager = None

    def run(self):
        name = ""
        self.game_manager = GameManager(self.client, name)
        self.client.run(wait=False)
        self.setup_routes()
        try:
            self.game_manager.run()
        except KeyboardInterrupt:
            self.client.stop()
            _exit(0)
        except Exception:
            traceback.print_exc()
        pg.quit()
        self.client.stop()

    def setup_routes(self):
        @self.client.route("id")
        def id(data, addr):
            self.game_manager.player.id = data["id"]
            self.game_manager.player.texture = self.game_manager.player_textures[data["id"] % 2]
            self.game_manager.players[data["id"]] = self.game_manager.player
            self.game_manager.player.team = self.game_manager.player.id % 2 + 1

        @self.client.route("update")
        def update(data, addr):
            crr_time = time()
            self.game_manager.update_game_state(data, crr_time)
        
        @self.client.route("servermsg")
        def server_msg(data, addr):
            self.game_manager.server_msg = data.get("text", "")
            self.game_manager.server_error = data.get("error", 0)