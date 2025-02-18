import pygame as pg

class Button:
    def __init__(self, pos, texture, texture_on_hover, text, font):
        self.rect = texture.get_rect(x=pos.x, y=pos.y)
        self.texture = texture
        self.texture_on_hover = texture_on_hover
        self.text = text
        self.font = font
        self.hovered = False
        self.clicked = False

    def update(self, event_list, scale, padding):
        self.clicked = False
        mouse_pos = pg.mouse.get_pos()
        scaled_mouse_pos = ((mouse_pos[0] - padding.x) / scale, (mouse_pos[1] - padding.y) / scale)

        if self.rect.collidepoint(scaled_mouse_pos):
            self.hovered = True
            for event in event_list:
                if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                    self.clicked = True
        else:
            self.hovered = False

    def draw(self, screen):
        if self.hovered:
            screen.blit(self.texture_on_hover, self.rect.topleft)
        else:
            screen.blit(self.texture, self.rect.topleft)
        
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class Panel:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.title = "Insira seu nome"
        self.title_font = pg.font.SysFont("Arial", 48)
        self.input_font = pg.font.SysFont("Arial", 36)
        self.center_x = 1000
        self.input_texture = manager.UI_text_input_grey

        # Input box
        self.input_box = self.input_texture.get_rect(x=0, y=200)

        # Buttons
        self.button = Button(pg.Vector2(0, 350), manager.UI_btt_green, manager.UI_btt_grey, "Jogar", self.title_font)
        self.settings_button = Button(pg.Vector2(0, 0), manager.UI_btt_green, manager.UI_btt_grey, "Opções", self.title_font)
        self.exit_button = Button(pg.Vector2(0, 400), manager.UI_btt_orange, manager.UI_btt_grey, "Sair", self.title_font)

    def draw(self, name, server_error, server_msg):
        # Input title
        title_text = self.title_font.render(self.title, True, (255, 255, 0))
        title_x = self.center_x - title_text.get_width() // 2
        self.screen.blit(title_text, (title_x, 100))

        # Input
        self.input_box.centerx = self.center_x
        self.screen.blit(self.input_texture, self.input_box.topleft)
        input_text = self.input_font.render(name, True, (255, 255, 255))
        self.screen.blit(input_text, (self.center_x - input_text.get_width() // 2, self.input_box.y + 15))

        # Button
        self.button.rect.centerx = self.center_x
        self.button.draw(self.screen)

        # Settings Button
        self.settings_button.rect.centerx = self.center_x
        self.settings_button.rect.y = self.button.rect.bottom + 20
        self.settings_button.draw(self.screen)

        # Exit Button
        self.exit_button.rect.centerx = self.center_x
        self.exit_button.rect.y = self.settings_button.rect.bottom + 20
        self.exit_button.draw(self.screen)

        # Server msg
        if server_error:
            server_msg_font = pg.font.SysFont("Arial", 20)
            server_msg_text = server_msg_font.render(server_msg + ". Clique para tentar novamente", True, (255, 0, 0))
            self.screen.blit(server_msg_text, (self.center_x - server_msg_text.get_width() // 2, 280))

class PlayerWindow:
    def __init__(self, rect, texture, id):
        self.rect = rect
        self.texture = texture
        self.id = id
        self.frame = 0

    def update(self, active):
        if active:
            self.frame += (self.frame < 7) * 0.5
        else:
            self.frame -= (self.frame >= 0) * 0.5

    def draw(self, screen):
        offset_x = 256 * int(self.frame)
        scaled_texture = pg.transform.scale(self.texture.subsurface((offset_x, 0, 256, 256)), (256, 256))
        screen.blit(scaled_texture, self.rect.topleft)

class Checkbox:
    def __init__(self, pos, size, font, text):
        self.rect = pg.Rect(pos.x, pos.y, size, size)
        self.checked = False
        self.font = font
        self.text = text

    def update(self, event_list, scale, padding):
        for event in event_list:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                scaled_mouse_pos = ((mouse_pos[0] - padding.x) / scale, (mouse_pos[1] - padding.y) / scale)
                if self.rect.collidepoint(scaled_mouse_pos):
                    self.checked = not self.checked

    def draw(self, screen):
        pg.draw.rect(screen, (255, 255, 255), self.rect, 2)
        if self.checked:
            pg.draw.rect(screen, (255, 255, 255), self.rect.inflate(-4, -4))
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surface, (self.rect.right + 10, self.rect.y))

class SettingsWindow:
    def __init__(self, screen, font, button_texture, button_hover_texture):
        self.screen = screen
        self.font = font
        self.rect = pg.Rect(200, 100, 800, 600)
        self.music_checkbox = Checkbox(pg.Vector2(300, 200), 30, self.font, "Silenciar música")
        self.ok_button = Button(pg.Vector2(self.rect.centerx - 128, self.rect.bottom - 120), button_texture, button_hover_texture, "OK", self.font)
        self.open = False

    def update(self, event_list, scale, padding):
        if not self.open: return

        self.music_checkbox.update(event_list, scale, padding)
        if self.music_checkbox.checked:
            pg.mixer.music.set_volume(0)
        else:
            pg.mixer.music.set_volume(1)

        self.ok_button.update(event_list, scale, padding)
        if self.ok_button.clicked:
            self.open = False

    def draw(self):
        if not self.open: return

        pg.draw.rect(self.screen, (50, 50, 50), self.rect)
        settings_text = self.font.render("Configurações", True, (255, 255, 255))
        self.screen.blit(settings_text, (self.rect.centerx - settings_text.get_width() // 2, self.rect.y + 20))
        self.music_checkbox.draw(self.screen)
        self.ok_button.draw(self.screen)

class MainMenu:
    def __init__(self, app, game_manager):
        self.app = app
        self.manager = game_manager
        self.screen = self.manager.screen
        
        self.name = self.manager.player.name
        self.running = True

        # Settings Window
        self.settings_window = SettingsWindow(self.screen, pg.font.SysFont("Arial", 48), self.manager.UI_btt_green, self.manager.UI_btt_grey)
        
        # Panel
        self.panel = Panel(self.screen, self.manager)
        self.player_windows = [PlayerWindow(pg.Rect(100 + (i % 2) * 300, 100 + (i // 2) * 300, 80, 80), self.manager.UI_player_textures[i % 2], i) for i in range(4)]

        self.frame = [0] * 4

    def handle_events(self, event_list):
        for event in event_list:
            if event.type == pg.QUIT:
                self.manager.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE:
                    self.name = self.name[:-1]
                else:
                    self.name += event.unicode
                    self.name = self.name[:12]
        
        if pg.key.get_pressed()[pg.K_ESCAPE]:
            self.manager.running = False

    def update(self):
        event_list = pg.event.get()
        self.handle_events(event_list)

        self.panel.button.update(event_list, self.manager.scale, self.manager.padding)
        self.panel.settings_button.update(event_list, self.manager.scale, self.manager.padding)
        self.panel.exit_button.update(event_list, self.manager.scale, self.manager.padding)

        if self.panel.button.clicked:
            if not self.manager.server_error and any(self.manager.IDs):
                self.app.send({"type": "setscreen", "data": {"crr_screen": "ingame", "name": self.name}})
                self.running = False
            else:
                self.manager.connect(force=True)
                self.running = False

        if self.panel.settings_button.clicked:
            self.settings_window.open = True

        if self.panel.exit_button.clicked:
            self.manager.running = False

        self.settings_window.update(event_list, self.manager.scale, self.manager.padding)

        self.manager.player.reset_name(self.name)

        if self.manager.player.id != -1:
            self.app.send({"type": "ping", "data": {"id": self.manager.player.id}})

        for i, window in enumerate(self.player_windows):
            window.update(self.manager.IDs[i])

    def draw(self):
        self.screen.fill((80, 80, 80))

        self.screen.blit(self.manager.UI_background, (0, 0))

        self.panel.draw(self.name, self.manager.server_error, self.manager.server_msg)

        for window in self.player_windows:
            window.draw(self.screen)

        self.settings_window.draw()

        self.manager.flip()