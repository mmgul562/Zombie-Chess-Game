from unittest import TestCase
from unittest.mock import patch, MagicMock

from game.game_modes import Gameplay, BlockTheBorder, BlockAndClear, GameMode, Difficulty, TurnResult


class TestGameMode(TestCase):
    def test_switch_game_mode(self):
        self.assertEqual(GameMode.SURVIVE_THE_LONGEST.switch(), GameMode.CAPTURE_THE_MOST)
        self.assertEqual(GameMode.CAPTURE_THE_MOST.switch(), GameMode.BLOCK_THE_BORDER)
        self.assertEqual(GameMode.BLOCK_THE_BORDER.switch(), GameMode.BLOCK_AND_CLEAR)
        self.assertEqual(GameMode.BLOCK_AND_CLEAR.switch(), GameMode.SURVIVE_THE_LONGEST)


class TestDifficulty(TestCase):
    def test_switch_difficulty(self):
        self.assertEqual(Difficulty.EASY.switch(), Difficulty.NORMAL)
        self.assertEqual(Difficulty.NORMAL.switch(), Difficulty.HARD)
        self.assertEqual(Difficulty.HARD.switch(), Difficulty.EXTREME)
        self.assertEqual(Difficulty.EXTREME.switch(), Difficulty.EASY)

    def test_roll_n_easy_difficulty(self):
        with patch('random.randint', return_value=50):
            self.assertEqual(Difficulty.EASY.roll_n(), 0)
        with patch('random.randint', return_value=51):
            self.assertEqual(Difficulty.EASY.roll_n(), 1)
        with patch('random.randint', return_value=100):
            self.assertEqual(Difficulty.EASY.roll_n(), 1)

    def test_roll_n_normal_difficulty(self):
        with patch('random.randint', return_value=30):
            self.assertEqual(Difficulty.NORMAL.roll_n(), 0)
        with patch('random.randint', return_value=31):
            self.assertEqual(Difficulty.NORMAL.roll_n(), 1)
        with patch('random.randint', return_value=90):
            self.assertEqual(Difficulty.NORMAL.roll_n(), 1)
        with patch('random.randint', return_value=91):
            self.assertEqual(Difficulty.NORMAL.roll_n(), 2)

    def test_roll_n_hard_difficulty(self):
        with patch('random.randint', return_value=20):
            self.assertEqual(Difficulty.HARD.roll_n(), 0)
        with patch('random.randint', return_value=21):
            self.assertEqual(Difficulty.HARD.roll_n(), 1)
        with patch('random.randint', return_value=60):
            self.assertEqual(Difficulty.HARD.roll_n(), 1)
        with patch('random.randint', return_value=61):
            self.assertEqual(Difficulty.HARD.roll_n(), 2)

    def test_roll_n_extreme_difficulty(self):
        with patch('random.randint', return_value=20):
            self.assertEqual(Difficulty.EXTREME.roll_n(), 0)
        with patch('random.randint', return_value=21):
            self.assertEqual(Difficulty.EXTREME.roll_n(), 1)
        with patch('random.randint', return_value=70):
            self.assertEqual(Difficulty.EXTREME.roll_n(), 1)
        with patch('random.randint', return_value=71):
            self.assertEqual(Difficulty.EXTREME.roll_n(), 2)


