import pygame as pg

class Game:
    def __init__(self, app, game_manager):
        self.app = app
        self.manager = game_manager

        self.players = self.manager.players
        self.IDs = self.manager.IDs
        self.player = self.manager.player
        self.ball = self.manager.ball
        self.screen = self.manager.screen

        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont("Arial", 24)
        self.score_font = pg.font.SysFont("Arial", 64)

    def update(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.manager.running = False

        pressed = pg.key.get_pressed()
        mouse_pressed = pg.mouse.get_pressed()

        if pressed[pg.K_q]:
            self.manager.running = False
        
        self.ball.update()
        for id, p in self.players.items():
            if id != self.player.id and self.IDs[id]:
                p.update()

        self.player.update(pressed, mouse_pressed, self.ball, self.players, self.IDs)
        self.send_updates()

    def send_updates(self):
        player_data = {
            "type": "update",
            "data": self.manager.player.data
        }
        if self.player.id != -1:
            self.app.send(player_data)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.manager.map_texture, (0, 0))

        self.ball.draw(self.screen)

        for id, p in self.players.items():
            if id != self.player.id and self.IDs[id]:
                p.draw(self.screen, self.player.pos)

        self.player.draw(self.screen)

        # Draw scoreboard
        self.draw_score()

        # Exibir FPS
        fps_text = self.font.render(f"FPS: {self.clock.get_fps():.1f}", True, (0, 0, 255))
        self.screen.blit(fps_text, (10, 10))

        # Exibir posição do cursor
        # cursor_pos = self.player.pos + self.player.cursor.pos
        # cursor_text = self.font.render(f"Cursor: {cursor_pos}", True, (20, 20, 20))
        # self.screen.blit(cursor_text, (10, 40))
        
        # pg.display.flip()
        self.manager.flip()
        self.clock.tick(200)

    def draw_score(self):
        score_text = f"{self.manager.placar[0]}   {self.manager.placar[1]}"
        score_surface = self.score_font.render(score_text, True, (119, 221, 119))
        score_rect = score_surface.get_rect(center=(self.screen.get_width() // 2, 50))
        self.screen.blit(score_surface, score_rect)
