import pygame

import os

from game.menu import Menu
from game.game_modes import *
from game.custom import *


class GameStates(Enum):
    MENU = 0
    HELP_MENU = 1
    CUSTOM_MENU = 2
    CREATE_CUSTOM = 3
    SAVE_CUSTOM = 4
    SAVING_STATUS = 5
    LOAD_CUSTOM = 6
    SETTINGS = 7
    GAME_OVER = 8
    PLAYING = 9


class DisplaySettings:
    def __init__(self, screen_width, screen_height, board_y):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.square_size = min(screen_height // board_y, screen_width // 8)
        self.board_y = board_y
        self.center_offset_x = ((8 * self.square_size) // 2) - (self.screen_width // 2)

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
                original_image = pygame.image.load(os.path.join('img/chess_pieces', filename))
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
        self.center_offset_x = ((8 * self.square_size) // 2) - (self.screen_width // 2)
        self.load_piece_images()
        self.highlight_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        pygame.draw.rect(self.highlight_surface, self.HIGHLIGHT_COLOR,
                         (0, 0, self.square_size, self.square_size))


class Game:
    def __init__(self, board_y, difficulty, game_mode):
        pygame.init()
        self.won = False
        self.gameplay = self.init_game_mode(board_y, difficulty, game_mode)
        self.custom = CustomGameMode()

        info_object = pygame.display.Info()
        screen_width = info_object.current_w
        screen_height = info_object.current_h
        self.screen = pygame.display.set_mode((screen_width, screen_height - 50), pygame.FULLSCREEN)
        self.fullscreen = True

        self.display_settings = DisplaySettings(screen_width, screen_height - 50, board_y)
        self.menu = Menu(self.screen, screen_width, screen_height, self.display_settings.piece_images)
        self._help_section = None

        pygame.display.set_caption('Pawnbies')
        self.current_state = GameStates.MENU

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
        colors = (self.display_settings.LIGHT_COLOR, self.display_settings.DARK_COLOR)
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
                                     ((
                                              col * self.display_settings.square_size + 5) - self.display_settings.center_offset_x,
                                      row * self.display_settings.square_size + 5))

    def handle_menu_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            play_btn, custom_btn, help_btn, quit_btn = self.menu.main_menu()
            if play_btn.collidepoint(mouse_pos):
                self.current_state = GameStates.SETTINGS
            elif custom_btn.collidepoint(mouse_pos):
                self.current_state = GameStates.CUSTOM_MENU
            elif help_btn.collidepoint(mouse_pos):
                self.current_state = GameStates.HELP_MENU
            elif quit_btn.collidepoint(mouse_pos):
                return False
        return True

    def handle_custom_menu_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            create_btn, load_btn, back_btn = self.menu.custom_menu()
            if create_btn.collidepoint(mouse_pos):
                self.current_state = GameStates.CREATE_CUSTOM
            elif load_btn.collidepoint(mouse_pos):
                self.current_state = GameStates.LOAD_CUSTOM
            elif back_btn.collidepoint(mouse_pos):
                self.current_state = GameStates.MENU

    def handle_create_custom_state(self, event):
        custom_info = self.menu.create_custom_menu(self.custom.board_y, self.custom.board, self.custom.selected_piece,
                                                   self.custom.has_king)
        square_size = custom_info['square_size']
        board_x, board_y = custom_info['board_start']

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            buttons = custom_info['buttons']
            board_rect = custom_info['board_area']

            if event.button == pygame.BUTTON_LEFT:
                if buttons['back'].collidepoint(mouse_pos):
                    self.current_state = GameStates.CUSTOM_MENU
                    self.custom.unselect_piece()
                    return
                elif buttons['next'].collidepoint(mouse_pos):
                    if self.custom.has_king:
                        self.current_state = GameStates.SAVE_CUSTOM
                    self.custom.unselect_piece()
                    return
                elif buttons['clear'].collidepoint(mouse_pos):
                    self.custom.clear_board()
                    self.custom.has_king = False
                    return
                elif buttons['add_board_height'].collidepoint(mouse_pos):
                    self.custom.add_board_height()
                elif buttons['rm_board_height'].collidepoint(mouse_pos):
                    self.custom.rm_board_height()

                for piece, rect in custom_info['pieces']:
                    if rect.collidepoint(mouse_pos):
                        self.custom.select_piece(piece)
                        return

                if board_rect.collidepoint(mouse_pos):
                    col = int((mouse_pos[0] - board_x) // square_size)
                    row = int((mouse_pos[1] - board_y) // square_size)
                    if 0 <= row < self.custom.board_y and 0 <= col < 8:
                        self.custom.put_selected_piece(row, col)
                        self.custom.check_for_king()

            elif event.button == pygame.BUTTON_RIGHT:
                if board_rect.collidepoint(mouse_pos):
                    col = int((mouse_pos[0] - board_x) // square_size)
                    row = int((mouse_pos[1] - board_y) // square_size)
                    if 0 <= row < self.custom.board_y and 0 <= col < 8:
                        self.custom.rm_piece(row, col)
                        self.custom.check_for_king()

    def handle_save_custom_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            custom_info = self.menu.save_custom_menu(self.custom.base_game_mode, self.custom.difficulty,
                                                     self.custom.game_mode_disabled, self.custom.difficulty_disabled,
                                                     self.custom.name, self.custom.is_focused, self.custom.is_name_ok)
            buttons = custom_info['buttons']
            input_area = custom_info['input_area']

            if buttons['back'].collidepoint(mouse_pos):
                self.current_state = GameStates.CREATE_CUSTOM
            elif buttons['change_gm'].collidepoint(mouse_pos):
                if not self.custom.game_mode_disabled:
                    self.custom.base_game_mode = self.custom.base_game_mode.switch()
            elif buttons['disable_gm'].collidepoint(mouse_pos):
                self.custom.game_mode_disabled = False if self.custom.game_mode_disabled else True
            elif buttons['change_difficulty'].collidepoint(mouse_pos):
                if not self.custom.difficulty_disabled:
                    self.custom.difficulty = self.custom.difficulty.switch()
            elif buttons['disable_difficulty'].collidepoint(mouse_pos):
                self.custom.difficulty_disabled = False if self.custom.difficulty_disabled else True
            elif buttons['save'].collidepoint(mouse_pos):
                if self.custom.is_name_ok:
                    self.custom.save()
                    self.current_state = GameStates.SAVING_STATUS

            if input_area.collidepoint(mouse_pos):
                self.custom.is_focused = True
            else:
                self.custom.is_focused = False

        elif event.type == pygame.KEYDOWN:
            if self.custom.is_focused:
                if event.key == pygame.K_BACKSPACE:
                    self.custom.name = self.custom.name[:-1]
                    self.custom.check_name()
                else:
                    if len(self.custom.name) < 20:
                        self.custom.name += event.unicode
                    self.custom.check_name()

    def handle_saving_status_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()

            main_text = 'Success'
            additional_info = 'Game Mode saved successfully'
            if self.custom.error_msg:
                main_text = 'Saving Failed'
                additional_info = self.custom.error_msg
            restart_btn, menu_btn = self.menu.information_menu(main_text, 'Go Back', 'Main Menu',
                                                               additional_info=additional_info)
            if restart_btn.collidepoint(mouse_pos):
                self.custom.unselect_piece()
                self.current_state = GameStates.CREATE_CUSTOM
            elif menu_btn.collidepoint(mouse_pos):
                self.custom.reset()
                self.current_state = GameStates.MENU

    def handle_load_custom_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            back_btn = self.menu.load_custom_menu()
            if back_btn.collidepoint(mouse_pos):
                self.current_state = GameStates.CUSTOM_MENU

    def handle_help_menu_state(self, event):
        if self._help_section is None:
            self._help_section = self.menu.help_menu()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            back_btn = self._help_section[1]
            if back_btn.collidepoint(mouse_pos):
                self.current_state = GameStates.MENU
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
                self.current_state = GameStates.PLAYING
            elif back_btn.collidepoint(mouse_pos):
                self.current_state = GameStates.MENU

    def handle_game_over_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            restart_btn, menu_btn = self.menu.information_menu('Game Over', 'Try Again', 'Main Menu',
                                                               additional_info=self.gameplay.endgame_info(self.won))
            if restart_btn.collidepoint(mouse_pos):
                self.current_state = GameStates.SETTINGS
            elif menu_btn.collidepoint(mouse_pos):
                self.current_state = GameStates.MENU

    def handle_playing_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_RIGHT:
                self.gameplay.unselect_piece()
            elif event.button == pygame.BUTTON_MIDDLE:
                if self.gameplay.skip_turn() == TurnResult.CHECKMATE:
                    self.current_state = GameStates.GAME_OVER
                    self.won = False
            else:
                col = (event.pos[0] + self.display_settings.center_offset_x) // self.display_settings.square_size
                row = event.pos[1] // self.display_settings.square_size
                if col < 0 or row < 0 or col >= 8 or row >= self.display_settings.board_y:
                    return

                if self.gameplay.selected_piece:
                    start_row, start_col = self.gameplay.selected_piece
                    turn_result = self.gameplay.move_piece(start_row, start_col, row, col)
                    if turn_result == TurnResult.CHECKMATE:
                        self.current_state = GameStates.GAME_OVER
                        self.won = False
                    elif turn_result == TurnResult.WIN:
                        self.current_state = GameStates.GAME_OVER
                        self.won = True
                    elif turn_result == TurnResult.OK:
                        if row == 0 and self.gameplay.get_piece_at(row, col)[0] == 'p':
                            new_piece = self.menu.pawn_promotion_menu()
                            self.gameplay.promote_pawn(row, col, new_piece)
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
                    self.current_state = GameStates.MENU
                if event.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode(
                            (self.display_settings.screen_width, self.display_settings.screen_height),
                            pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode(
                            (self.display_settings.screen_width, self.display_settings.screen_height),
                            pygame.SHOWN)

            if self.current_state == GameStates.MENU:
                if not self.handle_menu_state(event):
                    return False
            elif self.current_state == GameStates.CUSTOM_MENU:
                self.handle_custom_menu_state(event)
            elif self.current_state == GameStates.CREATE_CUSTOM:
                self.handle_create_custom_state(event)
            elif self.current_state == GameStates.SAVE_CUSTOM:
                self.handle_save_custom_state(event)
            elif self.current_state == GameStates.SAVING_STATUS:
                self.handle_saving_status_state(event)
            elif self.current_state == GameStates.LOAD_CUSTOM:
                self.handle_load_custom_state(event)
            elif self.current_state == GameStates.HELP_MENU:
                self.handle_help_menu_state(event)
            elif self.current_state == GameStates.SETTINGS:
                self.handle_settings_state(event)
            elif self.current_state == GameStates.GAME_OVER:
                self.handle_game_over_state(event)
            elif self.current_state == GameStates.PLAYING:
                self.handle_playing_state(event)
        return True

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            running = self.handle_events()

            if self.current_state == GameStates.MENU:
                self.menu.main_menu()
            elif self.current_state == GameStates.CUSTOM_MENU:
                self.menu.custom_menu()
            elif self.current_state == GameStates.CREATE_CUSTOM:
                self.menu.create_custom_menu(self.custom.board_y, self.custom.board, self.custom.selected_piece,
                                             self.custom.has_king)
            elif self.current_state == GameStates.SAVE_CUSTOM:
                self.menu.save_custom_menu(self.custom.base_game_mode, self.custom.difficulty,
                                           self.custom.game_mode_disabled, self.custom.difficulty_disabled,
                                           self.custom.name, self.custom.is_focused, self.custom.is_name_ok)
            elif self.current_state == GameStates.SAVING_STATUS:
                main_text = 'Success'
                additional_info = 'Game Mode saved successfully'
                if self.custom.error_msg:
                    main_text = 'Saving Failed'
                    additional_info = self.custom.error_msg
                self.menu.information_menu(main_text, 'Go Back', 'Main Menu', additional_info=additional_info)
            elif self.current_state == GameStates.LOAD_CUSTOM:
                self.menu.load_custom_menu()
            elif self.current_state == GameStates.HELP_MENU:
                if self._help_section:
                    help_section = self._help_section[0]
                    self.menu.update_help_menu(help_section)
            elif self.current_state == GameStates.SETTINGS:
                self.menu.game_settings_menu(self.gameplay.game_mode, self.gameplay.difficulty, self.gameplay.board_y)
            elif self.current_state == GameStates.PLAYING:
                self.draw_board()
                self.draw_pieces()
            elif self.current_state == GameStates.GAME_OVER:
                self.menu.information_menu('Game Over', 'Try Again', 'Main Menu',
                                           additional_info=self.gameplay.endgame_info(self.won))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