class TestGameplay(TestCase):
    def setUp(self):
        self.board_height = 10
        self.difficulty = Difficulty.NORMAL
        self.game = Gameplay(self.board_height, self.difficulty)

    def test_init_default_board(self):
        self.assertEqual(len(self.game.board), self.board_height)
        self.assertEqual(len(self.game.board[0]), 8)

        for i in range(8):
            self.assertEqual(self.game.board[self.board_height - 2][i], f'pp{i}')

        expected_last_row = ['pr8', 'pk9', 'pb10', 'pq11', 'pK12', 'pb13', 'pk14', 'pr15']
        self.assertEqual(self.game.board[self.board_height - 1], expected_last_row)

        self.assertEqual(self.game.selected_piece, None)
        self.assertEqual(self.game.turns, 1)
        self.assertEqual(self.game.moves, 0)
        self.assertEqual(self.game.zombies_captured, 0)
        self.assertEqual(self.game.pieces_left, 16)

    def test_init_custom_board(self):
        custom_board = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
            [None, None, None],
            ['pp0', 'pp1', 'pp2'],
            ['pr3', 'pK4', 'pr5']
        ]
        game = Gameplay(6, self.difficulty, custom_board)

        self.assertEqual(game.board, custom_board)
        self.assertIsNot(game.board, custom_board)

        self.assertIsNot(game.board[0], custom_board[0])

    def test_init_game_board_error(self):
        with self.assertRaises(ValueError):
            game = Gameplay(1, self.difficulty)

    def test_init_game_mode(self):
        game = Gameplay.init_game_mode(self.board_height, self.difficulty, GameMode.SURVIVE_THE_LONGEST)
        self.assertIsInstance(game, Gameplay)

        custom_board = [[None for _ in range(8)] for _ in range(self.board_height)]
        game = Gameplay.init_game_mode(self.board_height, self.difficulty, GameMode.CAPTURE_THE_MOST, custom_board)
        self.assertIsInstance(game, Gameplay)
        self.assertEqual(len(game.board), self.board_height)

    def test_get_piece_at(self):
        self.assertIsNone(self.game.get_piece_at(0, 0))

        pawn_row = self.board_height - 2
        self.assertEqual(self.game.get_piece_at(pawn_row, 0), f'pp0')

        piece_row = self.board_height - 1
        self.assertEqual(self.game.get_piece_at(piece_row, 4), 'pK12')

    def test_select_piece(self):
        pawn_row = self.board_height - 2
        self.assertTrue(self.game.select_piece(pawn_row, 3))
        self.assertEqual(self.game.selected_piece, (pawn_row, 3))

        self.assertFalse(self.game.select_piece(0, 0))
        self.assertEqual(self.game.selected_piece, (pawn_row, 3))

        self.game.last_moved_piece = 'pp3'
        self.assertFalse(self.game.select_piece(pawn_row, 3))

    def test_unselect_piece(self):
        pawn_row = self.board_height - 2
        self.game.select_piece(pawn_row, 3)
        self.assertEqual(self.game.selected_piece, (pawn_row, 3))

        self.game.unselect_piece()
        self.assertIsNone(self.game.selected_piece)

    def test_is_zombie(self):
        self.game.board[0][0] = 'zw'
        self.assertTrue(self.game.is_zombie(0, 0))

        piece_row = self.board_height - 1
        self.assertFalse(self.game.is_zombie(piece_row, 0))

        self.game.board[1][1] = None
        self.assertFalse(self.game.is_zombie(1, 1))

    def test_is_piece(self):
        piece_row = self.board_height - 1
        self.assertTrue(self.game.is_piece(piece_row, 4))

        self.assertFalse(self.game.is_piece(0, 0))

        self.game.board[0][0] = 'ze'
        self.assertFalse(self.game.is_piece(0, 0))

    def test_is_pawn(self):
        pawn_row = self.board_height - 2
        self.assertTrue(self.game.is_pawn(pawn_row, 3))

        piece_row = self.board_height - 1
        self.assertFalse(self.game.is_pawn(piece_row, 4))

        self.assertFalse(self.game.is_pawn(0, 0))

    def test_is_checkmate(self):
        piece_row = self.board_height - 1
        self.assertTrue(self.game.is_checkmate(piece_row, 4))

        self.assertFalse(self.game.is_checkmate(piece_row, 0))

        self.assertFalse(self.game.is_checkmate(0, 0))

    def test_skip_turn(self):
        initial_turns = self.game.turns

        self.game.move_wave = MagicMock(return_value=TurnResult.OK)

        result = self.game.skip_turn()

        self.assertEqual(self.game.turns, initial_turns + 1)
        self.assertIsNone(self.game.last_moved_piece)
        self.assertEqual(result, TurnResult.OK)
        self.game.move_wave.assert_called_once()

        self.game.move_wave = MagicMock(return_value=TurnResult.CHECKMATE)
        result = self.game.skip_turn()
        self.assertEqual(result, TurnResult.CHECKMATE)

    def test_promote_pawn(self):
        self.game.board[0][3] = 'pp7'

        self.assertTrue(self.game.promote_pawn(3, 'pq'))
        self.assertEqual(self.game.board[0][3], 'pq7')

        self.game.board[0][4] = 'pr8'
        self.assertFalse(self.game.promote_pawn(4, 'pq'))

        self.game.board[0][5] = None
        self.assertFalse(self.game.promote_pawn(5, 'pq'))

    def test_is_valid_move(self):
        self.game.board[5][3] = 'pp1'
        self.game.board[5][4] = 'pr2'
        self.game.board[5][5] = 'pk3'
        self.game.board[5][6] = 'pb4'
        self.game.board[5][7] = 'pq5'
        self.game.board[4][3] = 'pK6'

        self.game.check_pawn_move = MagicMock(return_value=True)
        self.game.check_rook_move = MagicMock(return_value=True)
        self.game.check_knight_move = MagicMock(return_value=True)
        self.game.check_bishop_move = MagicMock(return_value=True)
        self.game.check_queen_move = MagicMock(return_value=True)
        self.game.check_king_move = MagicMock(return_value=True)

        self.game.board[4][4] = 'pp7'
        self.assertFalse(self.game.is_valid_move(5, 3, 4, 4))

        self.assertFalse(self.game.is_valid_move(3, 3, 4, 4))

        self.game.board[4][4] = None
        self.assertTrue(self.game.is_valid_move(5, 3, 4, 4))
        self.game.check_pawn_move.assert_called_once_with(5, 3, 4, 4)

        self.game.check_pawn_move.reset_mock()
        self.assertTrue(self.game.is_valid_move(5, 4, 4, 4))
        self.game.check_rook_move.assert_called_once_with(5, 4, 4, 4)

        self.game.check_rook_move.reset_mock()
        self.assertTrue(self.game.is_valid_move(5, 5, 4, 4))
        self.game.check_knight_move.assert_called_once_with(5, 5, 4, 4)

        self.game.check_knight_move.reset_mock()
        self.assertTrue(self.game.is_valid_move(5, 6, 4, 4))
        self.game.check_bishop_move.assert_called_once_with(5, 6, 4, 4)

        self.game.check_bishop_move.reset_mock()
        self.assertTrue(self.game.is_valid_move(5, 7, 4, 4))
        self.game.check_queen_move.assert_called_once_with(5, 7, 4, 4)

        self.game.check_queen_move.reset_mock()
        self.assertTrue(self.game.is_valid_move(4, 3, 4, 4))
        self.game.check_king_move.assert_called_once_with(4, 3, 4, 4)

        self.game.board[3][3] = 'px9'
        self.assertFalse(self.game.is_valid_move(3, 3, 4, 4))

    def test_check_pawn_move(self):
        pawn_row = 5
        self.game.board[pawn_row][3] = 'pp1'

        self.assertTrue(self.game.check_pawn_move(pawn_row, 3, pawn_row - 1, 3))

        self.game.board[pawn_row - 1][3] = 'zw'
        self.assertFalse(self.game.check_pawn_move(pawn_row, 3, pawn_row - 1, 3))
        self.game.board[pawn_row - 1][3] = None

        pawn_start_row = self.board_height - 2
        self.game.board[pawn_start_row][4] = 'pp2'
        self.assertTrue(self.game.check_pawn_move(pawn_start_row, 4, pawn_start_row - 2, 4))

        self.game.board[pawn_start_row - 1][4] = 'zw'
        self.assertFalse(self.game.check_pawn_move(pawn_start_row, 4, pawn_start_row - 2, 4))
        self.game.board[pawn_start_row - 1][4] = None

        self.game.board[pawn_row - 1][4] = 'zw'
        self.assertTrue(self.game.check_pawn_move(pawn_row, 3, pawn_row - 1, 4))

        self.game.board[pawn_row - 1][4] = None
        self.assertFalse(self.game.check_pawn_move(pawn_row, 3, pawn_row - 1, 4))

        self.assertFalse(self.game.check_pawn_move(pawn_row, 3, pawn_row + 1, 3))

        self.assertFalse(self.game.check_pawn_move(pawn_row, 3, pawn_row - 2, 3))

    def test_check_rook_move(self):
        rook_row, rook_col = 5, 4
        self.game.board[rook_row][rook_col] = 'pr1'

        self.assertTrue(self.game.check_rook_move(rook_row, rook_col, rook_row, rook_col + 3))

        self.assertTrue(self.game.check_rook_move(rook_row, rook_col, rook_row - 3, rook_col))

        self.assertFalse(self.game.check_rook_move(rook_row, rook_col, rook_row - 2, rook_col + 2))

        self.game.board[rook_row][rook_col + 1] = 'zw'
        self.assertFalse(self.game.check_rook_move(rook_row, rook_col, rook_row, rook_col + 3))
        self.game.board[rook_row][rook_col + 1] = None

        self.game.board[rook_row - 1][rook_col] = 'ze'
        self.assertFalse(self.game.check_rook_move(rook_row, rook_col, rook_row - 3, rook_col))
        self.game.board[rook_row - 1][rook_col] = None

    def test_check_knight_move(self):
        self.assertTrue(Gameplay.check_knight_move(4, 4, 2, 5))
        self.assertTrue(Gameplay.check_knight_move(4, 4, 2, 3))
        self.assertTrue(Gameplay.check_knight_move(4, 4, 6, 5))
        self.assertTrue(Gameplay.check_knight_move(4, 4, 6, 3))
        self.assertTrue(Gameplay.check_knight_move(4, 4, 5, 6))
        self.assertTrue(Gameplay.check_knight_move(4, 4, 3, 6))
        self.assertTrue(Gameplay.check_knight_move(4, 4, 5, 2))
        self.assertTrue(Gameplay.check_knight_move(4, 4, 3, 2))

        self.assertFalse(Gameplay.check_knight_move(4, 4, 6, 6))
        self.assertFalse(Gameplay.check_knight_move(4, 4, 4, 6))
        self.assertFalse(Gameplay.check_knight_move(4, 4, 6, 4))
        self.assertFalse(Gameplay.check_knight_move(4, 4, 3, 4))
        self.assertFalse(Gameplay.check_knight_move(4, 4, 1, 1))

    def test_check_bishop_move(self):
        bishop_row, bishop_col = 5, 5
        self.game.board[bishop_row][bishop_col] = 'pb1'

        self.assertTrue(self.game.check_bishop_move(bishop_row, bishop_col, bishop_row - 2, bishop_col - 2))
        self.assertTrue(self.game.check_bishop_move(bishop_row, bishop_col, bishop_row - 2, bishop_col + 2))
        self.assertTrue(self.game.check_bishop_move(bishop_row, bishop_col, bishop_row + 2, bishop_col - 2))
        self.assertTrue(self.game.check_bishop_move(bishop_row, bishop_col, bishop_row + 2, bishop_col + 2))

        self.assertFalse(self.game.check_bishop_move(bishop_row, bishop_col, bishop_row, bishop_col + 2))
        self.assertFalse(self.game.check_bishop_move(bishop_row, bishop_col, bishop_row - 2, bishop_col))

        self.assertFalse(self.game.check_bishop_move(bishop_row, bishop_col, bishop_row - 1, bishop_col + 2))

        self.game.board[bishop_row - 1][bishop_col - 1] = 'zw'
        self.assertFalse(self.game.check_bishop_move(bishop_row, bishop_col, bishop_row - 2, bishop_col - 2))
        self.game.board[bishop_row - 1][bishop_col - 1] = None

    def test_check_queen_move(self):
        queen_row, queen_col = 5, 6
        self.game.board[queen_row][queen_col] = 'pq1'

        self.game.check_rook_move = MagicMock(return_value=False)
        self.game.check_bishop_move = MagicMock(return_value=False)

        self.assertFalse(self.game.check_queen_move(queen_row, queen_col, queen_row - 2, queen_col + 1))
        self.game.check_rook_move.assert_called_once_with(queen_row, queen_col, queen_row - 2, queen_col + 1)
        self.game.check_bishop_move.assert_called_once_with(queen_row, queen_col, queen_row - 2, queen_col + 1)

        self.game.check_rook_move.reset_mock()
        self.game.check_bishop_move.reset_mock()
        self.game.check_rook_move.return_value = True

        self.assertTrue(self.game.check_queen_move(queen_row, queen_col, queen_row - 2, queen_col))
        self.game.check_rook_move.assert_called_once_with(queen_row, queen_col, queen_row - 2, queen_col)
        self.game.check_bishop_move.assert_not_called()

        self.game.check_rook_move.reset_mock()
        self.game.check_rook_move.return_value = False
        self.game.check_bishop_move.return_value = True

        self.assertTrue(self.game.check_queen_move(queen_row, queen_col, queen_row - 2, queen_col + 2))
        self.game.check_rook_move.assert_called_once_with(queen_row, queen_col, queen_row - 2, queen_col + 2)
        self.game.check_bishop_move.assert_called_once_with(queen_row, queen_col, queen_row - 2, queen_col + 2)

    def test_check_king_move(self):
        king_row, king_col = 4, 4

        self.assertTrue(Gameplay.check_king_move(king_row, king_col, king_row - 1, king_col))
        self.assertTrue(Gameplay.check_king_move(king_row, king_col, king_row + 1, king_col))
        self.assertTrue(Gameplay.check_king_move(king_row, king_col, king_row, king_col - 1))
        self.assertTrue(Gameplay.check_king_move(king_row, king_col, king_row, king_col + 1))

        self.assertTrue(Gameplay.check_king_move(king_row, king_col, king_row - 1, king_col - 1))
        self.assertTrue(Gameplay.check_king_move(king_row, king_col, king_row - 1, king_col + 1))
        self.assertTrue(Gameplay.check_king_move(king_row, king_col, king_row + 1, king_col - 1))
        self.assertTrue(Gameplay.check_king_move(king_row, king_col, king_row + 1, king_col + 1))

        self.assertFalse(Gameplay.check_king_move(king_row, king_col, king_row - 2, king_col))
        self.assertFalse(Gameplay.check_king_move(king_row, king_col, king_row, king_col + 2))
        self.assertFalse(Gameplay.check_king_move(king_row, king_col, king_row - 2, king_col - 2))

    def test_move_piece_valid_move(self):
        self.game.is_valid_move = MagicMock(return_value=True)
        self.game.is_zombie = MagicMock(return_value=False)
        self.game.move_wave = MagicMock(return_value=TurnResult.OK)
        pawn_row = self.board_height - 2
        self.game.board[pawn_row][0] = 'pp0'

        result = self.game.move_piece(pawn_row, 0, pawn_row - 1, 0)

        self.assertEqual(result, TurnResult.OK)
        self.assertEqual(self.game.board[pawn_row - 1][0], 'pp0')
        self.assertIsNone(self.game.board[pawn_row][0])
        self.assertEqual(self.game.turns, 2)
        self.assertEqual(self.game.moves, 1)
        self.game.is_valid_move.assert_called_once_with(pawn_row, 0, pawn_row - 1, 0)
        self.game.move_wave.assert_called_once()

    def test_move_piece_capturing_zombie(self):
        self.game.is_valid_move = MagicMock(return_value=True)
        self.game.is_zombie = MagicMock(return_value=True)
        self.game.move_wave = MagicMock(return_value=TurnResult.OK)
        pawn_row = self.board_height - 2
        self.game.board[pawn_row][0] = 'pp0'
        self.game.board[pawn_row - 1][1] = 'zw'

        result = self.game.move_piece(pawn_row, 0, pawn_row - 1, 1)

        self.assertEqual(result, TurnResult.OK)
        self.assertEqual(self.game.board[pawn_row - 1][1], 'pp0')
        self.assertIsNone(self.game.board[pawn_row][0])
        self.assertEqual(self.game.zombies_captured, 1)
        self.assertEqual(self.game.turns, 2)
        self.assertEqual(self.game.moves, 1)

    def test_move_piece_exploding_zombie(self):
        self.game.is_valid_move = MagicMock(return_value=True)
        self.game.is_zombie = MagicMock(return_value=True)
        self.game.activate_exploding_zombie = MagicMock()
        self.game.move_wave = MagicMock(return_value=TurnResult.OK)
        pawn_row = self.board_height - 2
        self.game.board[pawn_row][0] = 'pp0'
        self.game.board[pawn_row - 1][1] = 'ze'

        result = self.game.move_piece(pawn_row, 0, pawn_row - 1, 1)

        self.assertEqual(result, TurnResult.OK)
        self.assertEqual(self.game.board[pawn_row - 1][1], 'pp0')
        self.assertIsNone(self.game.board[pawn_row][0])
        self.assertEqual(self.game.zombies_captured, 1)
        self.game.activate_exploding_zombie.assert_called_once_with(pawn_row - 1, 1)

    def test_move_piece_checkmate(self):
        self.game.is_valid_move = MagicMock(return_value=True)
        self.game.is_zombie = MagicMock(return_value=False)
        self.game.move_wave = MagicMock(return_value=TurnResult.CHECKMATE)
        pawn_row = self.board_height - 2
        self.game.board[pawn_row][0] = 'pp0'

        result = self.game.move_piece(pawn_row, 0, pawn_row - 1, 0)

        self.assertEqual(result, TurnResult.CHECKMATE)

    def test_move_piece_win(self):
        self.game.is_valid_move = MagicMock(return_value=True)
        self.game.is_zombie = MagicMock(return_value=False)
        self.game.move_wave = MagicMock(return_value=TurnResult.WIN)
        pawn_row = self.board_height - 2
        self.game.board[pawn_row][0] = 'pp0'

        result = self.game.move_piece(pawn_row, 0, pawn_row - 1, 0)

        self.assertEqual(result, TurnResult.WIN)

    def test_move_piece_rook_castling_update(self):
        self.game.is_valid_move = MagicMock(return_value=True)
        self.game.is_zombie = MagicMock(return_value=False)
        self.game.move_wave = MagicMock(return_value=TurnResult.OK)
        piece_row = self.board_height - 1
        self.game.board[piece_row][0] = 'pr8'
        initial_castling = self.game.castling_combinations.copy()

        result = self.game.move_piece(piece_row, 0, piece_row - 1, 0)

        self.assertEqual(result, TurnResult.OK)
        self.assertEqual(len(self.game.castling_combinations), 2)
        self.assertNotIn(('pK12', 'pr8'), self.game.castling_combinations)
        self.assertNotIn(('pr8', 'pK12'), self.game.castling_combinations)
        self.assertNotEqual(initial_castling, self.game.castling_combinations)

    def test_move_piece_king_castling_update(self):
        self.game.is_valid_move = MagicMock(return_value=True)
        self.game.is_zombie = MagicMock(return_value=False)
        self.game.move_wave = MagicMock(return_value=TurnResult.OK)
        piece_row = self.board_height - 1
        self.game.board[piece_row][4] = 'pK12'

        result = self.game.move_piece(piece_row, 4, piece_row - 1, 4)

        self.assertEqual(result, TurnResult.OK)
        self.assertIsNone(self.game.castling_combinations)

    def test_move_piece_no_extreme_difficulty(self):
        self.game.difficulty = Difficulty.NORMAL
        self.game.is_valid_move = MagicMock(return_value=True)
        self.game.is_zombie = MagicMock(return_value=False)
        self.game.move_wave = MagicMock(return_value=TurnResult.OK)
        pawn_row = self.board_height - 2
        self.game.board[pawn_row][0] = 'pp0'

        result = self.game.move_piece(pawn_row, 0, pawn_row - 1, 0)

        self.assertEqual(result, TurnResult.OK)
        self.assertIsNone(self.game.last_moved_piece)

    def test_move_piece_extreme_difficulty_last_moved(self):
        self.game.difficulty = Difficulty.EXTREME
        self.game.is_valid_move = MagicMock(return_value=True)
        self.game.is_zombie = MagicMock(return_value=False)
        self.game.move_wave = MagicMock(return_value=TurnResult.OK)
        pawn_row = self.board_height - 2
        self.game.board[pawn_row][0] = 'pp0'

        result = self.game.move_piece(pawn_row, 0, pawn_row - 1, 0)

        self.assertEqual(result, TurnResult.OK)
        self.assertEqual(self.game.last_moved_piece, 'pp0')

    def test_move_piece_castling(self):
        self.game.is_valid_move = MagicMock(return_value=False)
        self.game.check_castling_move = MagicMock(return_value=(2, 3, 8))  # Sample castling move data
        self.game.move_wave = MagicMock(return_value=TurnResult.OK)
        piece_row = self.board_height - 1
        self.game.board[piece_row][4] = 'pK12'
        self.game.board[piece_row][0] = 'pr8'

        result = self.game.move_piece(piece_row, 4, piece_row, 0)

        self.assertEqual(result, TurnResult.OK)
        self.assertIsNone(self.game.board[piece_row][4])
        self.assertIsNone(self.game.board[piece_row][0])
        self.assertEqual(self.game.board[piece_row][2], 'pK12')
        self.assertEqual(self.game.board[piece_row][3], 'pr8')
        self.assertIsNone(self.game.castling_combinations)
        self.assertEqual(self.game.turns, 2)
        self.assertEqual(self.game.moves, 1)

    def test_move_piece_invalid_move(self):
        self.game.is_valid_move = MagicMock(return_value=False)
        self.game.check_castling_move = MagicMock(return_value=None)

        result = self.game.move_piece(8, 0, 7, 0)

        self.assertEqual(result, TurnResult.WRONG)
        self.assertEqual(self.game.turns, 1)
        self.assertEqual(self.game.moves, 0)

    @patch('random.sample', return_value=[0, 3, 5])
    @patch('random.randint', side_effect=[15, 40, 60])
    def test_create_new_zombies(self, mock_randint, mock_sample):
        self.game.is_checkmate = MagicMock(return_value=False)

        result = self.game.create_new_zombies(3)

        self.assertEqual(result, TurnResult.OK)
        self.assertEqual(self.game.board[0][0], 'zs')
        self.assertEqual(self.game.board[0][3], 'zi')
        self.assertEqual(self.game.board[0][5], 'zw')
        mock_sample.assert_called_once_with(range(8), 3)
        self.assertEqual(mock_randint.call_count, 3)

    @patch('random.sample', return_value=[0, 3, 5])
    def test_create_new_zombies_checkmate(self, mock_sample):
        self.game.is_checkmate = MagicMock(side_effect=[True, False, False])

        result = self.game.create_new_zombies(3)

        self.assertEqual(result, TurnResult.CHECKMATE)
        self.game.is_checkmate.assert_called_once_with(0, 0)

    def test_move_wave(self):
        self.game.move_walker = MagicMock(return_value=(TurnResult.OK, (5, 3)))
        self.game.move_stomper = MagicMock(return_value=(TurnResult.OK, (6, 4)))
        self.game.move_exploding = MagicMock(return_value=(TurnResult.OK, (7, 5)))
        self.game.move_infected = MagicMock(return_value=(TurnResult.OK, (8, 6)))
        self.game.create_new_zombies = MagicMock(return_value=TurnResult.OK)
        self.game.is_piece = MagicMock(return_value=False)

        self.game.board[5][3] = 'zw'
        self.game.board[6][4] = 'zs'
        self.game.board[7][5] = 'ze'
        self.game.board[8][6] = 'zi'

        result = self.game.move_wave()

        self.assertEqual(result, TurnResult.OK)
        self.game.move_walker.assert_called_once_with(5, 3)
        self.game.move_stomper.assert_called_once_with(6, 4)
        self.game.move_exploding.assert_called_once_with(7, 5)
        self.game.move_infected.assert_called_once_with(8, 6)
        self.game.create_new_zombies.assert_called_once()

    def test_move_wave_checkmate(self):
        self.game.move_walker = MagicMock(return_value=(TurnResult.CHECKMATE, (5, 3)))
        self.game.is_piece = MagicMock(return_value=False)

        self.game.board[5][3] = 'zw'

        result = self.game.move_wave()

        self.assertEqual(result, TurnResult.CHECKMATE)
        self.game.move_walker.assert_called_once_with(5, 3)


