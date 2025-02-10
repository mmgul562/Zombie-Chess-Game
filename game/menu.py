import pygame


class Menu:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.LIGHT_BROWN = (255, 248, 220)
        self.DARK_BROWN = (193, 120, 50)
        self.YELLOW = (255, 245, 95)
        self.SEPARATOR_COLOR = (223, 178, 110)

        self.scale_factor = min(screen_width, screen_height) / 1000

        self.main_font_size = int(70 * self.scale_factor)
        self.regular_font_size = int(42 * self.scale_factor)
        self.section_font_size = int(50 * self.scale_factor)

        self.section_spacing = int(screen_height * 0.12)
        self.element_spacing = int(screen_height * 0.08)

        self.button_width = int(screen_width * 0.3)
        self.button_height = int(screen_height * 0.08)
        self.small_button_width = int(self.button_width * 0.3)
        self.small_button_height = int(self.button_height * 0.8)

        self.title_y = int(screen_height * 0.12)
        self.content_start_y = int(screen_height * 0.25)
        self.bottom_margin = int(screen_height * 0.9)

        self.left_section_x = int(screen_width * 0.2)
        self.middle_section_x = int(screen_width * 0.5)
        self.right_section_x = int(screen_width * 0.75)

        self.separator_start_x = int(screen_width * 0.1)
        self.separator_end_x = int(screen_width * 0.9)
        self.separator_thickness = max(2, int(self.scale_factor * 2))

        self.main_font = pygame.font.Font('util/Roboto-Bold.ttf', self.main_font_size)
        self.font = pygame.font.Font('util/Roboto-Regular.ttf', self.regular_font_size)
        self.section_font = pygame.font.Font('util/Roboto-Bold.ttf', self.section_font_size)

    def draw_main_text(self, text, color, y_pos=None):
        if y_pos is None:
            y_pos = self.title_y
        text_surface = self.main_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_pos))
        self.screen.blit(text_surface, text_rect)

    def draw_section_text(self, text, color, x, y):
        text_surface = self.section_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_text(self, text, color, x, y):
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_section_row(self, section_name, description, y_pos, buttons_info):
        self.draw_section_text(section_name, self.LIGHT_BROWN, self.left_section_x, y_pos)

        self.draw_text(str(description), self.LIGHT_BROWN, self.middle_section_x, y_pos)

        buttons = []
        for i, (text, width) in enumerate(buttons_info):
            x_offset = self.right_section_x - self.middle_section_x + (i * int(self.small_button_width * 1.2))
            btn = self.draw_button(text, y_pos,
                                   width=width or self.small_button_width,
                                   height=self.small_button_height,
                                   x_offset=x_offset)
            buttons.append(btn)
        return buttons

    def draw_separator(self, y_pos):
        pygame.draw.line(
            self.screen,
            self.SEPARATOR_COLOR,
            (self.separator_start_x, y_pos),
            (self.separator_end_x, y_pos),
            self.separator_thickness
        )

    def draw_button(self, text, y_pos, width=None, height=None, x_offset=0):
        if width is None:
            width = self.button_width
        if height is None:
            height = self.button_height

        x = (self.screen_width // 2) - (width // 2) + x_offset

        button_rect = pygame.Rect(
            x,
            y_pos - height // 2,
            width,
            height
        )

        try:
            pygame.draw.rect(self.screen, self.YELLOW, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, self.LIGHT_BROWN, button_rect, 2, border_radius=10)
        except TypeError:
            pygame.draw.rect(self.screen, self.YELLOW, button_rect)
            pygame.draw.rect(self.screen, self.LIGHT_BROWN, button_rect, 2)

        text_surface = self.font.render(text, True, self.DARK_BROWN)
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)

        return button_rect

    def main_menu(self):
        self.screen.fill(self.DARK_BROWN)
        self.draw_main_text('Zombie Chess Game', self.LIGHT_BROWN)

        first_button_y = self.content_start_y + self.section_spacing
        second_button_y = first_button_y + self.button_height + self.element_spacing

        play_btn = self.draw_button('Play', first_button_y)
        quit_btn = self.draw_button('Quit', second_button_y)

        return play_btn, quit_btn

    def game_settings_menu(self, game_mode, difficulty, board_y):
        self.screen.fill(self.DARK_BROWN)
        self.draw_main_text('Zombie Chess Game', self.LIGHT_BROWN)

        first_section_y = self.content_start_y
        second_section_y = first_section_y + self.section_spacing
        third_section_y = second_section_y + self.section_spacing

        game_mode_btn, = self.draw_section_row(
            'Game Mode', game_mode, first_section_y,
            [('>', None)]
        )
        self.draw_separator(first_section_y + self.element_spacing // 2)

        difficulty_btn, = self.draw_section_row(
            'Difficulty', difficulty, second_section_y,
            [('>', None)]
        )
        self.draw_separator(second_section_y + self.element_spacing // 2)

        add_btn, rm_btn = self.draw_section_row(
            'Board Height', str(board_y), third_section_y,
            [('+', None), ('-', None)]
        )
        self.draw_separator(third_section_y + self.element_spacing // 2)

        left_offset = -int(self.screen_width * 0.3)
        right_offset = int(self.screen_width * 0.3)

        go_back_btn = self.draw_button('Go Back', self.bottom_margin,
                                       x_offset=left_offset)
        play_btn = self.draw_button('Play', self.bottom_margin,
                                    x_offset=right_offset)

        buttons = (game_mode_btn, difficulty_btn, add_btn, rm_btn, play_btn, go_back_btn)
        return buttons

    def game_over_menu(self, endgame_info):
        self.screen.fill(self.DARK_BROWN)
        self.draw_main_text('Game Over!', self.LIGHT_BROWN)

        info_y = self.content_start_y + self.element_spacing
        self.draw_text(endgame_info, self.LIGHT_BROWN, self.screen_width // 2, info_y)

        first_button_y = info_y + self.section_spacing
        second_button_y = first_button_y + self.button_height + self.element_spacing

        restart_btn = self.draw_button('Play Again', first_button_y)
        menu_btn = self.draw_button('Main Menu', second_button_y)

        return restart_btn, menu_btn
