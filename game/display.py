import pygame

import random
import os


class Display:
    def __init__(self, screen, screen_width, screen_height, screen_border_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen_border_height = screen_border_height
        self.aspect_ratio = screen_width / screen_height

        self.LIGHT_BROWN = (255, 248, 220)
        self.BROWN = (193, 120, 50)
        self.DARK_BROWN = (153, 90, 32)
        self.YELLOW = (255, 244, 108)
        self.GREY = (136, 145, 153)
        self.BOARD_COLORS = ((255, 215, 175), (205, 132, 55))
        self.SEPARATOR_COLOR = (223, 178, 110)
        self.HIGHLIGHT_COLOR = (0, 162, 232, 128)
        self.OUTLINE_COLOR = (40, 15, 5)

        self.popup_background = None
        self.background = None
        self.set_background()
        self.piece_images = {}
        self.load_piece_images()

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
        self.content_start_y = int(screen_height * 0.2)
        self.bottom_margin = int(screen_height * 0.9)

        self.main_font = pygame.font.Font('util/Roboto-Bold.ttf', self.main_font_size)
        self.font = pygame.font.Font('util/Roboto-Regular.ttf', self.regular_font_size)
        self.section_font = pygame.font.Font('util/Roboto-Bold.ttf', self.section_font_size)

    def set_background(self):
        if self.aspect_ratio == 16 / 9:
            background_images = ('bg_blur.png', 'bg_alt_blur.png')
            bg_index = random.randint(0, 1)
            bg = pygame.image.load(os.path.join('img/backgrounds/16-9', background_images[bg_index]))
            self.background = pygame.transform.scale(bg, (self.screen_width, self.screen_height))
        else:
            self.background = pygame.Surface((self.screen_width, self.screen_height))
            self.background.fill(self.BROWN)

    def load_piece_images(self):
        pieces = {'pawn', 'rook', 'knight', 'bishop', 'queen', 'King',
                  'zombie_walker', 'zombie_stomper', 'zombie_infected', 'zombie_exploding'}

        for piece in pieces:
            filename = piece + '.png'
            piece_name = f'p{piece[0]}' if piece[0] != 'z' else f'z{piece[7]}'
            try:
                image = pygame.image.load(os.path.join('img/chess_pieces', filename))
                self.piece_images[piece_name] = image
            except Exception as e:
                print(f'Could not load image {filename}: {e}')

    def switch_screen_display(self):
        self.screen_height -= self.screen_border_height
        self.screen_border_height = -self.screen_border_height

    def set_popup_background(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        self.popup_background = self.screen.copy()

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

    def draw_section_text(self, text, color, x, y, center=True, outline_color=None, outline_width=3):
        if outline_color is None:
            outline_color = self.OUTLINE_COLOR

        for offset_x in range(-outline_width, outline_width + 1):
            for offset_y in range(-outline_width, outline_width + 1):
                if offset_x == 0 and offset_y == 0:
                    continue
                outline_surface = self.section_font.render(text, True, outline_color)
                if center:
                    outline_rect = outline_surface.get_rect(center=(x + offset_x, y + offset_y))
                else:
                    outline_rect = outline_surface.get_rect(x=x + offset_x, y=y + offset_y)
                self.screen.blit(outline_surface, outline_rect)

        text_surface = self.section_font.render(text, True, color)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
        else:
            text_rect = text_surface.get_rect(x=x, y=y)
        self.screen.blit(text_surface, text_rect)

    def draw_text(self, text, color, x, y, center=True, outline_color=None, outline_width=2):
        if outline_color:
            for offset_x in range(-outline_width, outline_width + 1):
                for offset_y in range(-outline_width, outline_width + 1):
                    if offset_x == 0 and offset_y == 0:
                        continue
                    outline_surface = self.font.render(text, True, outline_color)
                    if center:
                        outline_rect = outline_surface.get_rect(center=(x + offset_x, y + offset_y))
                    else:
                        outline_rect = outline_surface.get_rect(x=x + offset_x, y=y + offset_y)
                    self.screen.blit(outline_surface, outline_rect)

        text_surface = self.font.render(text, True, color)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
        else:
            text_rect = text_surface.get_rect(x=x, y=y)
        self.screen.blit(text_surface, text_rect)

    def draw_section_row(self, section_name, description, y_pos, buttons_info, disabled=False):
        text_color = self.LIGHT_BROWN if not disabled else self.GREY
        self.draw_section_text(section_name, text_color, int(self.screen_width * 0.2), y_pos)

        middle_section_x = int(self.screen_width * 0.5)
        self.draw_text(str(description), text_color, middle_section_x, y_pos, outline_color=self.OUTLINE_COLOR)

        buttons = []
        for i, (text, width, button_disabled) in enumerate(buttons_info):
            x_offset = int(self.screen_width * 0.75) - middle_section_x + (i * int(self.small_button_width * 1.2))
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
            (int(self.screen_width * 0.1), y_pos),
            (int(self.screen_width * 0.9), y_pos),
            max(2, int(self.scale_factor * 2))
        )

    def draw_button(self, text, y, x=None, width=None, height=None, x_offset=0, disabled=False):
        if width is None:
            width = self.button_width
        if height is None:
            height = self.button_height
        if x is None:
            x = (self.screen_width // 2) - (width // 2) + x_offset

        bg_color = self.YELLOW if not disabled else self.GREY
        text_color = self.DARK_BROWN

        button_rect = pygame.Rect(x, y - height // 2, width, height)
        if not disabled and button_rect.collidepoint(pygame.mouse.get_pos()):
            bg_color = self.HIGHLIGHT_COLOR
            text_color = self.LIGHT_BROWN

        try:
            pygame.draw.rect(self.screen, bg_color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, self.LIGHT_BROWN, button_rect, 2, border_radius=10)
        except TypeError:
            pygame.draw.rect(self.screen, bg_color, button_rect)
            pygame.draw.rect(self.screen, self.LIGHT_BROWN, button_rect, 2)

        text_surface = self.font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)

        return button_rect

    def draw_board(self, rows, cols, board, x, y, square_size):
        for row in range(rows):
            for col in range(cols):
                square_color = self.BOARD_COLORS[(row + col) % 2]
                square_rect = pygame.Rect(
                    x + col * square_size,
                    y + row * square_size,
                    square_size,
                    square_size
                )
                pygame.draw.rect(self.screen, square_color, square_rect)

                piece = board[row][col]
                if piece and piece[:2] in self.piece_images:
                    image = pygame.transform.scale(self.piece_images[piece[:2]],
                                                   (square_size - 10, square_size - 10))
                    self.screen.blit(image,
                                     ((col * square_size + 5) + x,
                                      (row * square_size + 5) + y))

    def information_menu(self, main_text, first_btn_text, second_btn_text, additional_info=None):
        self.screen.blit(self.background, (0, 0))
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

    def main_menu(self):
        self.screen.blit(self.background, (0, 0))
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
        self.screen.blit(self.background, (0, 0))
        self.draw_main_text('Custom Modes', self.LIGHT_BROWN, self.OUTLINE_COLOR)

        first_button_y = self.content_start_y + self.element_spacing
        second_button_y = first_button_y + self.button_height + self.element_spacing

        create_btn = self.draw_button('Create New Mode', first_button_y)
        load_btn = self.draw_button('Load New Mode', second_button_y)

        left_offset = -int(self.screen_width * 0.35)
        go_back_btn = self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)

        return create_btn, load_btn, go_back_btn

    def create_custom_menu(self, board_height, board, selected_piece, has_king):
        self.screen.blit(self.background, (0, 0))

        board_height_px = self.screen_height * 0.7
        square_size = board_height_px // max(8, board_height)
        board_width = square_size * 8
        board_start_x = (self.screen_width // 2) - (board_width // 2)
        board_start_y = (self.screen_height - board_height_px) // 4

        piece_selector_width = int(self.screen_width * 0.15)
        sections_gap = int(self.screen_width * 0.1) // 2
        settings_x = self.screen_width - sections_gap - self.small_button_width
        piece_selector_x = sections_gap

        add_board_height_btn = self.draw_button('+',
                                                board_start_y + board_height_px // 2 - self.font.get_height() * 1.5,
                                                width=self.small_button_width, x=settings_x)
        self.draw_text(str(board_height), self.LIGHT_BROWN, add_board_height_btn.centerx,
                       board_start_y + board_height_px // 2, outline_color=self.OUTLINE_COLOR)
        rm_board_height_btn = self.draw_button('-',
                                               board_start_y + board_height_px // 2 + self.font.get_height() * 1.5,
                                               width=self.small_button_width, x=settings_x)

        for row in range(board_height):
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
                         (piece_selector_x, board_start_y, piece_selector_width, board_height_px))
        self.draw_section_text('Available Pieces', self.LIGHT_BROWN,
                               piece_selector_x + piece_selector_width // 2, board_start_y - 40)

        pieces = ('pK', 'pq', 'pr', 'pb', 'pk', 'pp')
        zombies = ('zw', 'zs', 'ze', 'zi')

        piece_size = int((board_height_px // 6) * 0.8)
        piece_gap = (board_height_px - (6 * piece_size)) // 7
        selector_square_size = piece_size + 10
        list_gap = (piece_selector_width - 2 * selector_square_size) // 3
        highlight_surface = pygame.Surface((selector_square_size, selector_square_size))
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

        left_offset = -int(self.screen_width * 0.35)
        right_offset = int(self.screen_width * 0.3)

        go_back_btn = self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)
        clear_board_btn = self.draw_button('Clear Board', self.bottom_margin)
        next_btn = self.draw_button('Next', self.bottom_margin, x_offset=right_offset, disabled=not has_king)
        return {
            'board_start': (board_start_x, board_start_y),
            'square_size': square_size,
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

    def save_custom_menu(self, game_mode, difficulty, can_change_gm, can_change_difficulty, name, is_focused, name_ok):
        self.screen.blit(self.background, (0, 0))
        self.draw_main_text('Settings', self.LIGHT_BROWN, self.OUTLINE_COLOR)

        first_section_y = self.content_start_y
        second_section_y = first_section_y + self.section_spacing
        third_section_y = second_section_y + self.section_spacing
        fourth_section_y = third_section_y + int(1.25 * self.section_spacing)
        fifth_section_y = fourth_section_y + self.section_spacing

        change_game_mode_btn, disable_game_mode_btn = self.draw_section_row(
            'Base Game Mode', game_mode, first_section_y,
            [('>', None, can_change_gm), ('X', None, False)],
            disabled=can_change_gm
        )
        self.draw_separator(first_section_y + self.element_spacing // 2)

        change_difficulty_btn, disable_difficulty_btn = self.draw_section_row(
            'Difficulty', difficulty, second_section_y,
            [('>', None, can_change_difficulty), ('X', None, False)],
            disabled=can_change_difficulty
        )
        self.draw_separator(second_section_y + self.element_spacing // 2)

        self.draw_section_text('Specifying a setting here will disallow any changes to that setting later',
                               self.LIGHT_BROWN, self.screen_width // 2, third_section_y)

        # name
        input_color = self.DARK_BROWN
        if not name:
            name = 'Name'
            input_color = self.GREY
        input_width = self.screen_width * 0.6
        input_height = self.font.get_height() * 1.5
        input_start_x = (self.screen_width - input_width) // 2
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

        left_offset = -int(self.screen_width * 0.35)
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

    def load_custom_menu(self, game_modes, selected, scroll_offset):
        self.screen.blit(self.background, (0, 0))
        self.draw_main_text('Load Custom Mode', self.LIGHT_BROWN, self.OUTLINE_COLOR)

        panel_width = self.screen_width // 2 - 50 * self.scale_factor
        left_panel_x = 50
        right_panel_x = self.screen_width // 2 + 50 * self.scale_factor

        list_start_y = self.content_start_y + self.element_spacing
        panel_height = self.bottom_margin - list_start_y - self.section_spacing
        item_width = self.regular_font_size * 21
        item_height = self.regular_font_size * 1.5
        max_visible_items = int(panel_height // item_height - 1)
        item_spacing = (panel_height - max_visible_items * item_height) // max_visible_items + 1

        sidebar_width = 20 * self.scale_factor
        sidebar_x = left_panel_x + panel_width + 10
        sidebar_y = list_start_y - 30 * self.scale_factor

        self.draw_section_text('Game Modes', self.LIGHT_BROWN, left_panel_x + item_width // 2, self.content_start_y)
        self.draw_section_text('Details', self.LIGHT_BROWN, right_panel_x + panel_width // 2, self.content_start_y)

        total_items = len(game_modes)
        max_scroll = max(0, total_items - max_visible_items)

        if total_items > max_visible_items:
            sidebar_bg_rect = pygame.Rect(sidebar_x, sidebar_y, sidebar_width, panel_height)
            pygame.draw.rect(self.screen, self.LIGHT_BROWN, sidebar_bg_rect, 0, 5)

            scrollbar_height = panel_height * (max_visible_items / total_items)
            scrollbar_y = sidebar_y + (panel_height - scrollbar_height) * (scroll_offset / max_scroll)

            scrollbar_outline = pygame.Rect(sidebar_x - 5, scrollbar_y - 5, sidebar_width + 10, scrollbar_height + 10)
            scrollbar_rect = pygame.Rect(sidebar_x, scrollbar_y, sidebar_width, scrollbar_height)
            pygame.draw.rect(self.screen, self.DARK_BROWN, scrollbar_outline, 0, 5)
            pygame.draw.rect(self.screen, self.YELLOW, scrollbar_rect, 0, 5)

        game_mode_areas = []
        items = list(game_modes.items())
        visible_items = items[scroll_offset:scroll_offset + max_visible_items]

        for i, (gm_id, gm) in enumerate(visible_items):
            item_y = list_start_y + i * (item_height + item_spacing)
            gm_rect = pygame.Rect(left_panel_x, item_y - item_height // 2, item_width, item_height)
            game_mode_areas.append((gm_id, gm_rect))

            if selected and gm_id == selected[0]:
                pygame.draw.rect(self.screen, self.HIGHLIGHT_COLOR, gm_rect, 0, 10)

            pygame.draw.rect(self.screen, self.SEPARATOR_COLOR, gm_rect, 3, 10)
            self.draw_text(gm.name, self.LIGHT_BROWN, left_panel_x + item_width // 2, item_y,
                           outline_color=self.OUTLINE_COLOR)

        if selected:
            selected_gm = selected[1]
            gm_text = f"Game Mode: {selected_gm.base_gm if not selected_gm.can_change_gm else '-'}"
            self.draw_text(gm_text, self.LIGHT_BROWN, right_panel_x + panel_width // 2,
                           self.content_start_y + self.element_spacing,
                           outline_color=self.OUTLINE_COLOR)

            difficulty_text = f"Difficulty: {selected_gm.difficulty if not selected_gm.can_change_difficulty else '-'}"
            self.draw_text(difficulty_text, self.LIGHT_BROWN, right_panel_x + panel_width // 2,
                           self.content_start_y + 2 * self.element_spacing, outline_color=self.OUTLINE_COLOR)

            show_board_btn = self.draw_button('Show Board', self.content_start_y + 3 * self.element_spacing,
                                              x_offset=panel_width // 2 + 50)
        else:
            show_board_btn = None

        left_offset = -int(self.screen_width * 0.35)
        right_offset = int(self.screen_width * 0.3)

        go_back_btn = self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)
        refresh_btn = self.draw_button('Refresh', self.bottom_margin)
        load_btn = self.draw_button('Load', self.bottom_margin, x_offset=right_offset, disabled=not selected)

        return {
            'max_items': max_visible_items,
            'game_modes_areas': game_mode_areas,
            'buttons': {
                'show_board': show_board_btn,
                'back': go_back_btn,
                'refresh': refresh_btn,
                'load': load_btn
            }
        }

    def preview_board(self, board_height, board):
        square_size = self.screen_height // max(8, board_height)
        board_height_px = board_height * square_size
        board_width_px = 8 * square_size
        board_start_y = (self.screen_height - board_height_px) // 2
        board_start_x = (self.screen_width - board_width_px) // 2

        self.draw_board(board_height, 8, board, board_start_x, board_start_y, square_size)

        return pygame.Rect(board_start_x, board_start_y, board_width_px, board_height_px)

    def game_settings_menu(self, game_mode=None, difficulty=None, board_height=None):
        self.screen.blit(self.background, (0, 0))
        self.draw_main_text('Play', self.LIGHT_BROWN, self.OUTLINE_COLOR)

        i = 0
        sections_y = (self.content_start_y, self.content_start_y + self.section_spacing,
                      self.content_start_y + 2 * self.section_spacing)

        game_mode_btn = None
        if game_mode:
            game_mode_btn, = self.draw_section_row(
                'Game Mode', game_mode, sections_y[i],
                [('>', None, False)]
            )
            self.draw_separator(sections_y[i] + self.element_spacing // 2)
            i += 1

        difficulty_btn = None
        if difficulty:
            difficulty_btn, = self.draw_section_row(
                'Difficulty', difficulty, sections_y[i],
                [('>', None, False)]
            )
            self.draw_separator(sections_y[i] + self.element_spacing // 2)
            i += 1

        add_btn = rm_btn = None
        if board_height:
            add_btn, rm_btn = self.draw_section_row(
                'Board Height', str(board_height), sections_y[i],
                [('+', None, False), ('-', None, False)]
            )
            self.draw_separator(sections_y[i] + self.element_spacing // 2)

        left_offset = -int(self.screen_width * 0.35)
        right_offset = int(self.screen_width * 0.3)

        go_back_btn = self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)
        play_btn = self.draw_button('Play', self.bottom_margin, x_offset=right_offset)

        buttons = (game_mode_btn, difficulty_btn, add_btn, rm_btn, play_btn, go_back_btn)
        return buttons

    def playing_screen(self, board_height, board, selected, game_stats, displayed_board_part=-1):
        self.screen.blit(self.background, (0, 0))
        stats_sidebar_width = self.screen_width // 4
        stats_x_padding = stats_sidebar_width // 2 + 30
        stats_y_gap = self.screen_height // (len(game_stats) + 2)

        for i, (stat, val) in enumerate(game_stats.items()):
            self.draw_section_text(f'{stat}: {val}', self.LIGHT_BROWN, stats_x_padding, (i + 1) * stats_y_gap)

        can_split = board_height > 9
        display_whole_board = displayed_board_part == 0
        display_lower_half = displayed_board_part == -1

        base_square_size = self.screen_height // 10
        square_size = base_square_size
        start_row = 0
        end_row = board_height
        board_start_y = (self.screen_height - board_height * square_size) // 2

        if can_split:
            if display_whole_board:
                square_size = (self.screen_height - 2 * base_square_size) // board_height
                board_start_y = base_square_size
            else:
                if display_lower_half:
                    start_row = board_height // 2
                    end_row = board_height
                    board_start_y = 0
                else:
                    start_row = 0
                    end_row = board_height // 2
                    board_start_y = self.screen_height - (board_height // 2) * square_size

        board_start_x = max(stats_sidebar_width + 50, (self.screen_width - square_size * 8) // 2)

        highlight_surface = pygame.Surface((square_size, square_size))
        pygame.draw.rect(highlight_surface, self.HIGHLIGHT_COLOR,
                         (0, 0, square_size, square_size))
        for row in range(start_row, end_row):
            local_row = row - start_row
            for col in range(8):
                square_color = self.BOARD_COLORS[(row + col) % 2]
                square_rect = pygame.Rect(
                    board_start_x + col * square_size,
                    board_start_y + local_row * square_size,
                    square_size,
                    square_size
                )
                pygame.draw.rect(self.screen, square_color, square_rect)
                if (row, col) == selected:
                    self.screen.blit(highlight_surface,
                                     ((col * square_size) + board_start_x,
                                      (local_row * square_size) + board_start_y))

                piece = board[row][col]
                if piece and piece[:2] in self.piece_images:
                    image = pygame.transform.scale(self.piece_images[piece[:2]],
                                                   (square_size - 10, square_size - 10))
                    self.screen.blit(image,
                                     ((col * square_size + 5) + board_start_x,
                                      (local_row * square_size + 5) + board_start_y))

        switch_halves_btn = None
        if can_split and not display_whole_board:
            button_x = board_start_x + (square_size * 8) + 20
            button_y = (self.screen_height - self.small_button_height) // 2
            sign = '^' if display_lower_half else 'v'
            switch_halves_btn = self.draw_button(sign, button_y, button_x, width=self.small_button_width)

        return {
            'board_start': (board_start_x, board_start_y),
            'square_size': square_size,
            'row_offset': start_row,
            'switch_halves_btn': switch_halves_btn
        }

    def pawn_promotion_menu(self):
        self.screen.blit(self.popup_background, (0, 0))

        popup_width = int(self.screen_width * 0.3)
        popup_height = int(self.screen_height * 0.15)
        popup_x = (self.screen_width - popup_width) // 2
        popup_y = (self.screen_height - popup_height) // 2

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

        return piece_areas

    def help_menu(self):
        self.screen.blit(self.background, (0, 0))
        self.draw_main_text('Help', self.LIGHT_BROWN, self.OUTLINE_COLOR)

        first_button_y = self.content_start_y + self.element_spacing
        second_button_y = first_button_y + self.button_height + self.element_spacing
        third_button_y = second_button_y + self.button_height + self.element_spacing
        fourth_button_y = third_button_y + self.button_height + self.element_spacing

        rules_btn = self.draw_button('Rules', first_button_y)
        zombies_btn = self.draw_button('Zombies', second_button_y)
        game_modes_btn = self.draw_button('Game Modes', third_button_y)
        difficulties_btn = self.draw_button('Difficulties', fourth_button_y)

        left_offset = -int(self.screen_width * 0.35)
        go_back_btn = self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)

        return rules_btn, zombies_btn, game_modes_btn, difficulties_btn, go_back_btn

    def help_rules_1_menu(self):
        self.screen.blit(self.background, (0, 0))
        self.draw_main_text('Rules 1/2', self.LIGHT_BROWN, self.OUTLINE_COLOR)

        section_x = self.screen_width // 2

        self.draw_section_text('The Player can make all traditional chess moves', self.LIGHT_BROWN,
                               section_x, self.content_start_y + self.element_spacing)

        board_height = (self.bottom_margin - self.content_start_y) // 2
        square_size = board_height // 4
        board_width = square_size * 8
        board_left_start_x = self.screen_width // 2 - board_width - 50 * self.scale_factor
        board_right_start_x = self.screen_width // 2 + 50 * self.scale_factor
        board_start_y = self.content_start_y + self.element_spacing + self.section_spacing
        board = [
            [None for _ in range(8)],
            [None for _ in range(8)],
            ['pp' for _ in range(8)],
            ['pr', 'pk', 'pb', 'pq', 'pK', 'pb', 'pk', 'pr']
        ]
        self.draw_board(4, 8, board, board_left_start_x, board_start_y, square_size)

        board[1][5] = 'pp'
        board[2][5] = None
        self.draw_board(4, 8, board, board_right_start_x, board_start_y, square_size)

        left_offset = -int(self.screen_width * 0.35)
        right_offset = int(self.screen_width * 0.35)

        go_back_btn = self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)
        next_btn = self.draw_button('Next', self.bottom_margin, x_offset=right_offset)

        return go_back_btn, next_btn

    def help_rules_2_menu(self):
        self.screen.blit(self.background, (0, 0))
        self.draw_main_text('Rules 2/2', self.LIGHT_BROWN, self.OUTLINE_COLOR)

        section_x = self.screen_width // 2

        self.draw_section_text('The game ends when the King gets captured or turned', self.LIGHT_BROWN,
                               section_x, self.content_start_y + self.element_spacing)

        board_height = (self.bottom_margin - self.content_start_y) // 2
        square_size = board_height // 4
        board_width = square_size * 8
        board_left_start_x = self.screen_width // 2 - board_width - 50 * self.scale_factor
        board_right_start_x = self.screen_width // 2 + 50 * self.scale_factor
        board_start_y = self.content_start_y + self.element_spacing + self.section_spacing
        board = [
            [None, None, None, 'zw', None, None, None, None],
            [None, None, None, 'pK', None, None, None, None],
        ]
        self.draw_board(2, 8, board, board_left_start_x, board_start_y, square_size)

        board[1][3] = 'zw'
        board[0][3] = None
        self.draw_board(2, 8, board, board_right_start_x, board_start_y, square_size)

        left_offset = -int(self.screen_width * 0.35)
        go_back_btn = self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)

        return go_back_btn

    def help_zombies_menu(self):
        self.screen.blit(self.background, (0, 0))
        self.draw_main_text('Zombies', self.LIGHT_BROWN, self.OUTLINE_COLOR)

        img_space = self.screen_width // 9
        name_y = self.content_start_y + self.section_spacing
        img_y = name_y + self.button_height + self.element_spacing // 2
        info_y = img_y + img_space + self.element_spacing

        walker_x = img_space
        infected_x = walker_x + 2 * img_space
        stomper_x = infected_x + 2 * img_space
        explosive_x = stomper_x + 2 * img_space

        self.draw_section_text('Each turn new zombies will be created and all remaining moved', self.LIGHT_BROWN,
                               self.screen_width // 2, self.content_start_y)

        walker_btn = self.draw_button('Walker', name_y, x=walker_x, width=img_space)
        self.screen.blit(pygame.transform.scale(self.piece_images['zw'], (img_space, img_space)), (walker_x, img_y))
        self.draw_section_text('50%', self.LIGHT_BROWN, walker_x + img_space // 2, info_y)

        infected_btn = self.draw_button('Infected', name_y, x=infected_x, width=img_space)
        self.screen.blit(pygame.transform.scale(self.piece_images['zi'], (img_space, img_space)), (infected_x, img_y))
        self.draw_section_text('30%', self.LIGHT_BROWN, infected_x + img_space // 2, info_y)

        stomper_btn = self.draw_button('Stomper', name_y, x=stomper_x, width=img_space)
        self.screen.blit(pygame.transform.scale(self.piece_images['zs'], (img_space, img_space)), (stomper_x, img_y))
        self.draw_section_text('10%', self.LIGHT_BROWN, stomper_x + img_space // 2, info_y)

        explosive_btn = self.draw_button('Explosive', name_y, x=explosive_x, width=img_space)
        self.screen.blit(pygame.transform.scale(self.piece_images['ze'], (img_space, img_space)), (explosive_x, img_y))
        self.draw_section_text('10%', self.LIGHT_BROWN, explosive_x + img_space // 2, info_y)

        left_offset = -int(self.screen_width * 0.35)
        go_back_btn = self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)

        return walker_btn, infected_btn, stomper_btn, explosive_btn, go_back_btn

    def zombie_info_popup(self, zombie, movement, order, *behaviour):
        panel_width = self.screen_width // 2
        panel_rect = pygame.draw.rect(self.screen, self.BROWN,
                                      (self.screen_width // 4, 0, panel_width, self.screen_height))
        panel_rect = pygame.draw.rect(self.screen, self.OUTLINE_COLOR,
                                      (self.screen_width // 4, 0, panel_width, self.screen_height), 20)

        img_side = self.screen_height // 4

        desc_spacing = self.section_font_size * 1.5
        info_x = self.screen_width // 2
        mvm_y = self.title_y + img_side + self.element_spacing
        order_y = mvm_y + self.section_spacing + desc_spacing
        bhvr_y = order_y + self.section_spacing + desc_spacing

        self.screen.blit(pygame.transform.scale(self.piece_images[zombie], (img_side, img_side)),
                         ((self.screen_width - img_side) // 2, self.title_y))

        self.draw_section_text('Movement', self.LIGHT_BROWN, info_x, mvm_y)
        self.draw_text(movement, self.LIGHT_BROWN, info_x, mvm_y + desc_spacing,
                       outline_color=self.OUTLINE_COLOR)

        self.draw_section_text('Order of Movement', self.LIGHT_BROWN, info_x, order_y)
        self.draw_text(order, self.LIGHT_BROWN, info_x, order_y + desc_spacing,
                       outline_color=self.OUTLINE_COLOR)

        self.draw_section_text('Special Behaviour', self.LIGHT_BROWN, info_x, bhvr_y)
        line_spacing = bhvr_y
        for line in behaviour:
            line_spacing += desc_spacing
            self.draw_text(line, self.LIGHT_BROWN, info_x, line_spacing, outline_color=self.OUTLINE_COLOR)

        return panel_rect

    def help_game_modes_menu(self):
        self.screen.blit(self.background, (0, 0))
        self.draw_main_text('Game Modes', self.LIGHT_BROWN, self.OUTLINE_COLOR)

        desc_spacing = self.section_font_size * 1.5
        start_x = self.screen_width // 2
        survive_y = self.content_start_y
        capture_y = survive_y + self.section_spacing + desc_spacing
        block_y = capture_y + self.section_spacing + desc_spacing
        block_clear_y = block_y + self.section_spacing + desc_spacing

        self.draw_section_text('Survive The Longest', self.LIGHT_BROWN, start_x, survive_y)
        self.draw_text('No win condition. The longer the game, the higher the score', self.LIGHT_BROWN,
                       start_x, survive_y + desc_spacing, outline_color=self.OUTLINE_COLOR)

        self.draw_section_text('Capture The Most', self.LIGHT_BROWN, start_x, capture_y)
        self.draw_text('No win condition. The more you capture, the higher the score', self.LIGHT_BROWN,
                       start_x, capture_y + desc_spacing, outline_color=self.OUTLINE_COLOR)

        self.draw_section_text('Block The Border', self.LIGHT_BROWN, start_x, block_y)
        self.draw_text('Block the upper rank (row) to win', self.LIGHT_BROWN,
                       start_x, block_y + desc_spacing, outline_color=self.OUTLINE_COLOR)

        self.draw_section_text('Block And Clear', self.LIGHT_BROWN, start_x, block_clear_y)
        self.draw_text('Block the upper rank (row) and clear the board from zombies to win', self.LIGHT_BROWN,
                       start_x, block_clear_y + desc_spacing, outline_color=self.OUTLINE_COLOR)

        left_offset = -int(self.screen_width * 0.35)
        go_back_btn = self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)

        return go_back_btn

    def help_difficulties_menu(self):
        self.screen.blit(self.background, (0, 0))
        self.draw_main_text('Difficulties', self.LIGHT_BROWN, self.OUTLINE_COLOR)

        table_y = self.title_y + self.main_font_size
        col_width = self.regular_font_size * 9
        row_height = self.regular_font_size * 3
        table_width = 5 * col_width
        table_x = (self.screen_width - table_width) // 2

        headers = ["Name", "0 Zombies", "1 Zombie", "2 Zombies", "Limit"]

        rows = (
            ("Easy", "50%", "50%", "0%", "No"),
            ("Normal", "30%", "60%", "10%", "No"),
            ("Hard", "20%", "40%", "40%", "No"),
            ("Extreme", "20%", "50%", "30%", "Yes")
        )

        table_height = row_height * 5
        pygame.draw.rect(self.screen, self.OUTLINE_COLOR,
                         (table_x - 5, table_y - 5, table_width + 10, table_height + 10), 0)
        pygame.draw.rect(self.screen, self.LIGHT_BROWN,
                         (table_x, table_y, table_width, table_height), 0)

        current_x = table_x
        for i, header in enumerate(headers):
            cell_rect = pygame.Rect(current_x, table_y, col_width, row_height)
            pygame.draw.rect(self.screen, self.BROWN, cell_rect, 0)
            pygame.draw.rect(self.screen, self.OUTLINE_COLOR, cell_rect, 2)

            self.draw_text(header, self.LIGHT_BROWN,
                           current_x + col_width // 2,
                           table_y + row_height // 2,
                           outline_color=self.OUTLINE_COLOR)
            current_x += col_width

        for row_idx, row_data in enumerate(rows):
            current_y = table_y + (row_idx + 1) * row_height
            current_x = table_x

            for col_idx, cell_data in enumerate(row_data):
                cell_rect = pygame.Rect(current_x, current_y, col_width, row_height)
                pygame.draw.rect(self.screen, self.DARK_BROWN, cell_rect, 0)
                pygame.draw.rect(self.screen, self.OUTLINE_COLOR, cell_rect, 1)

                self.draw_text(cell_data, self.LIGHT_BROWN,
                               current_x + col_width // 2,
                               current_y + row_height // 2,
                               outline_color=self.OUTLINE_COLOR)
                current_x += col_width

        self.draw_section_text('The table describes a chance of creating given number of zombies each turn.',
                               self.LIGHT_BROWN, self.screen_width // 2,
                               table_y + 5 * row_height + self.section_font_size,
                               outline_color=self.OUTLINE_COLOR)
        self.draw_section_text("'Limit' refers to the limitation of moving the same piece twice in a row.",
                               self.LIGHT_BROWN, self.screen_width // 2,
                               table_y + 5 * row_height + 3 * self.section_font_size,
                               outline_color=self.OUTLINE_COLOR)

        left_offset = -int(self.screen_width * 0.35)
        go_back_btn = self.draw_button('Go Back', self.bottom_margin, x_offset=left_offset)

        return go_back_btn
