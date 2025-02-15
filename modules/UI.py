import pygame as pg

class UI_textures:
    def __init__(self):
        self.UI_player_textures = self.load_textures_from_path("assets/textures/UI", ["UI_duck_1.png", "UI_duck_2.png"], (2048, 256))
        self.UI_btt_green = self.load_texture("assets/textures/UI/btt_green_round.png", (256, 96))
        self.UI_btt_grey = self.load_texture("assets/textures/UI/btt_round.png", (256, 96))
        self.UI_background = self.load_texture("assets/textures/UI/background.png", (1366, 768))

    def load_texture(self, path, size):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, size)

    def load_textures_from_path(self, base_path, filenames, size):
        textures = [pg.image.load(f"{base_path}/{filename}").convert_alpha() for filename in filenames]
        return [pg.transform.scale(texture, size) for texture in textures]

class textures:
    def __init__(self):
        self.map_texture = self.load_texture("assets/textures/map/campo.png", (6830, 768))
        self.player_textures = self.load_textures_from_path("assets/textures/player/v2", ["duck_1.png", "duck_2.png"], (192, 128))
        self.weapon_textures = self.load_textures_from_path("assets/textures/player/v2", ["shotgun_1.png", "shotgun_2.png"], (192, 64))
        self.jail_textures = self.load_textures_from_path("assets/textures/items", ["jail_back.png", "jail_front.png"], (128, 128))
        self.granade = self.load_texture("assets/textures/player/v2/granade.png", (64, 64))
        self.explosion = self.load_texture("assets/textures/player/v2/explosion.png", (2048, 2048))

    def load_texture(self, path, size):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, size)

    def load_textures_from_path(self, base_path, filenames, size):
        textures = [pg.image.load(f"{base_path}/{filename}").convert_alpha() for filename in filenames]
        return [pg.transform.scale(texture, size) for texture in textures]