class TestBlockTheBorderGameMode(TestCase):
    def setUp(self):
        self.board_height = 10
        self.difficulty = Difficulty.NORMAL
        self.game = BlockTheBorder(self.board_height, self.difficulty)

    def test_get_free_border_spots_all_free(self):
        for i in range(8):
            self.game.board[0][i] = None
        self.game.is_zombie = MagicMock(return_value=False)

        free_spots, zombie_spots = self.game.get_free_border_spots()

        self.assertEqual(free_spots, list(range(8)))
        self.assertEqual(zombie_spots, [])

    def test_get_free_border_spots_mixed(self):
        self.game.board[0][0] = 'zw'
        self.game.board[0][1] = None
        self.game.board[0][2] = 'zs'
        self.game.board[0][3] = None
        self.game.board[0][4] = 'pp0'
        self.game.board[0][5] = None
        self.game.board[0][6] = 'zi'
        self.game.board[0][7] = None

        def is_zombie_side_effect(row, col):
            if row == 0 and self.game.board[0][col] in ['zw', 'zs', 'zi']:
                return True
            return False

        self.game.is_zombie = MagicMock(side_effect=is_zombie_side_effect)

        free_spots, zombie_spots = self.game.get_free_border_spots()

        self.assertEqual(free_spots, [1, 3, 5, 7])
        self.assertEqual(zombie_spots, [0, 2, 6])

    def test_get_free_border_spots_all_occupied(self):
        for i in range(8):
            if i % 2 == 0:
                self.game.board[0][i] = 'zw'
            else:
                self.game.board[0][i] = 'pp0'

        def is_zombie_side_effect(row, col):
            if row == 0 and col % 2 == 0:
                return True
            return False

        self.game.is_zombie = MagicMock(side_effect=is_zombie_side_effect)

        free_spots, zombie_spots = self.game.get_free_border_spots()

        self.assertEqual(free_spots, [])
        self.assertEqual(zombie_spots, [0, 2, 4, 6])

    def test_move_wave_captured_piece(self):
        self.game.is_piece = MagicMock(return_value=False)
        self.game.move_walker = MagicMock(return_value=(TurnResult.CAPTURED, (5, 3)))
        self.game.create_new_zombies = MagicMock(return_value=TurnResult.OK)
        self.game.board[5][3] = 'zw'

        result = self.game.move_wave()

        self.assertEqual(result, TurnResult.OK)
        self.assertEqual(self.game.pieces_left, 15)

    def test_move_wave_checkmate_from_zombie(self):
        self.game.is_piece = MagicMock(return_value=False)
        self.game.move_walker = MagicMock(return_value=(TurnResult.CHECKMATE, (5, 3)))
        self.game.board[5][3] = 'zw'

        result = self.game.move_wave()

        self.assertEqual(result, TurnResult.CHECKMATE)
        self.game.move_walker.assert_called_once_with(5, 3)

    def test_move_wave_checkmate_from_pieces_left(self):
        self.game.is_piece = MagicMock(return_value=False)
        self.game.move_walker = MagicMock(return_value=(TurnResult.CAPTURED, (5, 3)))
        self.game.board[5][3] = 'zw'
        self.game.pieces_left = 8

        result = self.game.move_wave()

        self.assertEqual(result, TurnResult.CHECKMATE)
        self.assertEqual(self.game.pieces_left, 7)

    @patch('random.sample', return_value=[0, 2])
    @patch('random.randint', side_effect=[15, 60])
    def test_create_new_zombies_standard(self, mock_randint, mock_sample):
        self.game.get_free_border_spots = MagicMock(return_value=([0, 1, 2, 3], []))
        mock_sample.return_value = [0, 2]
        mock_randint.side_effect = [15, 60]

        result = self.game.create_new_zombies(2)

        self.assertEqual(result, TurnResult.OK)
        self.assertEqual(self.game.board[0][0], 'zs')
        self.assertEqual(self.game.board[0][2], 'zw')

    def test_create_new_zombies_win(self):
        self.game.get_free_border_spots = MagicMock(return_value=([], []))
        result = self.game.create_new_zombies(2)
        self.assertEqual(result, TurnResult.WIN)

    def test_create_new_zombies_no_free_spots(self):
        self.game.get_free_border_spots = MagicMock(return_value=([], [4, 5]))
        result = self.game.create_new_zombies(2)
        self.assertEqual(result, TurnResult.OK)


