import pygame

from game.display import Display
from game.game_modes import *
from game.custom import *


class GameState(Enum):
    MENU = 0
    CUSTOM_MENU = 1
    CREATE_CUSTOM = 2
    SAVE_CUSTOM = 3
    SAVING_STATUS = 4
    LOAD_CUSTOM = 5
    SETTINGS = 6
    GAME_OVER = 7
    PLAYING = 8
    PAWN_PROMOTION = 9
    HELP_MENU = 10
    ENDGAME_BOARD = 11


class Game:
    def __init__(self):
        pygame.init()
        self.won = False
        self.gameplay = self.init_game_mode(8, Difficulty.EASY, GameMode.BLOCK_THE_BORDER)
        self.custom = CustomGameMode()

        self._displayed_board_part = 0
        self._promotion_col = 0

        info_object = pygame.display.Info()
        screen_width = info_object.current_w
        screen_height = info_object.current_h
        screen_border_height = 50
        self.fullscreen = True
        bordered_screen_height = screen_height - screen_border_height
        self.screen = pygame.display.set_mode((screen_width, screen_height if self.fullscreen else bordered_screen_height),
                                              pygame.FULLSCREEN if self.fullscreen else pygame.SHOWN)
        self.display = Display(self.screen, screen_width, screen_height, screen_border_height)
        self._help_section = None

        pygame.display.set_caption('Pawnbies')
        self.current_state = GameState.MENU

    @staticmethod
    def init_game_mode(board_height, difficulty, game_mode):
        if game_mode == GameMode.SURVIVE_THE_LONGEST:
            return SurviveTheLongest(board_height, difficulty)
        elif game_mode == GameMode.CAPTURE_THE_MOST:
            return CaptureTheMost(board_height, difficulty)
        elif game_mode == GameMode.BLOCK_THE_BORDER:
            return BlockTheBorder(board_height, difficulty)
        elif game_mode == GameMode.BLOCK_AND_CLEAR:
            return BlockAndClear(board_height, difficulty)

    def handle_menu_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            play_btn, custom_btn, help_btn, quit_btn = self.display.main_menu()
            if play_btn.collidepoint(mouse_pos):
                self.current_state = GameState.SETTINGS
            elif custom_btn.collidepoint(mouse_pos):
                self.current_state = GameState.CUSTOM_MENU
            elif help_btn.collidepoint(mouse_pos):
                self.current_state = GameState.HELP_MENU
            elif quit_btn.collidepoint(mouse_pos):
                return False
        return True

    def handle_custom_menu_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            create_btn, load_btn, back_btn = self.display.custom_menu()
            if create_btn.collidepoint(mouse_pos):
                self.current_state = GameState.CREATE_CUSTOM
            elif load_btn.collidepoint(mouse_pos):
                self.current_state = GameState.LOAD_CUSTOM
            elif back_btn.collidepoint(mouse_pos):
                self.current_state = GameState.MENU

    def handle_create_custom_state(self, event):
        custom_info = self.display.create_custom_menu(self.custom.board_height, self.custom.board,
                                                      self.custom.selected_piece,
                                                      self.custom.has_king)
        board_x, board_y = custom_info['board_start']

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            buttons = custom_info['buttons']
            square_size = custom_info['square_size']
            col = int((mouse_pos[0] - board_x) // square_size)
            row = int((mouse_pos[1] - board_y) // square_size)

            if event.button == pygame.BUTTON_LEFT:
                if buttons['back'].collidepoint(mouse_pos):
                    self.current_state = GameState.CUSTOM_MENU
                    self.custom.unselect_piece()
                    return
                elif buttons['next'].collidepoint(mouse_pos):
                    if self.custom.has_king:
                        self.current_state = GameState.SAVE_CUSTOM
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

                for i in range(2):
                    for piece, rect in custom_info['pieces'][i]:
                        if rect.collidepoint(mouse_pos):
                            self.custom.select_piece(piece)
                            return

                if 0 <= row < self.custom.board_height and 0 <= col < 8:
                    self.custom.put_selected_piece(row, col)
                    self.custom.check_for_king()

            elif event.button == pygame.BUTTON_RIGHT:
                if 0 <= row < self.custom.board_height and 0 <= col < 8:
                    self.custom.rm_piece(row, col)
                    self.custom.check_for_king()

    def handle_save_custom_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            custom_info = self.display.save_custom_menu(self.custom.base_game_mode, self.custom.difficulty,
                                                        self.custom.game_mode_disabled, self.custom.difficulty_disabled,
                                                        self.custom.name, self.custom.is_focused,
                                                        self.custom.is_name_ok)
            buttons = custom_info['buttons']
            input_area = custom_info['input_area']

            if buttons['back'].collidepoint(mouse_pos):
                self.current_state = GameState.CREATE_CUSTOM
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
                    self.current_state = GameState.SAVING_STATUS

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
            restart_btn, menu_btn = self.display.information_menu(main_text, 'Go Back', 'Main Menu',
                                                                  additional_info=additional_info)
            if restart_btn.collidepoint(mouse_pos):
                self.custom.unselect_piece()
                self.current_state = GameState.CREATE_CUSTOM
            elif menu_btn.collidepoint(mouse_pos):
                self.custom.reset()
                self.current_state = GameState.MENU

    def handle_load_custom_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            back_btn = self.display.load_custom_menu()
            if back_btn.collidepoint(mouse_pos):
                self.current_state = GameState.CUSTOM_MENU

    def handle_settings_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            buttons = self.display.game_settings_menu(
                self.gameplay.game_mode,
                self.gameplay.difficulty,
                self.gameplay.board_height
            )
            game_mode_btn = buttons[0]
            difficulty_btn = buttons[1]
            add_board_height_btn = buttons[2]
            rm_board_height_btn = buttons[3]
            play_btn = buttons[4]
            back_btn = buttons[5]

            if game_mode_btn.collidepoint(mouse_pos):
                self.gameplay.game_mode = self.gameplay.game_mode.switch()
            elif difficulty_btn.collidepoint(mouse_pos):
                self.gameplay.difficulty = self.gameplay.difficulty.switch()
            elif add_board_height_btn.collidepoint(mouse_pos):
                self.gameplay.board_height = min(self.gameplay.board_height + 1, 18)
            elif rm_board_height_btn.collidepoint(mouse_pos):
                self.gameplay.board_height = max(self.gameplay.board_height - 1, 6)
            elif play_btn.collidepoint(mouse_pos):
                self.gameplay = self.init_game_mode(self.gameplay.board_height,
                                                    self.gameplay.difficulty,
                                                    self.gameplay.game_mode)
                self.current_state = GameState.PLAYING
            elif back_btn.collidepoint(mouse_pos):
                self.current_state = GameState.MENU

    def handle_game_over_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            main_text = 'You Win' if self.won else 'Game Over'
            show_btn, restart_btn = self.display.information_menu(main_text, 'Show Board', 'Play Again',
                                                                  additional_info=self.gameplay.endgame_info(self.won))
            if show_btn.collidepoint(mouse_pos):
                self.current_state = GameState.ENDGAME_BOARD
            elif restart_btn.collidepoint(mouse_pos):
                self.current_state = GameState.SETTINGS

    def handle_playing_state(self, event):
        game_stats = {
            'Turn': self.gameplay.turns,
            'Moves': self.gameplay.moves,
            'Captured Zombies': self.gameplay.zombies_captured,
            'Castling Available': bool(self.gameplay.castling_combinations)
        }
        play_info = self.display.playing_screen(self.gameplay.board_height, self.gameplay.board,
                                                self.gameplay.selected_piece, game_stats, self._displayed_board_part)
        board_x, board_y = play_info['board_start']
        square_size = play_info['square_size']

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_RIGHT:
                self.gameplay.unselect_piece()
            elif event.button == pygame.BUTTON_MIDDLE:
                if self.gameplay.skip_turn() == TurnResult.CHECKMATE:
                    self.current_state = GameState.GAME_OVER
                    self.won = False
            elif event.button == pygame.BUTTON_LEFT:
                switch_btn = play_info['switch_halves_btn']
                if switch_btn and switch_btn.collidepoint(pygame.mouse.get_pos()):
                    self._displayed_board_part = -self._displayed_board_part
                    return

                col = (event.pos[0] - board_x) // square_size
                row = ((event.pos[1] - board_y) // square_size) + play_info['row_offset']
                if col < 0 or row < 0 or col >= 8 or row >= self.gameplay.board_height:
                    return

                if self.gameplay.selected_piece:
                    start_row, start_col = self.gameplay.selected_piece
                    turn_result = self.gameplay.move_piece(start_row, start_col, row, col)
                    if turn_result == TurnResult.CHECKMATE:
                        self.current_state = GameState.GAME_OVER
                        self.won = False
                    elif turn_result == TurnResult.WIN:
                        self.current_state = GameState.GAME_OVER
                        self.won = True
                    elif turn_result == TurnResult.OK:
                        if row == 0 and self.gameplay.is_pawn(row, col):
                            self._promotion_col = col
                            self.display.set_popup_background()
                            self.current_state = GameState.PAWN_PROMOTION
                        self.gameplay.unselect_piece()
                    else:
                        if self.gameplay.get_piece_at(row, col) and (row, col) != (start_row, start_col):
                            self.gameplay.select_piece(row, col)
                        else:
                            self.gameplay.unselect_piece()
                else:
                    self.gameplay.select_piece(row, col)

        elif event.type == pygame.MOUSEWHEEL:
            if event.y < 0:
                self._displayed_board_part = 0
            else:
                if self._displayed_board_part == 0:
                    if pygame.mouse.get_pos()[1] < self.display.screen_height // 2:
                        self._displayed_board_part = 1
                    else:
                        self._displayed_board_part = -1

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self._displayed_board_part = min(1, self._displayed_board_part + 1)
            elif event.key == pygame.K_s:
                self._displayed_board_part = max(-1, self._displayed_board_part - 1)

    def handle_pawn_promotion_state(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            piece_areas = self.display.pawn_promotion_menu()

            for piece, area in piece_areas.items():
                if area.collidepoint(mouse_pos):
                    self.gameplay.promote_pawn(self._promotion_col, piece)
                    self.current_state = GameState.PLAYING

    def handle_help_menu_state(self, event):
        if self._help_section is None:
            self._help_section = self.display.help_menu()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouse_pos = pygame.mouse.get_pos()
            back_btn = self._help_section[1]
            if back_btn.collidepoint(mouse_pos):
                self.current_state = GameState.MENU
                self._help_section = None

        if event.type == pygame.MOUSEWHEEL:
            help_section = self._help_section[0]
            help_section.handle_event(event)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.current_state = GameState.MENU
                if event.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode(
                            (self.display.screen_width, self.display.screen_height),
                            pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode(
                            (self.display.screen_width, self.display.screen_height - self.display.screen_border_height),
                            pygame.SHOWN)
                    self.display.switch_screen_display()

            if self.current_state == GameState.MENU:
                if not self.handle_menu_state(event):
                    return False
            elif self.current_state == GameState.CUSTOM_MENU:
                self.handle_custom_menu_state(event)
            elif self.current_state == GameState.CREATE_CUSTOM:
                self.handle_create_custom_state(event)
            elif self.current_state == GameState.SAVE_CUSTOM:
                self.handle_save_custom_state(event)
            elif self.current_state == GameState.SAVING_STATUS:
                self.handle_saving_status_state(event)
            elif self.current_state == GameState.LOAD_CUSTOM:
                self.handle_load_custom_state(event)
            elif self.current_state == GameState.SETTINGS:
                self.handle_settings_state(event)
            elif self.current_state == GameState.GAME_OVER:
                self.handle_game_over_state(event)
            elif self.current_state == GameState.PLAYING:
                self.handle_playing_state(event)
            elif self.current_state == GameState.PAWN_PROMOTION:
                self.handle_pawn_promotion_state(event)
            elif self.current_state == GameState.HELP_MENU:
                self.handle_help_menu_state(event)
        return True

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            running = self.handle_events()

            if self.current_state == GameState.MENU:
                self.display.main_menu()
            elif self.current_state == GameState.CUSTOM_MENU:
                self.display.custom_menu()
            elif self.current_state == GameState.CREATE_CUSTOM:
                self.display.create_custom_menu(self.custom.board_height, self.custom.board, self.custom.selected_piece,
                                                self.custom.has_king)
            elif self.current_state == GameState.SAVE_CUSTOM:
                self.display.save_custom_menu(self.custom.base_game_mode, self.custom.difficulty,
                                              self.custom.game_mode_disabled, self.custom.difficulty_disabled,
                                              self.custom.name, self.custom.is_focused, self.custom.is_name_ok)
            elif self.current_state == GameState.SAVING_STATUS:
                main_text = 'Success'
                additional_info = 'Game Mode saved successfully'
                if self.custom.error_msg:
                    main_text = 'Saving Failed'
                    additional_info = self.custom.error_msg
                self.display.information_menu(main_text, 'Go Back', 'Main Menu', additional_info=additional_info)
            elif self.current_state == GameState.LOAD_CUSTOM:
                self.display.load_custom_menu()
            elif self.current_state == GameState.HELP_MENU:
                if self._help_section:
                    help_section = self._help_section[0]
                    self.display.update_help_menu(help_section)
            elif self.current_state == GameState.SETTINGS:
                self.display.game_settings_menu(self.gameplay.game_mode, self.gameplay.difficulty,
                                                self.gameplay.board_height)
            elif self.current_state == GameState.PLAYING or self.current_state == GameState.ENDGAME_BOARD:
                game_stats = {
                    'Turn': self.gameplay.turns,
                    'Moves': self.gameplay.moves,
                    'Captured Zombies': self.gameplay.zombies_captured,
                    'Castling Available': bool(self.gameplay.castling_combinations)
                }
                self.display.playing_screen(self.gameplay.board_height, self.gameplay.board,
                                            self.gameplay.selected_piece, game_stats, self._displayed_board_part)
            elif self.current_state == GameState.PAWN_PROMOTION:
                self.display.pawn_promotion_menu()
            elif self.current_state == GameState.GAME_OVER:
                main_text = 'You Win' if self.won else 'Game Over'
                self.display.information_menu(main_text, 'Show Board', 'Play Again',
                                              additional_info=self.gameplay.endgame_info(self.won))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
