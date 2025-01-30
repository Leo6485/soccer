import pygame as pg

class MainMenu:
    def __init__(self, app, game_manager):
        self.app = app
        self.manager = game_manager
        self.screen = self.manager.screen
        self.font = pg.font.SysFont("Arial", 48)
        self.msg_font = pg.font.SysFont("Arial", 20)
        self.input_font = pg.font.SysFont("Arial", 36)

        self.name = self.manager.player.name
        self.running = True

        self.start_button = pg.Rect(self.screen.get_width() / 2 - 150, self.screen.get_height() / 2, 300, 60)
        self.name_input_box = pg.Rect(self.screen.get_width() / 2 - 150, self.screen.get_height() / 2 - 100, 300, 60)

    def update(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.running = False
            if e.type == pg.MOUSEBUTTONDOWN:
                if self.start_button.collidepoint(e.pos) and not self.manager.server_error:
                    self.app.send({"type": "setscreen", "data": {"crr_screen": "ingame", "name": self.name}})
                    self.running = False

            if e.type == pg.KEYDOWN:
                if e.key == pg.K_BACKSPACE:
                    self.name = self.name[:-1]
                else:
                    self.name += e.unicode
        self.manager.player.reset_name(self.name)
        player_data = {"type": "ping", "data": {"id": self.manager.player.id}}
        if self.manager.player.id != -1:
            self.app.send(player_data)

    def draw(self):
        # Tela de fundo preta
        self.screen.fill((255, 255, 255))
        
        # Título
        title_text = self.font.render("Digite seu nome", True, (0, 0, 255))
        self.screen.blit(title_text, (self.screen.get_width() / 2 - title_text.get_width() / 2, self.screen.get_height() / 4))
        
        if self.manager.server_error:
            server_msg = self.msg_font.render(self.manager.server_msg, True, (255, 0, 0))
            self.screen.blit(server_msg, (self.screen.get_width() / 2 - server_msg.get_width() / 2, self.screen.get_height() / 4 - 100))
        
        # Input para o nome
        pg.draw.rect(self.screen, (10, 10, 10), self.name_input_box, border_radius=10)
        input_text = self.input_font.render(self.name, True, (255, 255, 255))
        self.screen.blit(input_text, (self.name_input_box.x + 10, self.name_input_box.y + 10))

        pg.draw.rect(self.screen, (0, 255, 0), self.start_button, border_radius=10)
        start_button_text = self.font.render("Jogar", True, (255, 255, 255))
        self.screen.blit(start_button_text, (self.screen.get_width() / 2 - start_button_text.get_width() / 2, self.screen.get_height() / 2))

        pg.display.flip()