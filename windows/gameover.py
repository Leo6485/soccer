import pygame as pg

class GameOver:
    def __init__(self, app, game_manager):
        self.manager = game_manager
        self.app = app

        self.font_vitoria = pg.font.SysFont("Arial", 64)
        self.font_derrota = pg.font.SysFont("Arial", 64)
        self.msg_font = pg.font.SysFont("Arial", 48)
        self.button_font = pg.font.SysFont("Arial", 36)
        
        self.screen = self.manager.screen
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        self.menu_button = pg.Rect(self.screen_width / 2 - 150, self.screen_height / 2 + 100, 300, 60)

    def update(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.manager.running = False
        
        player_data = {"type": "ping", "data": {"id": self.manager.player.id}}
        self.app.send(player_data)

    def draw(self):
        self.screen.fill((255, 255, 255))

        # Result title
        result = "Vitória" if self.manager.placar[self.manager.player.team] == max(self.manager.placar) else "Derrota"
        font = self.font_vitoria if result == "Vitória" else self.font_derrota
        result_text = font.render(result, True, (0, 100, 0))
        self.screen.blit(result_text, (self.screen_width / 2 - result_text.get_width() / 2, self.screen_height / 4))

        # Score
        score_text = f"{self.manager.placar[0]} - {self.manager.placar[1]}"
        score_surface = self.msg_font.render(score_text, True, (255, 255, 0))
        self.screen.blit(score_surface, (self.screen_width / 2 - score_surface.get_width() / 2, self.screen_height / 2 - 50))

        # Menu button
        pg.draw.rect(self.screen, (0, 100, 0), self.menu_button, border_radius=10)
        menu_button_text = self.button_font.render("Menu Principal", True, (255, 255, 255))
        self.screen.blit(menu_button_text, (self.menu_button.x + self.menu_button.width / 2 - menu_button_text.get_width() / 2, self.menu_button.y + 10))

        self.manager.flip()

    def draw_background(self):
        # Desenha um fundo cyberpunk alinhado com a resolução
        for i in range(0, self.screen_width + 1, self.screen_width // 16):
            pg.draw.line(self.screen, (0, 255, 255), (i, 0), (i, self.screen_height), 1)
        for i in range(0, self.screen_height + 1, self.screen_height // 9):
            pg.draw.line(self.screen, (0, 255, 255), (0, i), (self.screen_width, i), 1)

    def draw_result(self):
        result = "Vitória" if self.manager.placar[self.manager.player.team] == max(self.manager.placar) else "Derrota"
        font = self.font_vitoria if result == "Vitória" else self.font_derrota
        result_text = font.render(result, True, (255, 0, 255))
        self.screen.blit(result_text, (1366 / 2 - result_text.get_width() / 2, 768 / 4))

    def draw_score(self):
        score_text = f"{self.manager.placar[0]} - {self.manager.placar[1]}"
        score_surface = self.msg_font.render(score_text, True, (255, 255, 0))
        self.screen.blit(score_surface, (1366 / 2 - score_surface.get_width() / 2, 768 / 2 - 50))