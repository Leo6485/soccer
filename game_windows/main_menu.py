import pygame as pg

class Button:
    def __init__(self, rect, texture, frames=3):
        self.rect = rect
        self.texture = texture
        self.frames = frames
        self.current_frame = 0
        self.clicked = False

    def update(self, event_list, scale, padding):
        mouse_pos = pg.mouse.get_pos()
        adjusted_mouse_pos = ((mouse_pos[0] - padding.x) / scale, (mouse_pos[1] - padding.y) / scale)
        mouse_pressed = pg.mouse.get_pressed()
        if self.rect.collidepoint(adjusted_mouse_pos):
            self.current_frame = 1
            if mouse_pressed[0]:
                self.clicked = True
                self.current_frame = 2
            for event in event_list:
                if event.type == pg.MOUSEBUTTONUP and event.button == 1 and self.clicked:
                    if self.rect.collidepoint(adjusted_mouse_pos):
                        self.clicked = False
                        self.current_frame = 1
                        return True
                    else:
                        self.clicked = False
                        self.current_frame = 0
        else:
            self.current_frame = 0
            self.clicked = False
        return False

    def draw(self, screen):
        frame_rect = pg.Rect(self.current_frame * 256, 0, 256, 128)
        screen.blit(self.texture, self.rect.topleft, frame_rect)

class Panel:
    def __init__(self, screen, title, title_font, input_box, input_font, button, center_x):
        self.screen = screen
        self.title = title
        self.title_font = title_font
        self.input_box = input_box
        self.input_font = input_font
        self.button = button
        self.center_x = center_x

    def draw(self, name, server_error, server_msg):
        # Input title
        title_text = self.title_font.render(self.title, True, (255, 255, 0))
        title_x = self.center_x - title_text.get_width() // 2
        self.screen.blit(title_text, (title_x, 250))

        # Input
        self.input_box.centerx = self.center_x
        pg.draw.rect(self.screen, (50, 50, 80), self.input_box, border_radius=0)
        input_text = self.input_font.render(name, True, (255, 255, 255))
        input_x = self.input_box.x + 10
        self.screen.blit(input_text, (input_x, self.input_box.y + 10))

        # Button
        self.button.rect.centerx = self.center_x
        self.button.draw(self.screen)
        
        # Server msg
        if server_error:
            server_msg_font = pg.font.SysFont("Arial", 20)
            server_msg_text = server_msg_font.render(server_msg, True, (255, 0, 0))
            self.screen.blit(server_msg_text, (self.center_x - server_msg_text.get_width() // 2, 500))

class MainMenu:
    def __init__(self, app, game_manager):
        self.app = app
        self.manager = game_manager
        self.screen = self.manager.screen
        
        self.font = pg.font.SysFont("Arial", 48)
        self.input_font = pg.font.SysFont("Arial", 36)

        self.name = self.manager.player.name
        self.running = True

        self.start_button = Button(pg.Rect(850, 500, 256, 128), self.manager.UI_start_button_texture)
        self.name_input_box = pg.Rect(850, 350, 350, 60)
        self.panel = Panel(self.screen, "Digite seu nome", self.font, self.name_input_box, self.input_font, self.start_button, center_x=1000)
        self.player_windows = [pg.Rect(100 + (i % 2) * 300, 100 + (i // 2) * 300, 80, 80) for i in range(4)]

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
        
        if pg.key.get_pressed()[pg.K_ESCAPE]:
            self.manager.running = False

    def update(self):
        event_list = pg.event.get()
        self.handle_events(event_list)

        if self.start_button.update(event_list, self.manager.scale, self.manager.padding) and not self.manager.server_error:
            self.app.send({"type": "setscreen", "data": {"crr_screen": "ingame", "name": self.name}})
            self.running = False

        self.manager.player.reset_name(self.name)
        if self.manager.player.id != -1:
            self.app.send({"type": "ping", "data": {"id": self.manager.player.id}})

    def draw(self):
        self.screen.fill((80, 80, 80))

        self.screen.blit(self.manager.UI_background, (0, 0))

        self.panel.draw(self.name, self.manager.server_error, self.manager.server_msg)

        for i, window in enumerate(self.player_windows):
            if self.manager.IDs[i]:
                self.frame[i] += (self.frame[i] < 7) * 0.5
            else:
                self.frame[i] -= (self.frame[i] >= 0) * 0.5

            texture = self.manager.UI_player_textures[i % 2]
            offset_x = 256 * int(self.frame[i])
            scaled_texture = pg.transform.scale(texture.subsurface((offset_x, 0, 256, 256)), (256, 256))
            self.screen.blit(scaled_texture, window.topleft)
        
        self.manager.flip()