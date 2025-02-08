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


        self.skills = {
                       "jail": {"has": 0, "use_ts": 0, "effect_ts": 0},
                       "invisibility": {"has": 0, "use_ts": 0, "effect_ts": 0}
                      }
