import os
import pygame

from game.menu import Menu

from game.game_modes import *


class DisplaySettings:
    def __init__(self, screen_width, screen_height, board_y):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.square_size = min(screen_height // board_y, screen_width // 8)
        self.board_x = 8
        self.board_y = board_y
        self.center_offset_x = ((self.board_x * self.square_size) // 2) - (self.screen_width // 2)

        self.BACKGROUND = (220, 168, 128)
        self.LIGHT_COLOR = (255, 215, 175)
        self.DARK_COLOR = (205, 132, 55)
        self.HIGHLIGHT_COLOR = (75, 200, 70, 128)
        self.highlight_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        pygame.draw.rect(self.highlight_surface, self.HIGHLIGHT_COLOR,
                         (0, 0, self.square_size, self.square_size))
        self.piece_images = {}
        self.load_piece_images()

    def load_piece_images(self):
        pieces = {'pawn', 'rook', 'knight', 'bishop', 'queen', 'King', 'zombie'}
        for piece in pieces:
            filename = piece + '.png'
            try:
                original_image = pygame.image.load(os.path.join('chess_pieces', filename))
                scaled_image = pygame.transform.scale(original_image, (self.square_size - 10, self.square_size - 10))
                self.piece_images[piece[0]] = scaled_image
            except Exception as e:
                print(f'Could not load image {filename}: {e}')

    def reset(self, screen_width=None, screen_height=None, board_y=None):
        if screen_width is None:
            screen_width = self.screen_width
        else:
            self.screen_width = screen_width
        if screen_height is None:
            screen_height = self.screen_height
        else:
            self.screen_height = screen_height
        if board_y is None:
            board_y = self.board_y
        else:
            self.board_y = board_y
        self.square_size = min(screen_height // board_y, screen_width // 8)
        self.center_offset_x = ((self.board_x * self.square_size) // 2) - (self.screen_width // 2)
        self.load_piece_images()


class Game:
    def __init__(self, board_y, difficulty, game_mode):
        pygame.init()
        self.won = False
        self.gameplay = self.init_game_mode(board_y, difficulty, game_mode)

        info_object = pygame.display.Info()
        screen_width = info_object.current_w
        screen_height = info_object.current_h - 50
        self.display_settings = DisplaySettings(screen_width, screen_height, board_y)
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.menu = Menu(self.screen, screen_width, screen_height)
        self._help_section = None
        pygame.display.set_caption('Pawnbies')

        self.MENU = 'menu'
        self.HELP_MENU = 'help_menu'
        self.SETTINGS = 'settings'
        self.PLAYING = 'playing'
        self.GAME_OVER = 'game_over'
        self.current_state = self.MENU

    @staticmethod
    def init_game_mode(board_y, difficulty, game_mode):
        if game_mode == GameModes.SURVIVE_THE_LONGEST:
            return SurviveTheLongest(board_y, difficulty)
        elif game_mode == GameModes.CAPTURE_THE_MOST:
            return CaptureTheMost(board_y, difficulty)
        elif game_mode == GameModes.BLOCK_THE_BORDER:
            return BlockTheBorder(board_y, difficulty)
        elif game_mode == GameModes.BLOCK_AND_CLEAR:
            return BlockAndClear(board_y, difficulty)

    def draw_board(self):
        self.screen.fill(self.display_settings.BACKGROUND)
        colors = [self.display_settings.LIGHT_COLOR, self.display_settings.DARK_COLOR]
        for row in range(self.gameplay.board_y):
            for col in range(8):
                color = colors[(row + col) % 2]
                pygame.draw.rect(self.screen, color,
                                 ((col * self.display_settings.square_size) - self.display_settings.center_offset_x,
                                  row * self.display_settings.square_size,
                                  self.display_settings.square_size, self.display_settings.square_size))
                if self.gameplay.is_selected(row, col):
                    self.screen.blit(self.display_settings.highlight_surface,
                                     ((col * self.display_settings.square_size) - self.display_settings.center_offset_x,
                                      row * self.display_settings.square_size))

    def draw_pieces(self):
        for row in range(self.gameplay.board_y):
            for col in range(8):
                piece = self.gameplay.get_piece_at(row, col)
                if piece and piece[0] in self.display_settings.piece_images:
                    self.screen.blit(self.display_settings.piece_images[piece[0]],
                                     ((col * self.display_settings.square_size + 5) - self.display_settings.center_offset_x,
                                      row * self.display_settings.square_size + 5))

    def handle_menu_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            play_btn, help_btn, quit_btn = self.menu.main_menu()
            if play_btn.collidepoint(mouse_pos):
                self.current_state = self.SETTINGS
            elif help_btn.collidepoint(mouse_pos):
                self.current_state = self.HELP_MENU
            elif quit_btn.collidepoint(mouse_pos):
                return False
        return True

    def handle_help_menu_state(self, event):
        if self._help_section is None:
            self._help_section = self.menu.help_menu()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            back_btn = self._help_section[1]
            if back_btn.collidepoint(mouse_pos):
                self.current_state = self.MENU
                self._help_section = None

        if event.type == pygame.MOUSEWHEEL:
            help_section = self._help_section[0]
            help_section.handle_event(event)

    def handle_settings_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            buttons = self.menu.game_settings_menu(
                self.gameplay.game_mode,
                self.gameplay.difficulty,
                self.gameplay.board_y
            )
            game_mode_btn = buttons[0]
            difficulty_btn = buttons[1]
            add_board_y_btn = buttons[2]
            rm_board_y_btn = buttons[3]
            play_btn = buttons[4]
            back_btn = buttons[5]

            if game_mode_btn.collidepoint(mouse_pos):
                self.gameplay.game_mode = self.gameplay.game_mode.switch()
            elif difficulty_btn.collidepoint(mouse_pos):
                self.gameplay.difficulty = self.gameplay.difficulty.switch()
            elif add_board_y_btn.collidepoint(mouse_pos):
                self.gameplay.board_y = min(self.gameplay.board_y + 1, 14)
                self.display_settings.reset(board_y=self.gameplay.board_y)
            elif rm_board_y_btn.collidepoint(mouse_pos):
                self.gameplay.board_y = max(self.gameplay.board_y - 1, 6)
                self.display_settings.reset(board_y=self.gameplay.board_y)
            elif play_btn.collidepoint(mouse_pos):
                self.gameplay = self.init_game_mode(self.gameplay.board_y,
                                                    self.gameplay.difficulty,
                                                    self.gameplay.game_mode)
                self.current_state = self.PLAYING
            elif back_btn.collidepoint(mouse_pos):
                self.current_state = self.MENU

    def handle_game_over_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            restart_btn, menu_btn = self.menu.game_over_menu(self.gameplay.endgame_info(self.won))
            if restart_btn.collidepoint(mouse_pos):
                self.current_state = self.SETTINGS
            elif menu_btn.collidepoint(mouse_pos):
                self.current_state = self.MENU

    def handle_playing_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_RIGHT:
                self.gameplay.unselect_piece()
            elif event.button == pygame.BUTTON_MIDDLE:
                if self.gameplay.skip_turn() == TurnResult.CHECKMATE:
                    self.current_state = self.GAME_OVER
                    self.won = False
            else:
                col = (event.pos[0] + self.display_settings.center_offset_x) // self.display_settings.square_size
                row = event.pos[1] // self.display_settings.square_size
                if col < 0 or row < 0 or col >= self.display_settings.board_x or row >= self.display_settings.board_y:
                    return

                if self.gameplay.selected_piece:
                    start_row, start_col = self.gameplay.selected_piece
                    turn_result = self.gameplay.move_piece(start_row, start_col, row, col)
                    if turn_result == TurnResult.CHECKMATE:
                        self.current_state = self.GAME_OVER
                        self.won = False
                    elif turn_result == TurnResult.WIN:
                        self.current_state = self.GAME_OVER
                        self.won = True
                    elif turn_result == TurnResult.OK:
                        self.gameplay.unselect_piece()
                    else:
                        if self.gameplay.get_piece_at(row, col) and (row, col) != (start_row, start_col):
                            self.gameplay.select_piece(row, col)
                        else:
                            self.gameplay.unselect_piece()
                else:
                    self.gameplay.select_piece(row, col)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.current_state = self.MENU

            if self.current_state == self.MENU:
                if not self.handle_menu_state(event):
                    return False
            elif self.current_state == self.HELP_MENU:
                self.handle_help_menu_state(event)
            elif self.current_state == self.SETTINGS:
                self.handle_settings_state(event)
            elif self.current_state == self.GAME_OVER:
                self.handle_game_over_state(event)
            elif self.current_state == self.PLAYING:
                self.handle_playing_state(event)
        return True

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            running = self.handle_events()

            if self.current_state == self.MENU:
                self.menu.main_menu()
            elif self.current_state == self.HELP_MENU:
                if self._help_section is not None:
                    help_section = self._help_section[0]
                    help_section.draw()
            elif self.current_state == self.SETTINGS:
                self.menu.game_settings_menu(self.gameplay.game_mode, self.gameplay.difficulty, self.gameplay.board_y)
            elif self.current_state == self.PLAYING:
                self.draw_board()
                self.draw_pieces()
            elif self.current_state == self.GAME_OVER:
                self.menu.game_over_menu(self.gameplay.endgame_info(self.won))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
