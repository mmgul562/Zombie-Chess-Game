import random
from enum import Enum


class GameMode(Enum):
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
        game_modes = list(GameMode)
        current_index = game_modes.index(self)
        next_index = (current_index + 1) % len(game_modes)
        return game_modes[next_index]


class Difficulty(Enum):
    EASY = 1
    NORMAL = 2
    HARD = 3
    EXTREME = 4

    def __str__(self):
        return self.name.capitalize()

    def switch(self):
        difficulties = list(Difficulty)
        current_index = difficulties.index(self)
        next_index = (current_index + 1) % len(difficulties)
        return difficulties[next_index]


class TurnResult(Enum):
    OK = 1
    CAPTURED = 2
    WRONG = 3
    WIN = 4
    CHECKMATE = 5


class Gameplay:
    def __init__(self, board_y, difficulty):
        self.zombie_spots = set({})
        self.board = [
            [None for _ in range(8)] for _ in range(board_y - 2)
        ]
        self.board.append([f'pp{i}' for i in range(8)])
        self.board.append(['pr8', 'pk9', 'pb10', 'pq11', 'pK12', 'pb13', 'pk14', 'pr15'])
        self.selected_piece = None
        self.last_moved_piece = None
        self.turns_taken = 0
        self.can_do_castling = True
        self.board_y = board_y
        self.difficulty = difficulty

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
        return self.board[row][col] and self.board[row][col][0:2] == 'pp'

    def is_selected(self, row, col):
        return self.selected_piece == (row, col)

    def is_checkmate(self, i, j):
        return self.board[i][j] and self.board[i][j][0:2] == 'pK'

    def skip_turn(self):
        self.last_moved_piece = None
        if self.move_wave() == TurnResult.CHECKMATE:
            return TurnResult.CHECKMATE
        return TurnResult.OK

    def promote_pawn(self, row, col, piece_type):
        if not self.is_pawn(row, col):
            return False

        pawn_idx = self.board[row][col][2]
        self.board[row][col] = f'{piece_type}{pawn_idx}'
        return True

    def is_valid_move(self, start_row, start_col, end_row, end_col):
        if self.is_piece(end_row, end_col) or not self.is_piece(start_row, start_col):
            return False

        piece_type = self.board[start_row][start_col][1]
        if piece_type == 'p':
            return self.check_pawn_move(start_row, start_col, end_row, end_col)
        elif piece_type == 'r':
            if self.check_rook_move(start_row, start_col, end_row, end_col):
                self.can_do_castling = False
                return True
            return False
        elif piece_type == 'k':
            return self.check_knight_move(start_row, start_col, end_row, end_col)
        elif piece_type == 'b':
            return self.check_bishop_move(start_row, start_col, end_row, end_col)
        elif piece_type == 'q':
            return self.check_queen_move(start_row, start_col, end_row, end_col)
        elif piece_type == 'K':
            if self.check_king_move(start_row, start_col, end_row, end_col):
                self.can_do_castling = False
                return True
            return False
        return False

    def move_piece(self, start_row, start_col, end_row, end_col):
        if self.is_valid_move(start_row, start_col, end_row, end_col):
            if self.board[end_row][end_col] == 'ze':
                self.board[end_row][end_col] = self.board[start_row][start_col]
                self.activate_exploding_zombie(end_row, end_col)
            else:
                self.board[end_row][end_col] = self.board[start_row][start_col]
            self.board[start_row][start_col] = None
            self.turns_taken += 1
            result = self.move_wave()
            if result == TurnResult.CHECKMATE:
                return TurnResult.CHECKMATE
            elif result == TurnResult.WIN:
                return TurnResult.WIN
            if self.difficulty != Difficulty.EASY:
                self.last_moved_piece = self.board[end_row][end_col]
            return TurnResult.OK

        castling_move = self.check_castling_move(start_row, start_col, end_col)
        if castling_move:
            self.turns_taken += 1
            self.board[start_row][start_col] = None
            self.board[end_row][end_col] = None
            self.board[start_row][castling_move[0]] = 'pK12'
            self.board[start_row][castling_move[1]] = f'pr{castling_move[2]}'
            if self.move_wave() == TurnResult.CHECKMATE:
                return TurnResult.CHECKMATE
            if self.difficulty != Difficulty.EASY:
                self.last_moved_piece = 'pK12'
            return TurnResult.OK

        return TurnResult.WRONG

    def move_wave(self):
        moved_zombies = set()
        for i in reversed(range(self.board_y)):
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
        return self.create_new_zombies(random.randint(0, self.difficulty.value))

    def move_walker(self, i, j):
        captured = False
        pos = None
        if i + 1 == self.board_y or self.is_zombie(i + 1, j):  # down occupied, go right
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
        new_i, new_j = i, j
        if i + 1 == self.board_y or self.is_zombie(i + 1, j):  # down occupied, go right
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
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        random.shuffle(directions)

        for di, dj in directions:
            new_i, new_j = i + di, j + dj
            if 0 <= new_i < self.board_y and 0 <= new_j < 8:
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
        pos = None
        if i + 1 == self.board_y or self.is_zombie(i + 1, j):  # down occupied, go right
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
        if row + 1 < self.board_y:
            self.board[row + 1][col] = None
        if col - 1 >= 0:
            self.board[row][col - 1] = None
        if col + 1 < 8:
            self.board[row][col + 1] = None

    def check_castling_move(self, row, start_col, end_col):
        if not self.can_do_castling:
            return None
        start_piece = self.board[row][start_col]
        end_piece = self.board[row][end_col]
        if start_piece is None or end_piece is None:
            return None

        combinations = (
            ('pK12', 'pr8'),
            ('pK12', 'pr15'),
            ('pr8', 'pK12'),
            ('pr15', 'pK12'),
        )
        if (start_piece, end_piece) not in combinations:
            return None

        step = 1 if end_col > start_col else -1
        for col in range(start_col + step, end_col, step):
            if self.board[row][col]:
                return None

        self.can_do_castling = False
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
    def __init__(self, board_y, difficulty):
        super().__init__(board_y, difficulty)
        self.waves = 0
        self.game_mode = GameMode.SURVIVE_THE_LONGEST

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
        if new_spots > 0:
            self.waves += 1
        return TurnResult.OK

    def endgame_info(self, won):
        return f"Survived waves: {self.waves}"


