import os
import random
from enum import Enum

import pygame

from game.menu import Menu


# TODO: improve menu look
# TODO: improve menu (game mode selection, difficulty etc)


class GameModes(Enum):
    SURVIVE_THE_LONGEST = 1
    CAPTURE_THE_MOST = 2
    BLOCK_THE_BORDER = 3
    BLOCK_AND_CLEAR = 4


class TurnResult(Enum):
    OK = 1
    WRONG = 2
    WIN = 3
    CHECKMATE = 4


class Gameplay:
    def __init__(self, board_y, difficulty):
        self.board = [
            [None for _ in range(8)] for _ in range(board_y - 2)
        ]
        self.board.append([f'p{i}' for i in range(8)])
        self.board.append(['r0', 'k0', 'b0', 'q', 'K', 'b1', 'k1', 'r1'])
        self.selected_piece = None
        self.last_moved_piece = None
        self.board_y = board_y
        self.difficulty = difficulty

    def get_piece_at(self, row, col):
        return self.board[row][col]

    def select_piece(self, row, col):
        piece = self.board[row][col]
        if piece and piece != 'z' and piece != self.last_moved_piece:
            self.selected_piece = (row, col)
            return True
        return False

    def unselect_piece(self):
        self.selected_piece = None

    def is_selected(self, row, col):
        return self.selected_piece == (row, col)

    def is_checkmate(self, i, j):
        if self.board[i][j] == 'K':
            return True

    def skip_turn(self):
        self.last_moved_piece = None
        if self.move_wave() == TurnResult.CHECKMATE:
            return TurnResult.CHECKMATE
        return TurnResult.OK

    def is_valid_move(self, start_row, start_col, end_row, end_col):
        if self.board[end_row][end_col] != 'z' and self.board[end_row][end_col] is not None:
            return False

        piece = self.board[start_row][start_col]
        if piece is None or piece == 'z':
            return False
        piece = piece[0]
        if piece == 'p':
            return self.check_pawn_move(start_row, start_col, end_row, end_col)
        elif piece == 'r':
            return self.check_rook_move(start_row, start_col, end_row, end_col)
        elif piece == 'k':
            return self.check_knight_move(start_row, start_col, end_row, end_col)
        elif piece == 'b':
            return self.check_bishop_move(start_row, start_col, end_row, end_col)
        elif piece == 'q':
            return self.check_queen_move(start_row, start_col, end_row, end_col)
        elif piece == 'K':
            return self.check_king_move(start_row, start_col, end_row, end_col)

    def move_piece(self, start_row, start_col, end_row, end_col):
        if self.is_valid_move(start_row, start_col, end_row, end_col):
            self.board[end_row][end_col] = self.board[start_row][start_col]
            self.board[start_row][start_col] = None
            if self.move_wave() == TurnResult.CHECKMATE:
                return TurnResult.CHECKMATE
            self.last_moved_piece = self.board[end_row][end_col]
            return TurnResult.OK
        return TurnResult.WRONG

    def move_wave(self):
        for i in reversed(range(self.board_y)):
            for j in reversed(range(8)):
                if self.board[i][j] != 'z':
                    continue

                move = self.check_zombie_collision(i, j)
                if move is None:
                    continue
                elif move[0] == 'd':
                    if self.is_checkmate(i + 1, j):
                        return TurnResult.CHECKMATE
                    self.board[i + 1][j] = 'z'
                    if move[1] == 'm':
                        self.board[i][j] = None
                elif move[0] == 'r':
                    if self.is_checkmate(i + 1, j):
                        return TurnResult.CHECKMATE
                    self.board[i][j + 1] = 'z'
                    if move[1] == 'm':
                        self.board[i][j] = None
                elif move[0] == 'l':
                    if self.is_checkmate(i + 1, j):
                        return TurnResult.CHECKMATE
                    self.board[i][j - 1] = 'z'
                    if move[1] == 'm':
                        self.board[i][j] = None
        return self.create_new_zombies(random.randint(0, self.difficulty))

    def create_new_zombies(self, n):
        new_spots = random.sample(range(8), n)
        for i in new_spots:
            if self.board[0][i] == 'K':
                return TurnResult.CHECKMATE
            self.board[0][i] = 'z'
        return TurnResult.OK

    def check_zombie_collision(self, i, j):
        # check down
        if i + 1 == self.board_y or self.board[i + 1][j] == 'z':
            # down occupied, go right
            if j + 1 == 8 or self.board[i][j + 1] == 'z':
                # right occupied, go left
                if j - 1 == -1 or self.board[i][j - 1] == 'z':
                    # all sides occupied
                    return None
                else:
                    if self.board[i][j - 1] is None:
                        return 'lm'
                    return 'lc'
            else:
                if self.board[i][j + 1] is None:
                    return 'rm'
                return 'rc'
        else:
            if self.board[i + 1][j] is None:
                return 'dm'
            return 'dc'

    def check_pawn_move(self, start_row, start_col, end_row, end_col):
        if end_row >= start_row:
            return False

        move_direction = -1
        if start_col == end_col:
            if start_row + move_direction == end_row:
                return self.board[end_row][end_col] is None
            elif start_row == len(self.board) - 2 and start_row + (2 * move_direction) == end_row:
                return (self.board[end_row][end_col] is None and
                        self.board[start_row + move_direction][end_col] is None)
            return False

        elif abs(start_col - end_col) == 1 and start_row + move_direction == end_row:
            target_piece = self.board[end_row][end_col]
            return target_piece == 'z'
        return False

    def check_rook_move(self, start_row, start_col, end_row, end_col):
        if start_row != end_row and start_col != end_col:
            return False

        if start_row == end_row:
            step = 1 if end_col > start_col else -1
            for col in range(start_col + step, end_col, step):
                if self.board[start_row][col] is not None:
                    return False
        else:
            step = 1 if end_row > start_row else -1
            for row in range(start_row + step, end_row, step):
                if self.board[row][start_col] is not None:
                    return False
        return True

    @staticmethod
    def check_knight_move(start_row, start_col, end_row, end_col):
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def check_bishop_move(self, start_row, start_col, end_row, end_col):
        if abs(end_row - start_row) != abs(end_col - start_col):
            return False

        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1

        current_row = start_row + row_step
        current_col = start_col + col_step

        while current_row != end_row and current_col != end_col:
            if self.board[current_row][current_col] is not None:
                return False
            current_row += row_step
            current_col += col_step
        return True

    def check_queen_move(self, start_row, start_col, end_row, end_col):
        return (self.check_rook_move(start_row, start_col, end_row, end_col) or
                self.check_bishop_move(start_row, start_col, end_row, end_col))

    @staticmethod
    def check_king_move(start_row, start_col, end_row, end_col):
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        return row_diff <= 1 and col_diff <= 1


