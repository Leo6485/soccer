from pygame import Vector2
from time import time

class CharacterBaseData:
    def __init__(self, id, name):
        self.size = 25
        self.pos = Vector2(100, 100)
        self.id = id
        self.name = name
        self.team = self.id%2
        
        # Timestamps
        self.respawn_ts = 0
        self.attack_ts = 0
        self.respawn_ts = time()

        # Animações
        self.run = 0
        self.dir = 0

        # Compatibilidade entre player e enemy
        self.cursor_pos = Vector2(0, 0)
        self.attack_target = None
        self.last_attack = 0
        self.last_update = time()
        self.granade_launch_ts = 0
        self.granade_pos = Vector2(0, 0)


        self.skills = {
                       "jail": {"has": 0, "use_ts": 0, "effect_ts": 0},
                       "invisibility": {"has": 0, "use_ts": 0, "effect_ts": 0},
                       "granade": {"has": 2, "use_ts": 0, "effect_ts": 0}
                      }

    def in_respawn(self):
        return time() - self.respawn_ts < 1.5

    def in_jail(self):
        return time() - self.skills["jail"]["effect_ts"] < 1.5