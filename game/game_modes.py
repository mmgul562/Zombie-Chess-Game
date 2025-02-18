import random
from enum import Enum


class GameModes(Enum):
    SURVIVE_THE_LONGEST = 1
    CAPTURE_THE_MOST = 2
    BLOCK_THE_BORDER = 3
    BLOCK_AND_CLEAR = 4

    def __str__(self):
        if self.name == 'SURVIVE_THE_LONGEST':
            return 'Survive The Longest'
        elif self.name == 'CAPTURE_THE_MOST':
            return 'Capture The Most'
        elif self.name == 'BLOCK_THE_BORDER':
            return 'Block The Border'
        elif self.name == 'BLOCK_AND_CLEAR':
            return 'Block And Clear'

    def switch(self):
        game_modes = list(GameModes)
        current_index = game_modes.index(self)
        next_index = (current_index + 1) % len(game_modes)
        return game_modes[next_index]


class Difficulties(Enum):
    EASY = 1
    NORMAL = 1.5
    HARD = 2
    EXTREME = 3

    def __str__(self):
        return self.name.capitalize()

    def switch(self):
        difficulties = list(Difficulties)
        current_index = difficulties.index(self)
        next_index = (current_index + 1) % len(difficulties)
        return difficulties[next_index]


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
        self.can_do_castling = True
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
        if self.board[i][j] and self.board[i][j][0] == 'K':
            return True

    def skip_turn(self):
        self.last_moved_piece = None
        if self.move_wave() == TurnResult.CHECKMATE:
            return TurnResult.CHECKMATE
        return TurnResult.OK

    def promote_pawn(self, row, col, piece):
        if self.board[row][col] is None:
            return False
        pawn_idx = int(self.board[row][col][1])
        self.board[row][col] = f'{piece}{pawn_idx + 2}'
        return True

    def is_valid_move(self, start_row, start_col, end_row, end_col):
        if self.board[end_row][end_col] != 'z' and self.board[end_row][end_col]:
            return False

        piece = self.board[start_row][start_col]
        if piece is None or piece == 'z':
            return False
        piece = piece[0]
        if piece == 'p':
            return self.check_pawn_move(start_row, start_col, end_row, end_col)
        elif piece == 'r':
            if self.check_rook_move(start_row, start_col, end_row, end_col):
                self.can_do_castling = False
                return True
            return False
        elif piece == 'k':
            return self.check_knight_move(start_row, start_col, end_row, end_col)
        elif piece == 'b':
            return self.check_bishop_move(start_row, start_col, end_row, end_col)
        elif piece == 'q':
            return self.check_queen_move(start_row, start_col, end_row, end_col)
        elif piece == 'K':
            if self.check_king_move(start_row, start_col, end_row, end_col):
                self.can_do_castling = False
                return True
            return False

    def move_piece(self, start_row, start_col, end_row, end_col):
        if self.is_valid_move(start_row, start_col, end_row, end_col):
            self.board[end_row][end_col] = self.board[start_row][start_col]
            self.board[start_row][start_col] = None
            if self.move_wave() == TurnResult.CHECKMATE:
                return TurnResult.CHECKMATE
            if self.difficulty != Difficulties.EASY:
                self.last_moved_piece = self.board[end_row][end_col]
            return TurnResult.OK

        castling_move = self.check_castling_move(start_row, start_col, end_col)
        if castling_move:
            self.board[start_row][start_col] = None
            self.board[end_row][end_col] = None
            self.board[start_row][castling_move[0]] = 'K'
            self.board[start_row][castling_move[1]] = f'r{castling_move[2]}'
            if self.move_wave() == TurnResult.CHECKMATE:
                return TurnResult.CHECKMATE
            if self.difficulty != Difficulties.EASY:
                self.last_moved_piece = 'K'
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
                    if self.is_checkmate(i, j + 1):
                        return TurnResult.CHECKMATE
                    self.board[i][j + 1] = 'z'
                    if move[1] == 'm':
                        self.board[i][j] = None
                else:
                    if self.is_checkmate(i, j - 1):
                        return TurnResult.CHECKMATE
                    self.board[i][j - 1] = 'z'
                    if move[1] == 'm':
                        self.board[i][j] = None
        return self.create_new_zombies(random.randint(0, int(self.difficulty.value)))

    def create_new_zombies(self, n):
        new_spots = random.sample(range(8), n)
        for i in new_spots:
            if self.board[0][i] and self.board[0][i][0] == 'K':
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

    def check_castling_move(self, row, start_col, end_col):
        if not self.can_do_castling:
            return None

        start_piece = self.board[row][start_col]
        end_piece = self.board[row][end_col]
        if start_piece is None or end_piece is None:
            return None

        valid_combinations = (
            ('r0', 'K'),
            ('r1', 'K'),
            ('K', 'r0'),
            ('K', 'r1')
        )
        if (start_piece, end_piece) not in valid_combinations:
            return None

        step = 1 if end_col > start_col else -1
        for col in range(start_col + step, end_col, step):
            if self.board[row][col]:
                return None

        self.can_do_castling = False
        # king pos, rook pos, rook index
        if start_piece == 'r0':
            return end_col - 2, end_col - 1, 0
        if start_piece == 'r1':
            return end_col + 2, end_col + 1, 1
        if end_piece == 'r0':
            return start_col - 2, start_col - 1, 0
        return start_col + 2, start_col + 1, 1

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
                if self.board[start_row][col]:
                    return False
        else:
            step = 1 if end_row > start_row else -1
            for row in range(start_row + step, end_row, step):
                if self.board[row][start_col]:
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
            if self.board[current_row][current_col]:
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
        self.game_mode = GameModes.SURVIVE_THE_LONGEST

    def create_new_zombies(self, n):
        new_spots = random.sample(range(8), n)
        for i in new_spots:
            if self.board[0][i] and self.board[0][i][0] == 'K':
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
        self.game_mode = GameModes.CAPTURE_THE_MOST

    def move_piece(self, start_row, start_col, end_row, end_col):
        if self.is_valid_move(start_row, start_col, end_row, end_col):
            if self.board[end_row][end_col] == 'z':
                self.captured += 1
            self.board[end_row][end_col] = self.board[start_row][start_col]
            self.board[start_row][start_col] = None
            if self.move_wave() == TurnResult.CHECKMATE:
                return TurnResult.CHECKMATE
            if self.difficulty != Difficulties.EASY:
                self.last_moved_piece = self.board[end_row][end_col]
            return TurnResult.OK

        castling_move = self.check_castling_move(start_row, start_col, end_col)
        if castling_move:
            self.board[start_row][start_col] = None
            self.board[end_row][end_col] = None
            self.board[start_row][castling_move[0]] = 'K'
            self.board[start_row][castling_move[1]] = f'r{castling_move[2]}'
            if self.move_wave() == TurnResult.CHECKMATE:
                return TurnResult.CHECKMATE
            if self.difficulty != Difficulties.EASY:
                self.last_moved_piece = 'K'
            return TurnResult.OK

        return TurnResult.WRONG

    def endgame_info(self, won):
        return f"Captured zombies: {self.captured}"


