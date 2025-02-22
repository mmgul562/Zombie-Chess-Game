import pygame

import random
import os


class ScrollableSection:
    def __init__(self, screen, rect, font, text_color):
        self.screen = screen
        self.rect = rect
        self.font = font
        self.text_color = text_color
        self.LIGHT_BROWN = (255, 248, 220)
        self.DARK_BROWN = (193, 120, 50)

        self.scroll_y = 0
        self.scroll_x = 0
        self.max_content_width = 0
        self.content_surface = None
        self.content_height = 0
        self.scroll_speed = 40

    def set_content(self, content_lines):
        line_height = self.font.get_linesize()
        padding = 10

        max_line_width = 0
        rendered_lines = []
        for line in content_lines:
            text_surface = self.font.render(line, True, self.text_color)
            max_line_width = max(max_line_width, text_surface.get_width())
            rendered_lines.append(text_surface)

        self.max_content_width = max_line_width + (2 * padding)
        self.content_height = (len(content_lines) * line_height) + (padding * 2)

        self.content_surface = pygame.Surface((self.max_content_width, self.content_height))
        self.content_surface.fill(self.DARK_BROWN)

        y = padding
        for text_surface in rendered_lines:
            text_rect = text_surface.get_rect(left=padding, top=y)
            self.content_surface.blit(text_surface, text_rect)
            y += line_height

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            keys = pygame.key.get_mods()
            if keys & pygame.KMOD_SHIFT:
                self.scroll_x = max(
                    min(self.scroll_x - (event.y * self.scroll_speed),
                        self.max_content_width - self.rect.width),
                    0
                )
            else:
                self.scroll_y = max(
                    min(self.scroll_y - (event.y * self.scroll_speed),
                        self.content_height - self.rect.height),
                    0
                )

    def draw(self):
        if self.content_surface is None:
            return

        visible_rect = pygame.Rect(
            self.scroll_x,
            self.scroll_y,
            self.rect.width,
            self.rect.height
        )
        visible_surface = self.content_surface.subsurface(visible_rect)

        self.screen.blit(visible_surface, self.rect)

        if self.content_height > self.rect.height:
            scroll_bar_height = (self.rect.height / self.content_height) * self.rect.height
            scroll_bar_pos = (self.scroll_y / self.content_height) * self.rect.height

            vertical_scroll_bar = pygame.Rect(
                self.rect.right + 10,
                self.rect.top + scroll_bar_pos,
                5,
                scroll_bar_height
            )
            pygame.draw.rect(self.screen, self.LIGHT_BROWN, vertical_scroll_bar)

        if self.max_content_width > self.rect.width:
            scroll_bar_width = (self.rect.width / self.max_content_width) * self.rect.width
            scroll_bar_pos = (self.scroll_x / self.max_content_width) * self.rect.width

            horizontal_scroll_bar = pygame.Rect(
                self.rect.left + scroll_bar_pos,
                self.rect.bottom + 10,
                scroll_bar_width,
                5
            )
            pygame.draw.rect(self.screen, self.LIGHT_BROWN, horizontal_scroll_bar)


