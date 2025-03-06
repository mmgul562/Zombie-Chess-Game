import json
import random
import string
import os

from game.game_modes import GameMode, Difficulty


class CustomGameMode:
    def __init__(self, name='', board_height=8, can_change_gm=True, can_change_difficulty=True,
                 base_gm=GameMode.CLEAR_THE_BOARD, difficulty=Difficulty.EASY, board=None):
        self.name = name
        self.board = board
        self.board_height = board_height
        self.can_change_gm = can_change_gm
        self.can_change_difficulty = can_change_difficulty
        self.base_gm = base_gm
        self.difficulty = difficulty


class CustomGameModeCreator:
    def __init__(self):
        self.game = CustomGameMode(board=[[None for _ in range(8)] for _ in range(8)])
        self.is_name_ok = False
        self.has_king = False
        self.input_focused = False
        self.selected_piece = None
        self.error_msg = None

    def reset(self):
        self.game.name = ''
        self.game.can_change_gm = True
        self.game.can_change_difficulty = True
        self.selected_piece = None
        self.error_msg = None
        self.game.board = [[None for _ in range(8)] for _ in range(self.game.board_height)]

    def get_piece_at(self, i, j):
        return self.game.board[i][j]

    def select_piece(self, piece):
        self.selected_piece = piece

    def unselect_piece(self):
        self.selected_piece = None

    def add_board_height(self):
        if self.game.board_height + 1 > 18:
            return
        self.game.board_height += 1
        self.game.board.insert(0, [None for _ in range(8)])

    def rm_board_height(self):
        if self.game.board_height - 1 < 6:
            return
        self.game.board_height -= 1
        self.game.board.pop(0)

    def clear_board(self):
        self.game.board = [[None for _ in range(8)] for _ in range(self.game.board_height)]

    def put_selected_piece(self, i, j):
        if self.selected_piece:
            self.game.board[i][j] = self.selected_piece

    def rm_piece(self, i, j):
        self.game.board[i][j] = None

    def check_for_king(self):
        for i in range(self.game.board_height):
            for j in range(8):
                if self.game.board[i][j] and self.game.board[i][j][1] == 'K':
                    self.has_king = True
                    return
        self.has_king = False

    def check_name(self):
        if 20 >= len(self.game.name) >= 3:
            self.is_name_ok = True
        else:
            self.is_name_ok = False

    def save(self):
        while True:
            random_string = ''.join(random.choices(string.digits + string.ascii_letters, k=12))
            filename = f'custom_gm/{random_string}.json'

            if not os.path.exists(filename):
                break

        index = 0
        for i in range(self.game.board_height):
            for j in range(8):
                if self.game.board[i][j] and self.game.board[i][j][0] == 'p':
                    self.game.board[i][j] += str(index)
                    index += 1

        data = {
            'name': self.game.name,
            'board_height': self.game.board_height,
            'can_change_gm': self.game.can_change_gm,
            'can_change_difficulty': self.game.can_change_difficulty,
            'base_gm': str(self.game.base_gm),
            'difficulty': str(self.game.difficulty),
            'board': self.game.board
        }
        try:
            with open(filename, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            self.error_msg = str(e)


class CustomGameModeLoader:
    def __init__(self):
        self.game_modes = {}
        self.selected_gm = None
        self.error_msg = None

    def reset(self):
        self.error_msg = None
        self.selected_gm = None

    def unselect_gm(self):
        self.selected_gm = None

    def select_gm(self, gm_id):
        self.selected_gm = (gm_id, self.game_modes[gm_id])

    def parse_gm_json(self, filename, gm_json):
        if 'board_height' not in gm_json:
            self.error_msg = f"'board_height' field is required ({filename})"
            return None
        if 'base_gm' not in gm_json:
            self.error_msg = f"'base_gm' field is required ({filename})"
            return None
        if 'difficulty' not in gm_json:
            self.error_msg = f"'difficulty' field is required ({filename})"
            return None
        if 'board' not in gm_json:
            self.error_msg = f"'board' field is required ({filename})"
            return None
        if 'can_change_gm' not in gm_json:
            self.error_msg = f"'can_change_gm' field is required ({filename})"
            return None
        if 'can_change_difficulty' not in gm_json:
            self.error_msg = f"'can_change_difficulty' field is required ({filename})"
            return None

        board = gm_json['board']
        if type(board) != list:
            self.error_msg = f"Board must be a LIST of lists of strings/nulls ({filename})"
            return None
        board_height = gm_json['board_height']
        if type(board_height) != int or board_height > 18 or board_height < 6 or board_height != len(board):
            self.error_msg = f"Board height must be an integer between 6 and 18 and match the number of rows in 'board' field ({filename})"
            return None

        for i in range(board_height):
            if type(board[i]) != list:
                self.error_msg = f"Board must be a list of LISTS of strings/nulls ({filename})"
                return None
            for val in board[i]:
                if val is not None and type(val) != str:
                    self.error_msg = f"Board must be a list of lists of STRINGS/NULLS ({filename})"
                    return None

        base_gm = gm_json['base_gm']
        if type(base_gm) != str or not any(gm.value == base_gm for gm in GameMode):
            self.error_msg = f"Base game mode must be a string representing a valid game mode ({filename})"
            return None
        difficulty = gm_json['difficulty']
        if type(difficulty) != str or not any(diff.name.capitalize() == difficulty for diff in Difficulty):
            self.error_msg = f"Difficulty must be a string representing a valid difficulty ({filename})"
            return None
        can_change_gm = gm_json['can_change_gm']
        if type(can_change_gm) != bool:
            self.error_msg = f"'Can change game mode' must be a boolean ({filename})"
            return None
        can_change_difficulty = gm_json['can_change_difficulty']
        if type(can_change_difficulty) != bool:
            self.error_msg = f"'Can change difficulty' must be a boolean ({filename})"
            return None

        if 'name' not in gm_json:
            name = '<unknown>'
        else:
            name = gm_json['name']

        return CustomGameMode(name, board_height, can_change_gm, can_change_difficulty,
                              GameMode(base_gm), Difficulty[difficulty.upper()], board)

    def get_all(self):
        try:
            game_mode_files = [f for f in os.listdir('custom_gm') if f.endswith('.json') and f not in self.game_modes]
        except FileNotFoundError:
            os.makedirs('custom_gm', exist_ok=True)
            return True

        success = True
        for file in game_mode_files:
            try:
                with open(os.path.join('custom_gm', file), 'r') as f:
                    parsed_gm = self.parse_gm_json(file, json.load(f))
                    if parsed_gm is None:
                        success = False
                        continue
                    self.game_modes[file[:-5]] = parsed_gm
            except (json.JSONDecodeError, IOError):
                self.error_msg = f'Error reading .json file {file}'
                success = False

        return success