class BlockTheBorder(Gameplay):
    def __init__(self, board_y, difficulty):
        super().__init__(board_y, difficulty)
        self.turns_taken = 0
        self.pieces_left = 16
        self.game_mode = GameModes.BLOCK_THE_BORDER

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
            if self.difficulty != Difficulties.EASY:
                self.last_moved_piece = self.board[end_row][end_col]
            return TurnResult.OK

        castling_move = self.check_castling_move(start_row, start_col, end_col)
        if castling_move:
            self.board[start_row][start_col] = None
            self.board[end_row][end_col] = None
            self.board[start_row][castling_move[0]] = 'K'
            self.board[start_row][castling_move[1]] = f'r{castling_move[2]}'
            self.turns_taken += 1
            result = self.move_wave()
            if result == TurnResult.CHECKMATE:
                return TurnResult.CHECKMATE
            elif result == TurnResult.WIN:
                return TurnResult.WIN
            if self.difficulty != Difficulties.EASY:
                self.last_moved_piece = 'K'
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
                else:
                    if self.is_checkmate(i, j - 1):
                        return TurnResult.CHECKMATE
                    self.board[i][j - 1] = 'z'
                    if move[1] == 'm':
                        self.board[i][j] = None
                    else:
                        self.pieces_left -= 1
        if self.pieces_left < 8:
            return TurnResult.CHECKMATE
        return self.create_new_zombies(random.randint(0, int(self.difficulty.value)))

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
        self.game_mode = GameModes.BLOCK_AND_CLEAR

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