class Menu:
    def __init__(self, screen, screen_width, screen_height, piece_images):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.aspect_ratio = screen_width / screen_height

        self.piece_images = piece_images
        if self.aspect_ratio == 16 / 9:
            background_images = ('bg_blur.png', 'bg_alt_blur.png')
            bg_index = random.randint(0, 1)
            bg = pygame.image.load(os.path.join('img/backgrounds/16-9', background_images[bg_index]))
            self.background = pygame.transform.scale(bg, (self.screen_width, self.screen_height))

        self.LIGHT_BROWN = (255, 248, 220)
        self.BROWN = (193, 120, 50)
        self.DARK_BROWN = (153, 90, 32)
        self.YELLOW = (255, 244, 108)
        self.GREY = (136, 145, 153)
        self.BOARD_COLORS = ((255, 215, 175), (205, 132, 55))
        self.SEPARATOR_COLOR = (223, 178, 110)
        self.HIGHLIGHT_COLOR = (75, 200, 70, 128)
        self.OUTLINE_COLOR = (40, 15, 5)

        self.scale_factor = min(screen_width, screen_height) / 1000

        self.main_font_size = int(60 * self.scale_factor)
        self.regular_font_size = int(36 * self.scale_factor)
        self.section_font_size = int(40 * self.scale_factor)

        self.section_spacing = int(screen_height * 0.12)
        self.element_spacing = int(screen_height * 0.08)

        self.button_width = int(screen_width * 0.2)
        self.button_height = int(screen_height * 0.06)
        self.small_button_width = int(self.button_width * 0.3)
        self.small_button_height = int(self.button_height * 0.8)

        self.title_y = int(screen_height * 0.08)
        self.content_start_y = int(screen_height * 0.22)
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

        self.hover_scale = 1.1
        self.current_scale = 1.0
        self.animation_speed = 0.02
        self.current_scales = {}

    def draw_background(self):
        if self.aspect_ratio != 16 / 9:
            self.screen.fill(self.BROWN)
        else:
            self.screen.blit(self.background, (0, 0))

    def draw_main_text(self, text, color, outline_color=None, outline_width=4, y_pos=None):
        x = self.screen_width // 2
        if y_pos is None:
            y_pos = self.title_y
        if outline_color is None:
            outline_color = self.OUTLINE_COLOR

        for offset_x in range(-outline_width, outline_width + 1):
            for offset_y in range(-outline_width, outline_width + 1):
                if offset_x == 0 and offset_y == 0:
                    continue
                outline_surface = self.main_font.render(text, True, outline_color)
                outline_rect = outline_surface.get_rect(center=(x + offset_x, y_pos + offset_y))
                self.screen.blit(outline_surface, outline_rect)

        text_surface = self.main_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y_pos))
        self.screen.blit(text_surface, text_rect)

    def draw_section_text(self, text, color, x, y, outline_color=None, outline_width=3):
        if outline_color is None:
            outline_color = self.OUTLINE_COLOR

        for offset_x in range(-outline_width, outline_width + 1):
            for offset_y in range(-outline_width, outline_width + 1):
                if offset_x == 0 and offset_y == 0:
                    continue
                outline_surface = self.section_font.render(text, True, outline_color)
                outline_rect = outline_surface.get_rect(center=(x + offset_x, y + offset_y))
                self.screen.blit(outline_surface, outline_rect)

        text_surface = self.section_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_text(self, text, color, x, y, outline_color=None, outline_width=2):
        if outline_color:
            for offset_x in range(-outline_width, outline_width + 1):
                for offset_y in range(-outline_width, outline_width + 1):
                    if offset_x == 0 and offset_y == 0:
                        continue
                    outline_surface = self.font.render(text, True, outline_color)
                    outline_rect = outline_surface.get_rect(center=(x + offset_x, y + offset_y))
                    self.screen.blit(outline_surface, outline_rect)

        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_section_row(self, section_name, description, y_pos, buttons_info, disabled=False):
        text_color = self.LIGHT_BROWN if not disabled else self.GREY
        self.draw_section_text(section_name, text_color, self.left_section_x, y_pos)

        self.draw_text(str(description), text_color, self.middle_section_x, y_pos, outline_color=self.OUTLINE_COLOR)

        buttons = []
        for i, (text, width, button_disabled) in enumerate(buttons_info):
            x_offset = self.right_section_x - self.middle_section_x + (i * int(self.small_button_width * 1.2))
            btn = self.draw_button(text, y_pos,
                                   width=width or self.small_button_width,
                                   height=self.small_button_height,
                                   x_offset=x_offset, disabled=button_disabled)
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

    def draw_button(self, text, y, x=None, width=None, height=None, x_offset=0, disabled=False):
        if width is None:
            width = self.button_width
        if height is None:
            height = self.button_height

        if x is None:
            x = (self.screen_width // 2) - (width // 2) + x_offset

        button_rect = pygame.Rect(x, y - height // 2, width, height)
        current_scale = 1.0
        if not disabled:
            button_id = (x, y)

            if button_id not in self.current_scales:
                self.current_scales[button_id] = 1.0

            mouse_pos = pygame.mouse.get_pos()
            is_hovered = button_rect.collidepoint(mouse_pos)

            current_scale = self.current_scales[button_id]
            target_scale = self.hover_scale if is_hovered else 1.0

            if current_scale < target_scale:
                current_scale = min(current_scale + self.animation_speed, target_scale)
            elif current_scale > target_scale:
                current_scale = max(current_scale - self.animation_speed, target_scale)

            self.current_scales[button_id] = current_scale

        scaled_width = int(width * current_scale)
        scaled_height = int(height * current_scale)
        scaled_x = x - (scaled_width - width) // 2
        scaled_y = y - scaled_height // 2

        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)

        color = self.YELLOW if not disabled else self.GREY

        try:
            pygame.draw.rect(self.screen, color, scaled_rect, border_radius=10)
            pygame.draw.rect(self.screen, self.LIGHT_BROWN, scaled_rect, 2, border_radius=10)
        except TypeError:
            pygame.draw.rect(self.screen, color, scaled_rect)
            pygame.draw.rect(self.screen, self.LIGHT_BROWN, scaled_rect, 2)

        scaled_font = pygame.font.Font('util/Roboto-Regular.ttf',
                                       int(self.regular_font_size * current_scale))
        text_surface = scaled_font.render(text, True, self.BROWN)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        self.screen.blit(text_surface, text_rect)

        return button_rect

    def pawn_promotion_menu(self):
        popup_width = int(self.screen_width * 0.3)
        popup_height = int(self.screen_height * 0.15)
        popup_x = (self.screen_width - popup_width) // 2
        popup_y = (self.screen_height - popup_height) // 2

        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.screen, self.LIGHT_BROWN,
                         (popup_x, popup_y, popup_width, popup_height))
        pygame.draw.rect(self.screen, self.BROWN,
                         (popup_x, popup_y, popup_width, popup_height), 2)

        piece_size = min(popup_height - 60, popup_width // 4 - 20)
        pieces = ('pq', 'pr', 'pb', 'pk')
        piece_y = popup_y + (popup_height - piece_size) // 2
        spacing = (popup_width - (len(pieces) * piece_size)) // (len(pieces) + 1)

        piece_areas = {}
        for i, piece in enumerate(pieces):
            piece_x = popup_x + spacing + (i * (piece_size + spacing))

            pygame.draw.rect(self.screen, self.YELLOW,
                             (piece_x, piece_y, piece_size, piece_size))
            pygame.draw.rect(self.screen, self.BROWN,
                             (piece_x, piece_y, piece_size, piece_size), 1)

            if piece in self.piece_images:
                image = pygame.transform.scale(self.piece_images[piece], (piece_size - 10, piece_size - 10))
                image_x = piece_x + 5
                image_y = piece_y + 5
                self.screen.blit(image, (image_x, image_y))

            piece_areas[piece] = pygame.Rect(piece_x, piece_y, piece_size, piece_size)

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for piece, area in piece_areas.items():
                        if area.collidepoint(mouse_pos):
                            return piece
                elif event.type == pygame.QUIT:
                    return None

    def main_menu(self):
        self.draw_background()
        self.draw_main_text('Zombie Chess Game', self.LIGHT_BROWN, self.OUTLINE_COLOR)

        first_button_y = self.content_start_y + self.element_spacing
        second_button_y = first_button_y + self.button_height + self.element_spacing
        third_button_y = second_button_y + self.button_height + self.element_spacing
        fourth_button_y = third_button_y + self.button_height + self.element_spacing

        play_btn = self.draw_button('Play', first_button_y)
        custom_btn = self.draw_button('Custom Modes', second_button_y)
        help_btn = self.draw_button('Help', third_button_y)
        quit_btn = self.draw_button('Quit', fourth_button_y)

        return play_btn, custom_btn, help_btn, quit_btn

    def custom_menu(self):
        self.draw_background()
        self.draw_main_text('Custom Modes', self.LIGHT_BROWN, self.OUTLINE_COLOR)

        first_button_y = self.content_start_y + self.element_spacing
        second_button_y = first_button_y + self.button_height + self.element_spacing

        create_btn = self.draw_button('Create New Mode', first_button_y)
        load_btn = self.draw_button('Load New Mode', second_button_y)

        left_offset = -int(self.screen_width * 0.3)
        go_back_btn = self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)

        return create_btn, load_btn, go_back_btn

    def create_custom_menu(self, board_y, board, selected_piece, has_king):
        self.draw_background()

        base_board_height = self.screen_height * 0.7
        square_size = min(base_board_height // board_y, (self.screen_width * 0.5) // 8)
        board_width = square_size * 8
        board_height = square_size * board_y
        board_start_x = (self.screen_width // 2) - (board_width // 2)
        board_start_y = (self.screen_height - board_height) // 4

        piece_selector_width = int(self.screen_width * 0.15)
        sections_gap = int(self.screen_width * 0.1) // 4
        settings_x = board_start_x + board_width + sections_gap
        piece_selector_x = board_start_x - piece_selector_width - sections_gap

        add_board_height_btn = self.draw_button('+',
                                                board_start_y + base_board_height // 2 - self.font.get_height() * 1.5,
                                                width=self.small_button_width, x=settings_x)
        self.draw_text(str(board_y), self.LIGHT_BROWN, add_board_height_btn.centerx,
                       board_start_y + base_board_height // 2)
        rm_board_height_btn = self.draw_button('-',
                                               board_start_y + base_board_height // 2 + self.font.get_height() * 1.5,
                                               width=self.small_button_width, x=settings_x)

        pygame.draw.rect(self.screen, self.DARK_BROWN,
                         (board_start_x - 5, board_start_y - 5, board_width + 10, board_height + 10), 5)
        for row in range(board_y):
            for col in range(8):
                x = board_start_x + (col * square_size)
                y = board_start_y + (row * square_size)
                color = self.BOARD_COLORS[(row + col) % 2]
                pygame.draw.rect(self.screen, color, (x, y, square_size, square_size))

                piece = board[row][col]
                if piece in self.piece_images:
                    piece_size = square_size - 10
                    image = pygame.transform.scale(
                        self.piece_images[piece],
                        (piece_size, piece_size)
                    )
                    self.screen.blit(image, (x + 5, y + 5))

        pygame.draw.rect(self.screen, self.SEPARATOR_COLOR,
                         (piece_selector_x, board_start_y, piece_selector_width, base_board_height))
        self.draw_section_text('Available Pieces', self.LIGHT_BROWN,
                               piece_selector_x + piece_selector_width // 2, board_start_y - 40)

        pieces = ('pK', 'pq', 'pr', 'pb', 'pk', 'pp')
        zombies = ('zw', 'zs', 'ze', 'zi')

        piece_size = int((base_board_height // 6) * 0.8)
        piece_gap = (base_board_height - (6 * piece_size)) // 7
        selector_square_size = piece_size + 10
        list_gap = (piece_selector_width - 2 * selector_square_size) // 3
        highlight_surface = pygame.Surface((selector_square_size, selector_square_size), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surface, self.HIGHLIGHT_COLOR,
                         (0, 0, selector_square_size, selector_square_size))

        for i, piece in enumerate(pieces):
            if piece in self.piece_images:
                piece_x = piece_selector_x + 2 * list_gap + selector_square_size
                piece_y = board_start_y + (i * (piece_size + piece_gap)) + piece_gap

                pygame.draw.rect(self.screen, self.YELLOW,
                                 (piece_x - 5, piece_y - 5, selector_square_size, selector_square_size))
                if i == 0:
                    pygame.draw.rect(self.screen, self.DARK_BROWN,
                                     (piece_x - 5, piece_y - 5, selector_square_size, selector_square_size), 3)
                else:
                    pygame.draw.rect(self.screen, self.LIGHT_BROWN,
                                     (piece_x - 5, piece_y - 5, selector_square_size, selector_square_size), 2)

                if piece is selected_piece:
                    self.screen.blit(highlight_surface, (piece_x - 5, piece_y - 5))

                image = pygame.transform.scale(self.piece_images[piece], (piece_size, piece_size))
                self.screen.blit(image, (piece_x, piece_y))

        for i, zombie in enumerate(zombies):
            if zombie in self.piece_images:
                zombie_x = piece_selector_x + list_gap
                zombie_y = board_start_y + (i * (piece_size + piece_gap)) + piece_gap

                pygame.draw.rect(self.screen, self.YELLOW,
                                 (zombie_x - 5, zombie_y - 5, selector_square_size, selector_square_size))
                pygame.draw.rect(self.screen, self.LIGHT_BROWN,
                                 (zombie_x - 5, zombie_y - 5, selector_square_size, selector_square_size), 2)

                if zombie is selected_piece:
                    self.screen.blit(highlight_surface, (zombie_x - 5, zombie_y - 5))

                image = pygame.transform.scale(self.piece_images[zombie], (piece_size, piece_size))
                self.screen.blit(image, (zombie_x, zombie_y))
        left_offset = -int(self.screen_width * 0.3)
        right_offset = int(self.screen_width * 0.3)

        go_back_btn = self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)
        clear_board_btn = self.draw_button('Clear Board', self.bottom_margin)
        next_btn = self.draw_button('Next', self.bottom_margin, x_offset=right_offset, disabled=not has_king)

        return {
            'board_area': pygame.Rect(board_start_x, board_start_y, board_width, board_height),
            'square_size': square_size,
            'board_start': (board_start_x, board_start_y),
            'pieces': [
                [(piece, pygame.Rect(
                    piece_selector_x + 2 * list_gap + selector_square_size,
                    board_start_y + (i * (piece_size + piece_gap)) + piece_gap,
                    piece_size, piece_size
                )) for i, piece in enumerate(pieces)],
                [(zombie, pygame.Rect(
                    piece_selector_x + list_gap,
                    board_start_y + (i * (piece_size + piece_gap)) + piece_gap,
                    piece_size, piece_size
                )) for i, zombie in enumerate(zombies)]
            ],
            'buttons': {
                'add_board_height': add_board_height_btn,
                'rm_board_height': rm_board_height_btn,
                'next': next_btn,
                'clear': clear_board_btn,
                'back': go_back_btn
            }
        }

    def save_custom_menu(self, game_mode, difficulty, gm_disabled, difficulty_disabled, name, is_focused, name_ok):
        self.draw_background()
        self.draw_main_text('Settings', self.LIGHT_BROWN, self.OUTLINE_COLOR)

        first_section_y = self.content_start_y
        second_section_y = first_section_y + self.section_spacing
        third_section_y = second_section_y + self.section_spacing
        fourth_section_y = third_section_y + int(1.25 * self.section_spacing)
        fifth_section_y = fourth_section_y + self.section_spacing

        change_game_mode_btn, disable_game_mode_btn = self.draw_section_row(
            'Base Game Mode', game_mode, first_section_y,
            [('>', None, gm_disabled), ('X', None, False)],
            disabled=gm_disabled
        )
        self.draw_separator(first_section_y + self.element_spacing // 2)

        change_difficulty_btn, disable_difficulty_btn = self.draw_section_row(
            'Difficulty', difficulty, second_section_y,
            [('>', None, difficulty_disabled), ('X', None, False)],
            disabled=difficulty_disabled
        )
        self.draw_separator(second_section_y + self.element_spacing // 2)

        self.draw_section_text('Specifying a setting here will disallow any changes to that setting later',
                               self.LIGHT_BROWN,
                               self.screen_width // 2, third_section_y)

        # name
        input_color = self.DARK_BROWN
        if not name:
            name = 'Name'
            input_color = self.GREY
        input_width = self.screen_width * 0.6
        input_height = self.font.get_height() * 1.5
        input_start_x = self.screen_width // 2 - input_width // 2
        if is_focused:
            pygame.draw.rect(self.screen, self.HIGHLIGHT_COLOR,
                             (input_start_x - 2, fourth_section_y - 2, input_width + 4, input_height + 4), 6)
        else:
            pygame.draw.rect(self.screen, self.SEPARATOR_COLOR,
                             (input_start_x, fourth_section_y, input_width, input_height), 4)
        input_rect = pygame.Rect(input_start_x + 4, fourth_section_y + 4, input_width - 8, input_height - 8)
        pygame.draw.rect(self.screen, self.LIGHT_BROWN, input_rect)
        text_surface = self.font.render(name, True, input_color)
        self.screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 8))

        self.draw_text('Name should be at least 3 and at most 20 characters long',
                       self.LIGHT_BROWN,
                       self.screen_width // 2, fifth_section_y,
                       outline_color=self.OUTLINE_COLOR)

        left_offset = -int(self.screen_width * 0.3)
        right_offset = int(self.screen_width * 0.3)

        go_back_btn = self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)
        save_btn = self.draw_button('Save', self.bottom_margin, x_offset=right_offset, disabled=not name_ok)

        return {
            'input_area': input_rect,
            'buttons': {
                'change_gm': change_game_mode_btn,
                'disable_gm': disable_game_mode_btn,
                'change_difficulty': change_difficulty_btn,
                'disable_difficulty': disable_difficulty_btn,
                'back': go_back_btn,
                'save': save_btn
            }
        }

    def load_custom_menu(self):
        self.draw_background()
        self.draw_main_text('Load Custom Mode', self.LIGHT_BROWN, self.OUTLINE_COLOR)

        left_offset = -int(self.screen_width * 0.3)
        go_back_btn = self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)

        return go_back_btn

    def game_settings_menu(self, game_mode, difficulty, board_y):
        self.draw_background()
        self.draw_main_text('Play', self.LIGHT_BROWN, self.OUTLINE_COLOR)

        first_section_y = self.content_start_y
        second_section_y = first_section_y + self.section_spacing
        third_section_y = second_section_y + self.section_spacing

        game_mode_btn, = self.draw_section_row(
            'Game Mode', game_mode, first_section_y,
            [('>', None, False)]
        )
        self.draw_separator(first_section_y + self.element_spacing // 2)

        difficulty_btn, = self.draw_section_row(
            'Difficulty', difficulty, second_section_y,
            [('>', None, False)]
        )
        self.draw_separator(second_section_y + self.element_spacing // 2)

        add_btn, rm_btn = self.draw_section_row(
            'Board Height', str(board_y), third_section_y,
            [('+', None, False), ('-', None, False)]
        )
        self.draw_separator(third_section_y + self.element_spacing // 2)

        left_offset = -int(self.screen_width * 0.3)
        right_offset = int(self.screen_width * 0.3)

        go_back_btn = self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)
        play_btn = self.draw_button('Play', self.bottom_margin, x_offset=right_offset)

        buttons = (game_mode_btn, difficulty_btn, add_btn, rm_btn, play_btn, go_back_btn)
        return buttons

    def information_menu(self, main_text, first_btn_text, second_btn_text, additional_info=None):
        self.draw_background()
        self.draw_main_text(main_text, self.LIGHT_BROWN, self.OUTLINE_COLOR)

        info_y = self.content_start_y + self.element_spacing
        if additional_info:
            self.draw_text(additional_info, self.LIGHT_BROWN, self.screen_width // 2, info_y,
                           outline_color=self.OUTLINE_COLOR)

        first_button_y = info_y + self.section_spacing
        second_button_y = first_button_y + self.button_height + self.element_spacing

        first_btn = self.draw_button(first_btn_text, first_button_y)
        second_btn = self.draw_button(second_btn_text, second_button_y)

        return first_btn, second_btn

    def help_menu(self):
        self.draw_background()
        self.draw_main_text('Help', self.LIGHT_BROWN, self.OUTLINE_COLOR)

        content_rect = pygame.Rect(
            int(self.screen_width * 0.1),
            self.content_start_y,
            int(self.screen_width * 0.8),
            int(self.screen_height * 0.6)
        )

        help_section = ScrollableSection(
            self.screen,
            content_rect,
            self.font,
            self.LIGHT_BROWN
        )

        help_content = [
            "1. Rules:",
            "   Player:",
            "       - can make all traditional chess moves",
            "       - cannot move the same piece two turns in a row",
            "       - can capture enemy pieces by applying the same traditional chess moveset",
            "       - can change the height of the game board (6-14) before the game starts",
            "       - can move the King into a checkmate position, without any warning. "
            "The game will then end immediately",
            "",
            "   Enemy:",
            "       - will spawn between 0-x zombies every turn, where x depends on the difficulty",
            "       - will move every zombie each turn to the first spot unoccupied by another zombie, in this order:",
            "           > downward",
            "           > to the right",
            "           > to the left",
            "       - will turn player's piece into another zombie, if that piece stands in a spot that the zombie "
            "would reach in its current move",
            "",
            "   The game ends when the king is turned into a zombie",
            "",
            "",
            "2. Game Modes:",
            "   - Survive The Longest:",
            "       > player has no win condition",
            "       > every turn passing increases the score",
            "       > play to get the highest score",
            "",
            "   - Capture The Most:",
            "       > player has no win condition",
            "       > every zombie captured increases the score",
            "       > play to get the highest score",
            "",
            "   - Block The Border:",
            "       > player wins when every spot of the top row is occupied by the player's pieces",
            "       > every spot of the top row currently occupied by the player's piece will not spawn any zombies",
            "",
            "   - Block And Clear:",
            "       > player wins when every spot of the top row is occupied by the player's pieces "
            "and no zombie is left on the board",
            "       > every spot of the top row currently occupied by the player's piece will not spawn any zombies",
            "",
            "",
            "3. Difficulty Levels:",
            "   - Easy: spawns up to 1 zombie each turn, player can move the same piece every turn",
            "   - Normal: spawns up to 1 zombie each turn",
            "   - Hard: spawns up to 2 zombies each turn",
            "   - Extreme: spawns up to 3 zombies each turn",
            "",
        ]

        help_section.set_content(help_content)

        left_offset = -int(self.screen_width * 0.3)
        go_back_btn = self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)

        return help_section, go_back_btn

    def update_help_menu(self, scrollable_section):
        self.draw_background()
        self.draw_main_text('Help', self.LIGHT_BROWN, self.OUTLINE_COLOR)
        left_offset = -int(self.screen_width * 0.3)
        self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)
        scrollable_section.draw()