class TestBlockAndClearGameMode(TestCase):
    def setUp(self):
        self.board_height = 10
        self.difficulty = Difficulty.NORMAL
        self.game = BlockAndClear(self.board_height, self.difficulty)

    def test_is_board_clear_empty(self):
        self.game.is_zombie = MagicMock(return_value=False)

        result = self.game.is_board_clear()

        self.assertTrue(result)
        self.assertEqual(self.game.is_zombie.call_count, self.board_height * 8)

    def test_is_board_clear_with_zombies(self):
        def is_zombie_side_effect(row, col):
            return row == 5 and col == 3
        self.game.is_zombie = MagicMock(side_effect=is_zombie_side_effect)

        result = self.game.is_board_clear()

        self.assertFalse(result)

    @patch('random.sample', return_value=[0, 2])
    @patch('random.randint', side_effect=[15, 40])
    def test_create_new_zombies_standard(self, mock_randint, mock_sample):
        self.game.get_free_border_spots = MagicMock(return_value=([0, 1, 2, 3], []))
        self.game.is_board_clear = MagicMock(return_value=False)

        result = self.game.create_new_zombies(2)

        self.assertEqual(result, TurnResult.OK)
        self.assertEqual(self.game.board[0][0], 'zs')
        self.assertEqual(self.game.board[0][2], 'zi')

    def test_create_new_zombies_win(self):
        self.game.get_free_border_spots = MagicMock(return_value=([], []))
        self.game.is_board_clear = MagicMock(return_value=True)

        result = self.game.create_new_zombies(2)

        self.assertEqual(result, TurnResult.WIN)

    def test_create_new_zombies_zombies_exist(self):
        self.game.get_free_border_spots = MagicMock(return_value=([], []))
        self.game.is_board_clear = MagicMock(return_value=False)

        result = self.game.create_new_zombies(2)

        self.assertEqual(result, TurnResult.OK)
