import random
from enum import Enum


class GameMode(Enum):
    SURVIVE_THE_LONGEST = 'Survive The Longest'
    CAPTURE_THE_MOST = 'Capture The Most'
    BLOCK_THE_BORDER = 'Block The Border'
    BLOCK_AND_CLEAR = 'Block And Clear'
    CLEAR_THE_BOARD = 'Clear The Board'

    def __str__(self):
        return self.value

    def switch(self, include_clear=False):
        game_modes = list(GameMode)
        current_index = game_modes.index(self)
        if include_clear:
            next_index = (current_index + 1) % 5
        else:
            next_index = (current_index + 1) % 4
        return game_modes[next_index]


class Difficulty(Enum):
    # (number of zombies, chance of spawning %)
    EASY = ((0, 50), (1, 50))
    NORMAL = ((0, 30), (1, 60), (2, 10))
    HARD = ((0, 20), (1, 40), (2, 40))
    EXTREME = ((0, 20), (1, 50), (2, 30))

    def __str__(self):
        return self.name.capitalize()

    def switch(self):
        difficulties = list(Difficulty)
        current_index = difficulties.index(self)
        next_index = (current_index + 1) % len(difficulties)
        return difficulties[next_index]

    def roll_n(self):
        distribution = self.value
        roll = random.randint(1, 100)
        cumulative_chance = 0
        for count, chance in distribution:
            cumulative_chance += chance
            if roll <= cumulative_chance:
                return count

        return distribution[-1][0]


class TurnResult(Enum):
    OK = 1
    CAPTURED = 2
    WRONG = 3
    WIN = 4
    CHECKMATE = 5


