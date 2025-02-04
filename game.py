import os
import random
import pygame


class Checkmate(Exception):
    def __init__(self):
        super().__init__()


class Win(Exception):
    def __init__(self):
        super().__init__()


class Gameplay:
    def __init__(self, board_y, difficulty, game_mode):
        self.board = [
            [None for _ in range(8)] for _ in range(board_y - 2)
        ]
        self.board.append([f'p{i}' for i in range(8)])
        self.board.append(['r0', 'k0', 'b0', 'q', 'K', 'b1', 'k1', 'r1'])
        self.selected_piece = None
        self.last_moved_piece = None
        self.board_y = board_y
        self.difficulty = difficulty
        self.game_mode = game_mode

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

    def is_valid_move(self, start_row, start_col, end_row, end_col):
        if self.board[end_row][end_col] != 'z' and self.board[end_row][end_col] is not None:
            return False

        piece = (self.board[start_row][start_col])[0]
        if piece == 'z' or piece is None:
            return False
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
            self.move_wave()
            self.last_moved_piece = self.board[end_row][end_col]
            return True
        return False

    def move_wave(self):
        for i in reversed(range(self.board_y)):
            for j in reversed(range(8)):
                if self.board[i][j] != 'z':
                    continue

                move_to = self.check_zombie_collision(i, j)
                if move_to is None:
                    continue
                elif move_to[0] == 'd':
                    self.check_checkmate(i + 1, j)
                    self.board[i + 1][j] = 'z'
                    if move_to[1] == 'm':
                        self.board[i][j] = None
                elif move_to[0] == 'r':
                    self.check_checkmate(i, j + 1)
                    self.board[i][j + 1] = 'z'
                    if move_to[1] == 'm':
                        self.board[i][j] = None
                elif move_to[0] == 'l':
                    self.check_checkmate(i, j - 1)
                    self.board[i][j - 1] = 'z'
                    if move_to[1] == 'm':
                        self.board[i][j] = None

        self.create_new_zombies(random.randint(0, self.difficulty))

    def create_new_zombies(self, n):
        if self.game_mode == 'highest_score':
            new_spots = random.sample(range(8), n)
            for i in new_spots:
                if self.board[0][i] == 'K':
                    raise Checkmate()
                self.board[0][i] = 'z'
        elif self.game_mode[:5] == 'block':
            new_spots = self.get_free_border_spots()
            if not new_spots:
                if self.game_mode == 'block':
                    raise Win()
                else:
                    if self.is_board_clear():
                        raise Win()
            new_spots = random.sample(new_spots, n)
            for i in new_spots:
                self.board[0][i] = 'z'

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

    def check_checkmate(self, i, j):
        if self.board[i][j] == 'K':
            raise Checkmate()

    def is_board_clear(self):
        for i in range(self.board_y):
            for j in range(8):
                if self.board[i][j] == 'z':
                    return False
        return True

    def get_free_border_spots(self):
        free_spots = []
        for i in range(8):
            if self.board[0][i] is None:
                free_spots.append(i)
        return free_spots

    def skip_turn(self):
        self.last_moved_piece = None
        self.move_wave()

    def check_pawn_move(self, start_row, start_col, end_row, end_col):
        if end_row >= start_row:
            return False

        move_direction = -1
        # straight move
        if start_col == end_col:
            if start_row + move_direction == end_row:
                return self.board[end_row][end_col] is None
            elif start_row == len(self.board) - 2 and start_row + (2 * move_direction) == end_row:
                return (self.board[end_row][end_col] is None and
                        self.board[start_row + move_direction][end_col] is None)
            return False

        # diagonal capture
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


class Game:
    def __init__(self, board_y, difficulty='easy', game_mode='highest_score'):
        pygame.init()
        self.board_y = board_y
        self.screen = pygame.display.set_mode((800, board_y * 100))
        pygame.display.set_caption('Pawnbies')
        self.gameplay = Gameplay(board_y, difficulty, game_mode)
        self.square_size = 100
        self.light_square = (255, 206, 158)
        self.dark_square = (209, 139, 71)
        self.highlight_color = (124, 252, 0, 128)
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

    def draw_board(self):
        colors = [self.light_square, self.dark_square]
        for row in range(self.board_y):
            for col in range(8):
                color = colors[(row + col) % 2]
                pygame.draw.rect(self.screen, color,
                                 (col * self.square_size, row * self.square_size,
                                  self.square_size, self.square_size))
                if self.gameplay.is_selected(row, col):
                    self.screen.blit(self.highlight_surface,
                                     (col * self.square_size, row * self.square_size))

    def draw_pieces(self):
        for row in range(self.board_y):
            for col in range(8):
                piece = self.gameplay.get_piece_at(row, col)
                if piece and piece[0] in self.piece_images:
                    self.screen.blit(self.piece_images[piece[0]],
                                     (col * self.square_size + 5, row * self.square_size + 5))

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_RIGHT:
                        self.gameplay.unselect_piece()
                    elif event.button == pygame.BUTTON_MIDDLE:
                        # skip turn
                        self.gameplay.skip_turn()
                    else:
                        col = event.pos[0] // self.square_size
                        row = event.pos[1] // self.square_size

                        if self.gameplay.selected_piece:
                            start_row, start_col = self.gameplay.selected_piece
                            piece_moved = None
                            try:
                                piece_moved = self.gameplay.move_piece(start_row, start_col, row, col)
                            except (Checkmate, Win):
                                running = False
                            if piece_moved:
                                self.gameplay.unselect_piece()
                            else:
                                if self.gameplay.get_piece_at(row, col) and (row, col) != (start_row, start_col):
                                    self.gameplay.select_piece(row, col)
                                else:
                                    self.gameplay.unselect_piece()
                        else:
                            self.gameplay.select_piece(row, col)

            self.draw_board()
            self.draw_pieces()
            clock.tick(60)
            pygame.display.flip()

        pygame.quit()
