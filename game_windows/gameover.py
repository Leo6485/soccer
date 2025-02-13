import pygame as pg
from time import time

class GameOver:
    def __init__(self, app, game_manager):
        self.manager = game_manager
        self.app = app

        self.font_vitoria = pg.font.SysFont("Arial", 64)
        self.font_derrota = pg.font.SysFont("Arial", 64)
        self.msg_font = pg.font.SysFont("Arial", 48)
        
        self.screen = self.manager.screen
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        
        self.end_time = 0
        self.countdown = 0

        self.player_windows = [pg.Rect(100 + (i % 2) * 910, 100 + (i // 2) * 300, 80, 80) for i in range(4)]
    def update(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.manager.running = False
        
        if (self.end_time - time()) <= -1:
            self.end_time = time() + 5.9

        self.countdown = max(0, int(self.end_time - time()))

        player_data = {"type": "ping", "data": {"id": self.manager.player.id}}
        self.app.send(player_data)

    def draw(self):
        self.screen.fill((80, 80, 80))
        
        self.screen.blit(self.manager.UI_background, (0, 0))

        self.draw_result()
        self.draw_score()
        self.draw_countdown()

        for i, window in enumerate(self.player_windows):
            texture = self.manager.UI_player_textures[i % 2]
            offset_x = 256 * 7 * self.manager.IDs[i]
            scaled_texture = pg.transform.scale(texture.subsurface((offset_x, 0, 256, 256)), (256, 256))
            self.screen.blit(scaled_texture, window.topleft)

        self.manager.flip()

    def draw_result(self):
        result = "Vitória" if self.manager.placar[self.manager.player.team] == max(self.manager.placar) else "Derrota"
        font = self.font_vitoria if result == "Vitória" else self.font_derrota
        result_text = font.render(result, True, (255, 0, 255))
        self.screen.blit(result_text, (self.screen_width / 2 - result_text.get_width() / 2, self.screen_height / 4))

    def draw_score(self):
        score_text = f"{self.manager.placar[0]} - {self.manager.placar[1]}"
        score_surface = self.msg_font.render(score_text, True, (255, 255, 0))
        self.screen.blit(score_surface, (self.screen_width / 2 - score_surface.get_width() / 2, self.screen_height / 2 - 50))

    def draw_countdown(self):
        countdown_text = self.msg_font.render(str(self.countdown), True, (255, 255, 255))
        self.screen.blit(countdown_text, (self.screen_width / 2 - countdown_text.get_width() / 2, self.screen_height / 2 + 50))