class Gameplay:
    def __init__(self, board_height, difficulty, board=None):
        self.zombie_spots = set()
        if board_height < 2 or (board and board_height != len(board)):
            raise ValueError('Board height cannot be lower than 2 and must match the board\'s actual height')

        if board is None:
            self.board = [
                [None for _ in range(8)] for _ in range(board_height - 2)
            ]
            self.board.append([f'pp{i}' for i in range(8)])
            self.board.append(['pr8', 'pk9', 'pb10', 'pq11', 'pK12', 'pb13', 'pk14', 'pr15'])

            self.pieces_left = 16
        else:
            self.board = []
            self.pieces_left = 0

            for row in range(board_height):
                for col in range(8):
                    if board[row][col] and board[row][col][0] == 'p':
                        self.pieces_left += 1
                self.board.append(board[row].copy())

        self.selected_piece = None
        self.last_moved_piece = None
        self.turns = 1
        self.moves = 0
        self.zombies_captured = 0
        self.castling_combinations = [
            ('pK12', 'pr8'),
            ('pr8', 'pK12'),
            ('pK12', 'pr15'),
            ('pr15', 'pK12'),
        ]
        self.board_height = board_height
        self.difficulty = difficulty

    @staticmethod
    def init_game_mode(board_height, difficulty, game_mode, board=None):
        if game_mode == GameMode.SURVIVE_THE_LONGEST:
            return SurviveTheLongest(board_height, difficulty, board)
        elif game_mode == GameMode.CAPTURE_THE_MOST:
            return CaptureTheMost(board_height, difficulty, board)
        elif game_mode == GameMode.BLOCK_THE_BORDER:
            return BlockTheBorder(board_height, difficulty, board)
        elif game_mode == GameMode.BLOCK_AND_CLEAR:
            return BlockAndClear(board_height, difficulty, board)
        elif game_mode == GameMode.CLEAR_THE_BOARD:
            return ClearTheBoard(board_height, difficulty, board)

    def get_piece_at(self, row, col):
        return self.board[row][col]

    def select_piece(self, row, col):
        if self.is_piece(row, col) and self.board[row][col] != self.last_moved_piece:
            self.selected_piece = (row, col)
            return True
        return False

    def unselect_piece(self):
        self.selected_piece = None

    def is_zombie(self, row, col):
        return self.board[row][col] and self.board[row][col][0] == 'z'

    def is_piece(self, row, col):
        return self.board[row][col] and self.board[row][col][0] == 'p'

    def is_pawn(self, row, col):
        return self.board[row][col] and self.board[row][col][:2] == 'pp'

    def is_checkmate(self, i, j):
        return self.board[i][j] and self.board[i][j][:2] == 'pK'

    def skip_turn(self):
        self.last_moved_piece = None
        self.turns += 1
        if self.move_wave() == TurnResult.CHECKMATE:
            return TurnResult.CHECKMATE
        return TurnResult.OK

    def promote_pawn(self, col, piece_type):
        if not self.is_pawn(0, col):
            return False

        pawn_idx = self.board[0][col][2]
        self.board[0][col] = f'{piece_type}{pawn_idx}'
        return True

    def is_valid_move(self, start_row, start_col, end_row, end_col):
        if self.is_piece(end_row, end_col) or not self.is_piece(start_row, start_col):
            return False

        piece_type = self.board[start_row][start_col][1]
        if piece_type == 'p':
            return self.check_pawn_move(start_row, start_col, end_row, end_col)
        elif piece_type == 'r':
            return self.check_rook_move(start_row, start_col, end_row, end_col)
        elif piece_type == 'k':
            return self.check_knight_move(start_row, start_col, end_row, end_col)
        elif piece_type == 'b':
            return self.check_bishop_move(start_row, start_col, end_row, end_col)
        elif piece_type == 'q':
            return self.check_queen_move(start_row, start_col, end_row, end_col)
        elif piece_type == 'K':
            return self.check_king_move(start_row, start_col, end_row, end_col)
        return False

    def move_piece(self, start_row, start_col, end_row, end_col):
        if self.is_valid_move(start_row, start_col, end_row, end_col):
            if self.is_zombie(end_row, end_col):
                self.zombies_captured += 1

            if self.board[end_row][end_col] == 'ze':
                self.board[end_row][end_col] = self.board[start_row][start_col]
                self.activate_exploding_zombie(end_row, end_col)
            else:
                self.board[end_row][end_col] = self.board[start_row][start_col]

            if self.castling_combinations:
                piece = self.board[start_row][start_col]
                if piece == 'pr8':
                    del self.castling_combinations[:2]
                elif piece == 'pr15':
                    del self.castling_combinations[2:4]
                elif piece == 'pK12':
                    self.castling_combinations = None

            self.board[start_row][start_col] = None
            self.turns += 1
            self.moves += 1

            result = self.move_wave()
            if result == TurnResult.CHECKMATE:
                return TurnResult.CHECKMATE
            elif result == TurnResult.WIN:
                return TurnResult.WIN
            if self.difficulty == Difficulty.EXTREME:
                self.last_moved_piece = self.board[end_row][end_col]
            return TurnResult.OK

        castling_move = self.check_castling_move(start_row, start_col, end_col)
        if castling_move:
            self.turns += 1
            self.moves += 1
            self.castling_combinations = None
            self.board[start_row][start_col] = None
            self.board[end_row][end_col] = None
            self.board[start_row][castling_move[0]] = 'pK12'
            self.board[start_row][castling_move[1]] = f'pr{castling_move[2]}'
            if self.move_wave() == TurnResult.CHECKMATE:
                return TurnResult.CHECKMATE
            if self.difficulty == Difficulty.EXTREME:
                self.last_moved_piece = 'pK12'
            return TurnResult.OK

        return TurnResult.WRONG

    def move_wave(self):
        moved_zombies = set()
        for i in reversed(range(self.board_height)):
            for j in reversed(range(8)):
                if self.board[i][j] is None or self.is_piece(i, j) or (i, j) in moved_zombies:
                    continue

                zombie = self.board[i][j][1]
                pos = None

                result = TurnResult.OK
                if zombie == 'w':
                    result, pos = self.move_walker(i, j)
                elif zombie == 's':
                    result, pos = self.move_stomper(i, j)
                elif zombie == 'e':
                    result, pos = self.move_exploding(i, j)
                elif zombie == 'i':
                    result, pos = self.move_infected(i, j)

                if result == TurnResult.CHECKMATE:
                    return TurnResult.CHECKMATE
                moved_zombies.add(pos)

        return self.create_new_zombies(self.difficulty.roll_n())

    def move_walker(self, i, j):
        captured = False
        if i + 1 == self.board_height or self.is_zombie(i + 1, j):  # down occupied, go right
            if j + 1 == 8 or self.is_zombie(i, j + 1):  # right occupied, go left
                if self.is_zombie(i, j - 1):  # all sides occupied
                    return TurnResult.OK, None
                else:
                    if self.is_checkmate(i, j - 1):
                        return TurnResult.CHECKMATE, None
                    if self.board[i][j - 1]:
                        captured = True
                    self.board[i][j - 1] = 'zw'
                    self.board[i][j] = None
                    pos = (i, j - 1)
            else:
                if self.is_checkmate(i, j + 1):
                    return TurnResult.CHECKMATE, None
                if self.board[i][j + 1]:
                    captured = True
                self.board[i][j + 1] = 'zw'
                self.board[i][j] = None
                pos = (i, j + 1)
        else:
            if self.is_checkmate(i + 1, j):
                return TurnResult.CHECKMATE, None
            if self.board[i + 1][j]:
                captured = True
            self.board[i + 1][j] = 'zw'
            self.board[i][j] = None
            pos = (i + 1, j)

        result = TurnResult.CAPTURED if captured else TurnResult.OK
        return result, pos

    # if captures a piece, can move again (up to 3 times)
    def move_stomper(self, i, j, moves_left=3):
        if moves_left <= 0:
            return TurnResult.OK, None
        captured = False
        if i + 1 == self.board_height or self.is_zombie(i + 1, j):  # down occupied, go right
            if j + 1 == 8 or self.is_zombie(i, j + 1):  # right occupied, go left
                if j - 1 == -1 or self.is_zombie(i, j - 1):  # all sides occupied
                    return TurnResult.OK, None
                else:
                    if self.is_checkmate(i, j - 1):
                        return TurnResult.CHECKMATE, None
                    if self.board[i][j - 1]:
                        captured = True
                    new_i, new_j = i, j - 1
                    self.board[i][j - 1] = 'zs'
                    self.board[i][j] = None
            else:
                if self.is_checkmate(i, j + 1):
                    return TurnResult.CHECKMATE, None
                if self.board[i][j + 1]:
                    captured = True
                new_i, new_j = i, j + 1
                self.board[i][j + 1] = 'zs'
                self.board[i][j] = None
        else:
            if self.is_checkmate(i + 1, j):
                return TurnResult.CHECKMATE, None
            if self.board[i + 1][j]:
                captured = True
            new_i, new_j = i + 1, j
            self.board[i + 1][j] = 'zs'
            self.board[i][j] = None

        if captured and moves_left > 1:
            chain_result, pos = self.move_stomper(new_i, new_j, moves_left - 1)
            if chain_result == TurnResult.CHECKMATE:
                return TurnResult.CHECKMATE, None
            return TurnResult.CAPTURED, pos

        result = TurnResult.CAPTURED if captured else TurnResult.OK
        return result, (new_i, new_j)

    def move_exploding(self, i, j):
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        random.shuffle(directions)

        for di, dj in directions:
            new_i, new_j = i + di, j + dj
            if 0 <= new_i < self.board_height and 0 <= new_j < 8:
                if not self.is_zombie(new_i, new_j):
                    if self.is_checkmate(new_i, new_j):
                        return TurnResult.CHECKMATE, None
                    captured = False
                    if self.board[new_i][new_j]:
                        captured = True
                    self.board[new_i][new_j] = 'ze'
                    self.board[i][j] = None

                    result = TurnResult.CAPTURED if captured else TurnResult.OK
                    return result, (new_i, new_j)
        return TurnResult.OK

    def move_infected(self, i, j):
        captured = False
        if i + 1 == self.board_height or self.is_zombie(i + 1, j):  # down occupied, go right
            if j + 1 == 8 or self.is_zombie(i, j + 1):  # right occupied, go left
                if j - 1 == -1 or self.is_zombie(i, j - 1):  # all sides occupied
                    return TurnResult.OK, None
                else:
                    if self.is_checkmate(i, j - 1):
                        return TurnResult.CHECKMATE, None
                    if self.board[i][j - 1]:
                        captured = True
                        self.board[i][j - 1] = 'zw'
                    else:
                        self.board[i][j] = None
                        self.board[i][j - 1] = 'zi'
                    pos = (i, j - 1)
            else:
                if self.is_checkmate(i, j + 1):
                    return TurnResult.CHECKMATE, None
                if self.board[i][j + 1]:
                    captured = True
                    self.board[i][j + 1] = 'zw'
                else:
                    self.board[i][j] = None
                    self.board[i][j + 1] = 'zi'
                pos = (i, j + 1)
        else:
            if self.is_checkmate(i + 1, j):
                return TurnResult.CHECKMATE, None
            if self.board[i + 1][j]:
                captured = True
                self.board[i + 1][j] = 'zw'
            else:
                self.board[i][j] = None
                self.board[i + 1][j] = 'zi'
            pos = (i + 1, j)

        result = TurnResult.CAPTURED if captured else TurnResult.OK
        return result, pos

    def create_new_zombies(self, n):
        new_spots = random.sample(range(8), n)
        for i in new_spots:
            if self.is_checkmate(0, i):
                return TurnResult.CHECKMATE

            zombie_chance = random.randint(1, 100)
            if zombie_chance <= 10:
                self.board[0][i] = 'ze'
            elif 10 < zombie_chance <= 20:
                self.board[0][i] = 'zs'
            elif 20 < zombie_chance <= 50:
                self.board[0][i] = 'zi'
            else:
                self.board[0][i] = 'zw'
        return TurnResult.OK

    def activate_exploding_zombie(self, row, col):
        #      up
        # left ze  right
        #     down
        if row - 1 >= 0:
            self.board[row - 1][col] = None
        if row + 1 < self.board_height:
            self.board[row + 1][col] = None
        if col - 1 >= 0:
            self.board[row][col - 1] = None
        if col + 1 < 8:
            self.board[row][col + 1] = None

    def check_castling_move(self, row, start_col, end_col):
        if not self.castling_combinations:
            return None
        start_piece = self.board[row][start_col]
        end_piece = self.board[row][end_col]
        if start_piece is None or end_piece is None:
            return None

        if (start_piece, end_piece) not in self.castling_combinations:
            return None

        step = 1 if end_col > start_col else -1
        for col in range(start_col + step, end_col, step):
            if self.board[row][col]:
                return None

        # king pos, rook pos, rook index
        if start_piece == 'pr8':
            return end_col - 2, end_col - 1, 0
        if start_piece == 'pr15':
            return end_col + 2, end_col + 1, 1
        if end_piece == 'pr8':
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
            return self.is_zombie(end_row, end_col)
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
    def __init__(self, board_height, difficulty, board=None):
        super().__init__(board_height, difficulty, board)
        self.game_mode = GameMode.SURVIVE_THE_LONGEST

    def endgame_info(self, won):
        return f"Survived turns: {self.turns}"


