import pygame


class Menu:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.LIGHT_BROWN = (255, 228, 200)
        self.DARK_BROWN = (193, 120, 50)
        self.YELLOW = (255, 245, 95)

        self.main_font = pygame.font.Font('util/Roboto-Bold.ttf', 55)
        self.font = pygame.font.Font('util/Roboto-Regular.ttf', 36)
        self.font_bold = pygame.font.Font('util/Roboto-Bold.ttf', 36)
        self.button_width = screen_width // 3
        self.button_height = 60

    def draw_main_text(self, text, color, x, y):
        text_surface = self.main_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_text(self, text, color, x, y):
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_button(self, text, x, y, width, height):
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, self.YELLOW, button_rect)
        pygame.draw.rect(self.screen, self.LIGHT_BROWN, button_rect, 2)

        text_surface = self.font.render(text, True, self.DARK_BROWN)
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)

        return button_rect

    def main_menu(self):
        self.screen.fill(self.DARK_BROWN)
        self.draw_main_text('Zombie Chess Game', self.LIGHT_BROWN, self.screen_width // 2, 100)

        play_btn = self.draw_button('Play',
                                    self.screen_width // 2 - self.button_width // 2,
                                    250,
                                    self.button_width,
                                    self.button_height)

        quit_btn = self.draw_button('Quit',
                                    self.screen_width // 2 - self.button_width // 2,
                                    350,
                                    self.button_width,
                                    self.button_height)

        return play_btn, quit_btn

    def game_over_menu(self, endgame_info):
        self.screen.fill(self.DARK_BROWN)
        self.draw_main_text('Game Over!', self.LIGHT_BROWN, self.screen_width // 2, 100)
        self.draw_text(endgame_info, self.LIGHT_BROWN, self.screen_width // 2, 200)

        restart_btn = self.draw_button('Play Again',
                                       self.screen_width // 2 - self.button_width // 2,
                                       300,
                                       self.button_width,
                                       self.button_height)

        menu_btn = self.draw_button('Main Menu',
                                    self.screen_width // 2 - self.button_width // 2,
                                    400,
                                    self.button_width,
                                    self.button_height)

        return restart_btn, menu_btn