class SurviveTheLongest(Gameplay):
    def __init__(self, board_y, difficulty):
        super().__init__(board_y, difficulty)
        self.waves = 0

    def create_new_zombies(self, n):
        new_spots = random.sample(range(8), n)
        for i in new_spots:
            if self.board[0][i] == 'K':
                return TurnResult.CHECKMATE
            self.board[0][i] = 'z'
        self.waves += 1
        return TurnResult.OK

    def endgame_info(self, won):
        return f"Survived waves: {self.waves}"


class CaptureTheMost(Gameplay):
    def __init__(self, board_y, difficulty):
        super().__init__(board_y, difficulty)
        self.captured = 0

    def move_piece(self, start_row, start_col, end_row, end_col):
        if self.is_valid_move(start_row, start_col, end_row, end_col):
            if self.board[end_row][end_col] == 'z':
                self.captured += 1
            self.board[end_row][end_col] = self.board[start_row][start_col]
            self.board[start_row][start_col] = None
            if self.move_wave() == TurnResult.CHECKMATE:
                return TurnResult.CHECKMATE
            self.last_moved_piece = self.board[end_row][end_col]
            return TurnResult.OK
        return TurnResult.WRONG

    def endgame_info(self, won):
        return f"Captured zombies: {self.captured}"


class BlockTheBorder(Gameplay):
    def __init__(self, board_y, difficulty):
        super().__init__(board_y, difficulty)
        self.turns_taken = 0
        self.pieces_left = 16

    def get_free_border_spots(self):
        free_spots = []
        for i in range(8):
            if self.board[0][i] is None:
                free_spots.append(i)
        return free_spots

    def move_piece(self, start_row, start_col, end_row, end_col):
        if self.is_valid_move(start_row, start_col, end_row, end_col):
            self.board[end_row][end_col] = self.board[start_row][start_col]
            self.board[start_row][start_col] = None
            self.turns_taken += 1
            result = self.move_wave()
            if result == TurnResult.CHECKMATE:
                return TurnResult.CHECKMATE
            elif result == TurnResult.WIN:
                return TurnResult.WIN
            self.last_moved_piece = self.board[end_row][end_col]
            return TurnResult.OK
        return TurnResult.WRONG

    def move_wave(self):
        for i in reversed(range(self.board_y)):
            for j in reversed(range(8)):
                if self.board[i][j] != 'z':
                    continue

                move = self.check_zombie_collision(i, j)
                if move is None:
                    continue
                elif move[0] == 'd':
                    if self.is_checkmate(i + 1, j):
                        return TurnResult.CHECKMATE
                    self.board[i + 1][j] = 'z'
                    if move[1] == 'm':
                        self.board[i][j] = None
                    else:
                        self.pieces_left -= 1
                elif move[0] == 'r':
                    if self.is_checkmate(i, j + 1):
                        return TurnResult.CHECKMATE
                    self.board[i][j + 1] = 'z'
                    if move[1] == 'm':
                        self.board[i][j] = None
                    else:
                        self.pieces_left -= 1
                elif move[0] == 'l':
                    if self.is_checkmate(i, j - 1):
                        return TurnResult.CHECKMATE
                    self.board[i][j - 1] = 'z'
                    if move[1] == 'm':
                        self.board[i][j] = None
                    else:
                        self.pieces_left -= 1
        if self.pieces_left < 8:
            return TurnResult.CHECKMATE
        return self.create_new_zombies(random.randint(0, self.difficulty))

    def create_new_zombies(self, n):
        new_spots = self.get_free_border_spots()
        if not new_spots:
            return TurnResult.WIN
        new_spots = random.sample(new_spots, n)
        for i in new_spots:
            self.board[0][i] = 'z'
        return TurnResult.OK

    def endgame_info(self, won):
        if won:
            return f"You blocked the border in {self.turns_taken} turns"
        return "You didn't manage to block the border"