class CaptureTheMost(Gameplay):
    def __init__(self, board_y, difficulty):
        super().__init__(board_y, difficulty)
        self.captured = 0
        self.game_mode = GameMode.CAPTURE_THE_MOST

    def move_piece(self, start_row, start_col, end_row, end_col):
        if self.is_valid_move(start_row, start_col, end_row, end_col):
            if self.is_zombie(end_row, end_col):
                self.captured += 1
            self.board[end_row][end_col] = self.board[start_row][start_col]
            self.board[start_row][start_col] = None
            if self.move_wave() == TurnResult.CHECKMATE:
                return TurnResult.CHECKMATE
            if self.difficulty != Difficulty.EASY:
                self.last_moved_piece = self.board[end_row][end_col]
            return TurnResult.OK

        castling_move = self.check_castling_move(start_row, start_col, end_col)
        if castling_move:
            self.board[start_row][start_col] = None
            self.board[end_row][end_col] = None
            self.board[start_row][castling_move[0]] = 'pK12'
            self.board[start_row][castling_move[1]] = f'pr{castling_move[2]}'
            if self.move_wave() == TurnResult.CHECKMATE:
                return TurnResult.CHECKMATE
            if self.difficulty != Difficulty.EASY:
                self.last_moved_piece = 'pK12'
            return TurnResult.OK

        return TurnResult.WRONG

    def endgame_info(self, won):
        return f"Captured zombies: {self.captured}"


class BlockTheBorder(Gameplay):
    def __init__(self, board_y, difficulty):
        super().__init__(board_y, difficulty)
        self.pieces_left = 16
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
        for i in reversed(range(self.board_y)):
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
        return self.create_new_zombies(random.randint(0, self.difficulty.value))

    def create_new_zombies(self, n):
        new_spots, zombie_spots = self.get_free_border_spots()
        if not new_spots and not zombie_spots:
            return TurnResult.WIN
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
            return f"You blocked the border in {self.turns_taken} turns"
        return "You didn't manage to block the border"


class BlockAndClear(BlockTheBorder):
    def __init__(self, board_y, difficulty):
        super().__init__(board_y, difficulty)
        self.game_mode = GameMode.BLOCK_AND_CLEAR

    def is_board_clear(self):
        for i in range(self.board_y):
            for j in range(8):
                if self.is_zombie(i, j):
                    return False
        return True

    def create_new_zombies(self, n):
        new_spots, zombie_spots = self.get_free_border_spots()
        if not new_spots and not zombie_spots and self.is_board_clear():
            return TurnResult.WIN
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
            return f"You cleared the board and blocked the border in {self.turns_taken} turns"
        return "You didn't manage to block the border and clear the board"