class CaptureTheMost(Gameplay):
    def __init__(self, board_height, difficulty, board=None):
        super().__init__(board_height, difficulty, board)
        self.game_mode = GameMode.CAPTURE_THE_MOST

    def endgame_info(self, won):
        return f"Captured zombies: {self.zombies_captured}"


class BlockTheBorder(Gameplay):
    def __init__(self, board_height, difficulty, board=None):
        super().__init__(board_height, difficulty, board)
        self.game_mode = GameMode.BLOCK_THE_BORDER

    def get_free_border_spots(self):
        free_spots = []
        zombie_spots = []
        for i in range(8):
            if self.board[0][i] is None:
                free_spots.append(i)
            elif self.is_zombie(0, i):
                zombie_spots.append(i)
        return free_spots, zombie_spots

    def move_wave(self):
        moved_zombies = set()
        for i in reversed(range(self.board_height)):
            for j in reversed(range(8)):
                if self.board[i][j] is None or self.is_piece(i, j) or (i, j) in moved_zombies:
                    continue

                zombie = self.board[i][j][1]
                pos = None

                result = TurnResult.OK
                if zombie == 'w':
                    result, pos = self.move_walker(i, j)
                elif zombie == 's':
                    result, pos = self.move_stomper(i, j)
                elif zombie == 'e':
                    result, pos = self.move_exploding(i, j)
                elif zombie == 'i':
                    result, pos = self.move_infected(i, j)

                if result == TurnResult.CAPTURED:
                    self.pieces_left -= 1
                elif result == TurnResult.CHECKMATE:
                    return TurnResult.CHECKMATE
                moved_zombies.add(pos)

        if self.pieces_left < 8:
            return TurnResult.CHECKMATE

        return self.create_new_zombies(self.difficulty.roll_n())

    def create_new_zombies(self, n):
        new_spots, zombie_spots = self.get_free_border_spots()
        if not new_spots:
            if not zombie_spots:
                return TurnResult.WIN
            else:
                return TurnResult.OK
        new_spots = random.sample(new_spots, n)
        for i in new_spots:
            zombie_chance = random.randint(1, 100)
            if zombie_chance <= 10:
                self.board[0][i] = 'ze'
            elif zombie_chance <= 20:
                self.board[0][i] = 'zs'
            elif zombie_chance <= 50:
                self.board[0][i] = 'zi'
            else:
                self.board[0][i] = 'zw'
        return TurnResult.OK

    def endgame_info(self, won):
        if won:
            return f"You blocked the border in {self.moves} moves"
        return "You didn't manage to block the border"


