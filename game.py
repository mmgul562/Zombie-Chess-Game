import os
import pygame


class GameBoard:
    def __init__(self):
        self.board = [
            ['z' for _ in range(8)],
            [None for _ in range(8)],
            [None for _ in range(8)],
            [None for _ in range(8)],
            [None for _ in range(8)],
            [None for _ in range(8)],
            ['p' for _ in range(8)],
            ['r', 'k', 'b', 'q', 'K', 'b', 'k', 'r']
        ]
        self.selected_piece = None
        self.available_moves = []

    def get_piece_at(self, row, col):
        return self.board[row][col]

    def is_valid_move(self, start_row, start_col, end_row, end_col):
        piece = self.board[start_row][start_col]

        if piece == 'p':
            self.check_pawn_move(start_row, start_col, end_row, end_col)
        elif piece == 'r':
            self.check_rook_move(start_row, start_col, end_row, end_col)
        elif piece == 'k':
            self.check_knight_move(start_row, start_col, end_row, end_col)
        elif piece == 'b':
            self.check_bishop_move(start_row, start_col, end_row, end_col)
        elif piece == 'q':
            self.check_queen_move(start_row, start_col, end_row, end_col)
        elif piece == 'K':
            self.check_king_move(start_row, start_col, end_row, end_col)

    def move_piece(self, start_row, start_col, end_row, end_col):
        if self.is_valid_move(start_row, start_col, end_row, end_col):
            self.board[end_row][end_col] = self.board[start_row][start_col]
            self.board[start_row][start_col] = None
            # opponent's move
            return True
        return False

    @staticmethod
    def check_pawn_move(start_row, start_col, end_row, end_col):
        pass

    @staticmethod
    def check_rook_move(start_row, start_col, end_row, end_col):
        pass

    @staticmethod
    def check_knight_move(start_row, start_col, end_row, end_col):
        pass

    @staticmethod
    def check_bishop_move(start_row, start_col, end_row, end_col):
        pass

    @staticmethod
    def check_queen_move(start_row, start_col, end_row, end_col):
        pass

    @staticmethod
    def check_king_move(start_row, start_col, end_row, end_col):
        pass


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption('Pawnbies')
        self.board = GameBoard()
        self.square_size = 100
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
        colors = [(255, 206, 158), (209, 139, 71)]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                pygame.draw.rect(self.screen, color,
                                 (col * self.square_size, row * self.square_size,
                                  self.square_size, self.square_size))

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece_at(row, col)
                if piece and piece in self.piece_images:
                    self.screen.blit(self.piece_images[piece],
                                     (col * self.square_size + 5, row * self.square_size + 5))

    def run(self):
        running = True
        selected_piece = None
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    col = event.pos[0] // self.square_size
                    row = event.pos[1] // self.square_size

                    if selected_piece:
                        start_row, start_col = selected_piece
                        if self.board.move_piece(start_row, start_col, row, col):
                            selected_piece = None
                        else:
                            selected_piece = None
                    else:
                        piece = self.board.get_piece_at(row, col)
                        if piece and piece[0] != 'z':
                            selected_piece = (row, col)

            self.draw_board()
            self.draw_pieces()
            clock.tick(60)
            pygame.display.flip()

        pygame.quit()
