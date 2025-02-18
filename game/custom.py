import json
import random
import string
from datetime import datetime

from game.game_modes import GameModes, Difficulties


class CustomGameMode:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.selected_piece = None
        self.name = ''
        self.is_name_ok = False
        self.has_king = False
        self.is_focused = False
        self.board_y = 8
        self.base_game_mode = GameModes.SURVIVE_THE_LONGEST
        self.difficulty = Difficulties.NORMAL
        self.game_mode_disabled = False
        self.difficulty_disabled = False
        self.error_msg = None

    def reset(self):
        self.selected_piece = None
        self.error_msg = None
        self.board = [[None for _ in range(8)] for _ in range(self.board_y)]

    def get_piece_at(self, i, j):
        return self.board[i][j]

    def select_piece(self, piece):
        self.selected_piece = piece

    def unselect_piece(self):
        self.selected_piece = None

    def add_board_height(self):
        if self.board_y + 1 > 14:
            return
        self.board_y += 1
        self.board.insert(0, [None for _ in range(8)])

    def rm_board_height(self):
        if self.board_y - 1 < 6:
            return
        self.board_y -= 1
        self.board.pop(0)

    def clear_board(self):
        self.board = [[None for _ in range(8)] for _ in range(self.board_y)]

    def put_selected_piece(self, i, j):
        if self.selected_piece:
            self.board[i][j] = self.selected_piece

    def rm_piece(self, i, j):
        if self.selected_piece:
            self.selected_piece = None
        else:
            self.board[i][j] = None

    def check_for_king(self):
        for i in range(self.board_y):
            for j in range(8):
                if self.board[i][j] == 'K':
                    self.has_king = True
                    return
        self.has_king = False

    def check_name(self):
        if 20 >= len(self.name) >= 3:
            self.is_name_ok = True
        else:
            self.is_name_ok = False

    def save(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        filename = f'custom_gm/{timestamp}_{random_string}.json'

        data = {
            'name': self.name,
            'board_y': self.board_y,
            'gm_disabled': self.game_mode_disabled,
            'difficulty_disabled': self.difficulty_disabled,
            'base_gm': str(self.base_game_mode),
            'difficulty': str(self.difficulty),
            'board': self.board
        }
        try:
            with open(filename, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            self.error_msg = str(e)

    # def load(self, filename):
    #     filename = f'custom_gm/{filename}'
    #     try:
    #         with open(filename, 'r') as file:
    #             data = json.load(file)
    #         return data
    #     except FileNotFoundError:
    #         self.error_msg = f'File {filename} not found'
    #     except json.JSONDecodeError:
    #         self.error_msg = f'Error decoding JSON from {filename}'
    #     except Exception as e:
    #         self.error_msg = str(e)
    #     return None