class BlockAndClear(BlockTheBorder):
    def __init__(self, board_height, difficulty, board=None):
        super().__init__(board_height, difficulty, board)
        self.game_mode = GameMode.BLOCK_AND_CLEAR

    def is_board_clear(self):
        for i in range(self.board_height):
            for j in range(8):
                if self.is_zombie(i, j):
                    return False
        return True

    def create_new_zombies(self, n):
        new_spots, zombie_spots = self.get_free_border_spots()
        if not new_spots and not zombie_spots:
            if self.is_board_clear():
                return TurnResult.WIN
            else:
                return TurnResult.OK

        new_spots = random.sample(new_spots, n)
        for i in new_spots:
            zombie_chance = random.randint(1, 100)
            if zombie_chance <= 10:
                self.board[0][i] = 'ze'
            elif 10 < zombie_chance <= 20:
                self.board[0][i] = 'zs'
            elif 20 < zombie_chance <= 50:
                self.board[0][i] = 'zi'
            else:
                self.board[0][i] = 'zw'
        return TurnResult.OK

    def endgame_info(self, won):
        if won:
            return f"You cleared the board and blocked the border in {self.moves} moves"
        return "You didn't manage to block the border and clear the board"


class ClearTheBoard(BlockAndClear):
    def __init__(self, board_height, difficulty, board=None):
        super().__init__(board_height, difficulty, board)
        self.game_mode = GameMode.CLEAR_THE_BOARD

    def move_wave(self):
        if self.is_board_clear():
            return TurnResult.WIN

        moved_zombies = set()
        for i in reversed(range(self.board_height)):
            for j in reversed(range(8)):
                if self.board[i][j] is None or self.is_piece(i, j) or (i, j) in moved_zombies:
                    continue

                zombie = self.board[i][j][1]
                pos = None

                result = TurnResult.OK
                if zombie == 'w':
                    result, pos = self.move_walker(i, j)
                elif zombie == 's':
                    result, pos = self.move_stomper(i, j)
                elif zombie == 'e':
                    result, pos = self.move_exploding(i, j)
                elif zombie == 'i':
                    result, pos = self.move_infected(i, j)

                if result == TurnResult.CAPTURED:
                    self.pieces_left -= 1
                elif result == TurnResult.CHECKMATE:
                    return TurnResult.CHECKMATE
                moved_zombies.add(pos)

        return TurnResult.OK

    def endgame_info(self, won):
        if won:
            return f"You cleared the board in {self.moves} moves"
        return "You didn't manage to clear the board"
