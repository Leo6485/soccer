from time import time
from modules.entity import CharacterBaseData

class Player(CharacterBaseData):
    def __init__(self, addr, pos, name, id):
        super().__init__(id, name)
        self.pos = pos
        self.addr = addr
        self.skills = {
            "jail": {"has": 0, "use_ts": 0, "effect_ts": 0},
            "invisibility": {"has": 0, "use_ts": 0, "effect_ts": 0}
        }

    def check_inactive(self, crr_time, game):
        if crr_time - self.last_update > 1:
            game.IDs[self.id] = False
            if not any(game.IDs):
                game.restart_server()

    def handle_attack(self, crr_time, game):
        # Ataque
        att_ts = self.attack_ts
        last_att = self.last_attack
        attack_target = self.attack_target
        if crr_time - att_ts < 0.5 and att_ts - last_att > 0.5:
            if attack_target is not None:
                target_player = game.players.get(attack_target)
                if target_player and not target_player.in_respawn():
                    target = target_player.pos
                    cursor = self.cursor_pos
                    distancia = (target - cursor).length()
                    if distancia < 50:
                        game.kill(attack_target, crr_time)
                        print(f"Player {self.id} atacou player {target_player.id}")

            self.last_attack = crr_time

    def handle_skills(self, crr_time, game):
        # Jail
        put_jail_ts = self.skills["jail"]["use_ts"]
        has_jail = self.skills["jail"]["has"]
        if crr_time - put_jail_ts < 0.5 and has_jail:
            print(f"Player {self.id} colocou uma jaula")
            for other_id, other_player in game.players.items():
                if other_id == self.id:
                    continue
                other_player.skills["jail"]["effect_ts"] = crr_time
            self.skills["jail"]["has"] = 0

        # Invisibility
        use_invisibility_ts = self.skills["invisibility"]["use_ts"]
        has_invisibility = self.skills["invisibility"]["has"]
        if crr_time - use_invisibility_ts < 0.5 and has_invisibility:
            self.skills["invisibility"]["effect_ts"] = crr_time
            self.skills["invisibility"]["has"] = 0
    
    def handle_granade(self, crr_time, game):
        launch_ts = self.granade_launch_ts
        if 0.5 < crr_time - launch_ts < 0.6:
            for player in game.players.values():
                if player.id % 2 == self.id % 2 and player.id != self.id:
                    continue

                distance = (player.pos - self.granade_pos).length()
                if distance < 100:
                    game.kill(player.id, crr_time)
                    print(f"Player {self.id} matou player {player.id} com uma granada")

    def collect_skills(self, game):
        if game.jail_item.check(self.pos):
            self.skills["jail"]["has"] = 1
        
        if game.invisibility_item.check(self.pos):
            self.skills["invisibility"]["has"] = 1
    
    def check_pos(self, game, crr_time):
        if (self.pos.x < -200 or self.pos.x > 1566 or 
            self.pos.y < -200 or self.pos.y > 968):
            game.kill(self.id, crr_time)
            print(f"Player {self.id} morreu por sair do mapa")
