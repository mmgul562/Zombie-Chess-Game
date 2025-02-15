class CustomGameMode:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.selected_piece = None
        self.board_y = 8
        self.game_mode_enabled = True
        self.difficulty_enabled = True

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

    def has_king(self):
        for i in range(self.board_y):
            for j in range(8):
                if self.board[i][j] == 'K':
                    return True
        return False