class BlockAndClear(BlockTheBorder):
    def __init__(self, board_y, difficulty):
        super().__init__(board_y, difficulty)

    def is_board_clear(self):
        for i in range(self.board_y):
            for j in range(8):
                if self.board[i][j] == 'z':
                    return False
        return True

    def create_new_zombies(self, n):
        new_spots = self.get_free_border_spots()
        if not new_spots and self.is_board_clear():
            return TurnResult.WIN
        new_spots = random.sample(new_spots, n)
        for i in new_spots:
            self.board[0][i] = 'z'
        return TurnResult.OK

    def endgame_info(self, won):
        if won:
            return f"You cleared the board and blocked the border in {self.turns_taken} turns"
        return "You didn't manage to block the border and clear the board"


class DisplaySettings:
    def __init__(self, board_y):
        self.board_y = board_y
        self.square_size = 100
        self.light_square = (255, 215, 175)
        self.dark_square = (205, 132, 55)
        self.highlight_color = (75, 200, 70, 128)
        self.highlight_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        pygame.draw.rect(self.highlight_surface, self.highlight_color,
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


class Game:
    def __init__(self, board_y, difficulty, game_mode):
        pygame.init()
        self.won = False
        self.display_settings = DisplaySettings(board_y)
        self.gameplay = self.init_game_mode(board_y, difficulty, game_mode)
        self.screen = pygame.display.set_mode((800, board_y * 100))
        self.menu = Menu(self.screen, 800, board_y * 100)
        pygame.display.set_caption('Pawnbies')

        self.MENU = 'menu'
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
        colors = [self.display_settings.light_square, self.display_settings.dark_square]
        for row in range(self.display_settings.board_y):
            for col in range(8):
                color = colors[(row + col) % 2]
                pygame.draw.rect(self.screen, color,
                                 (col * self.display_settings.square_size, row * self.display_settings.square_size,
                                  self.display_settings.square_size, self.display_settings.square_size))
                if self.gameplay.is_selected(row, col):
                    self.screen.blit(self.display_settings.highlight_surface,
                                     (col * self.display_settings.square_size, row * self.display_settings.square_size))

    def draw_pieces(self):
        for row in range(self.display_settings.board_y):
            for col in range(8):
                piece = self.gameplay.get_piece_at(row, col)
                if piece and piece[0] in self.display_settings.piece_images:
                    self.screen.blit(self.display_settings.piece_images[piece[0]],
                                     (col * self.display_settings.square_size + 5,
                                      row * self.display_settings.square_size + 5))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if self.current_state == self.MENU:
                    play_btn, quit_btn = self.menu.main_menu()
                    if play_btn.collidepoint(mouse_pos):
                        self.current_state = self.PLAYING
                    elif quit_btn.collidepoint(mouse_pos):
                        return False

                elif self.current_state == self.GAME_OVER:
                    restart_btn, menu_btn = self.menu.game_over_menu(self.gameplay.endgame_info(self.won))
                    if restart_btn.collidepoint(mouse_pos):
                        self.init_game_mode(self.gameplay.board_y, self.gameplay.difficulty, GameModes.BLOCK_THE_BORDER)
                        self.current_state = self.PLAYING
                    elif menu_btn.collidepoint(mouse_pos):
                        self.current_state = self.MENU

                elif self.current_state == self.PLAYING:
                    if event.button == pygame.BUTTON_RIGHT:
                        self.gameplay.unselect_piece()
                    elif event.button == pygame.BUTTON_MIDDLE:
                        if self.gameplay.skip_turn() == TurnResult.CHECKMATE:
                            self.current_state = self.GAME_OVER
                            self.won = False
                    else:
                        col = event.pos[0] // self.display_settings.square_size
                        row = event.pos[1] // self.display_settings.square_size

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
        return True

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            running = self.handle_events()

            if self.current_state == self.MENU:
                self.menu.main_menu()
            elif self.current_state == self.PLAYING:
                self.draw_board()
                self.draw_pieces()
            elif self.current_state == self.GAME_OVER:
                self.menu.game_over_menu(self.gameplay.endgame_info(self.won))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
