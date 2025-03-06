import json
from unittest import TestCase
from unittest.mock import patch, mock_open, MagicMock

from game.custom import CustomGameMode, CustomGameModeLoader, CustomGameModeCreator
from game.game_modes import GameMode, Difficulty


class TestCustomGameMode(TestCase):
    def test_init_default_values(self):
        game_mode = CustomGameMode()
        self.assertEqual(game_mode.name, '')
        self.assertEqual(game_mode.board_height, 8)
        self.assertTrue(game_mode.can_change_gm)
        self.assertTrue(game_mode.can_change_difficulty)
        self.assertEqual(game_mode.base_gm, GameMode.CLEAR_THE_BOARD)
        self.assertEqual(game_mode.difficulty, Difficulty.EASY)
        self.assertIsNone(game_mode.board)

    def test_init_custom_values(self):
        board = [[None for _ in range(8)] for _ in range(10)]
        game_mode = CustomGameMode(
            name='Custom Mode',
            board_height=10,
            can_change_gm=False,
            can_change_difficulty=False,
            base_gm=GameMode.CAPTURE_THE_MOST,
            difficulty=Difficulty.HARD,
            board=board
        )
        self.assertEqual(game_mode.name, 'Custom Mode')
        self.assertEqual(game_mode.board_height, 10)
        self.assertFalse(game_mode.can_change_gm)
        self.assertFalse(game_mode.can_change_difficulty)
        self.assertEqual(game_mode.base_gm, GameMode.CAPTURE_THE_MOST)
        self.assertEqual(game_mode.difficulty, Difficulty.HARD)
        self.assertEqual(game_mode.board, board)


class TestCustomGameModeCreator(TestCase):
    def setUp(self):
        self.creator = CustomGameModeCreator()

    def test_init(self):
        self.assertIsInstance(self.creator.game, CustomGameMode)
        self.assertEqual(len(self.creator.game.board), 8)
        self.assertEqual(len(self.creator.game.board[0]), 8)
        self.assertFalse(self.creator.is_name_ok)
        self.assertFalse(self.creator.has_king)
        self.assertFalse(self.creator.input_focused)
        self.assertIsNone(self.creator.selected_piece)
        self.assertIsNone(self.creator.error_msg)

    def test_reset(self):
        self.creator.game.can_change_gm = False
        self.creator.game.can_change_difficulty = False
        self.creator.selected_piece = 'pK'
        self.creator.error_msg = 'Some error'

        self.creator.reset()

        self.assertTrue(self.creator.game.can_change_gm)
        self.assertTrue(self.creator.game.can_change_difficulty)
        self.assertIsNone(self.creator.selected_piece)
        self.assertIsNone(self.creator.error_msg)

    def test_get_piece_at(self):
        self.creator.game.board[3][4] = 'pK'

        self.assertEqual(self.creator.get_piece_at(3, 4), 'pK')
        self.assertIsNone(self.creator.get_piece_at(0, 0))

    def test_select_unselect_piece(self):
        self.creator.select_piece('pq')
        self.assertEqual(self.creator.selected_piece, 'pq')

        self.creator.unselect_piece()
        self.assertIsNone(self.creator.selected_piece)

    def test_add_board_height(self):
        initial_height = self.creator.game.board_height
        initial_board_len = len(self.creator.game.board)

        self.creator.add_board_height()

        self.assertEqual(self.creator.game.board_height, initial_height + 1)
        self.assertEqual(len(self.creator.game.board), initial_board_len + 1)

        self.creator.game.board_height = 18
        self.creator.add_board_height()
        self.assertEqual(self.creator.game.board_height, 18)

    def test_rm_board_height(self):
        self.creator.game.board_height = 10
        self.creator.game.board = [[None for _ in range(8)] for _ in range(10)]

        initial_height = self.creator.game.board_height
        initial_board_len = len(self.creator.game.board)

        self.creator.rm_board_height()

        self.assertEqual(self.creator.game.board_height, initial_height - 1)
        self.assertEqual(len(self.creator.game.board), initial_board_len - 1)

        self.creator.game.board_height = 6
        self.creator.rm_board_height()
        self.assertEqual(self.creator.game.board_height, 6)

    def test_clear_board(self):
        self.creator.game.board[0][0] = 'pK'
        self.creator.game.board[1][1] = 'pq'

        self.creator.clear_board()

        for row in self.creator.game.board:
            for cell in row:
                self.assertIsNone(cell)

    def test_put_selected_piece(self):
        self.creator.selected_piece = 'pp'
        self.creator.put_selected_piece(2, 3)
        self.assertEqual(self.creator.game.board[2][3], 'pp')

        self.creator.selected_piece = None
        self.creator.put_selected_piece(1, 1)
        self.assertIsNone(self.creator.game.board[1][1])

    def test_rm_piece(self):
        self.creator.game.board[4][5] = 'pp'
        self.creator.rm_piece(4, 5)
        self.assertIsNone(self.creator.game.board[4][5])

    def test_check_for_king(self):
        self.creator.check_for_king()
        self.assertFalse(self.creator.has_king)

        self.creator.game.board[3][3] = 'pK'
        self.creator.check_for_king()
        self.assertTrue(self.creator.has_king)

    def test_check_name(self):
        self.creator.game.name = 'ab'
        self.creator.check_name()
        self.assertFalse(self.creator.is_name_ok)

        self.creator.game.name = 'Valid Name'
        self.creator.check_name()
        self.assertTrue(self.creator.is_name_ok)

        self.creator.game.name = 'x' * 21
        self.creator.check_name()
        self.assertFalse(self.creator.is_name_ok)

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('random.choices', return_value=['a', 'b', 'c', 'd', '1', '2', '3', '4', '5', '6'])
    def test_save(self, mock_random_choices, mock_json_dump, mock_file_open):
        self.creator.game.board[0][0] = 'pK'
        self.creator.game.board[0][1] = 'pq'
        self.creator.game.name = 'Test Mode'

        self.creator.save()

        mock_file_open.assert_called_once_with('custom_gm/abcd123456.json', 'w')

        args, _ = mock_json_dump.call_args
        data = args[0]

        self.assertEqual(data['name'], 'Test Mode')
        self.assertEqual(data['board_height'], 8)
        self.assertTrue(data['can_change_gm'])
        self.assertTrue(data['can_change_difficulty'])
        self.assertEqual(data['base_gm'], 'Clear The Board')
        self.assertEqual(data['difficulty'], 'Easy')

        self.assertTrue(data['board'][0][0].startswith('pK'))
        self.assertTrue(data['board'][0][1].startswith('pq'))

    @patch('builtins.open', side_effect=Exception('Test exception'))
    def test_save_exception(self, mock_open):
        self.creator.save()
        self.assertEqual(self.creator.error_msg, 'Test exception')


class TestCustomGameModeLoader(TestCase):
    def setUp(self):
        self.loader = CustomGameModeLoader()

    def test_init(self):
        self.assertEqual(self.loader.game_modes, {})
        self.assertIsNone(self.loader.selected_gm)
        self.assertIsNone(self.loader.error_msg)

    def test_reset(self):
        self.loader.selected_gm = ('test', CustomGameMode())
        self.loader.error_msg = 'Some error'

        self.loader.reset()

        self.assertIsNone(self.loader.selected_gm)
        self.assertIsNone(self.loader.error_msg)

    def test_unselect_select_gm(self):
        gm = CustomGameMode()
        self.loader.game_modes = {'test': gm}

        self.loader.select_gm('test')
        self.assertEqual(self.loader.selected_gm, ('test', gm))

        self.loader.unselect_gm()
        self.assertIsNone(self.loader.selected_gm)

    def test_parse_gm_json_missing_fields(self):
        required_fields = ['board_height', 'base_gm', 'difficulty', 'board',
                           'can_change_gm', 'can_change_difficulty']

        for field in required_fields:
            data = {f: 'value' for f in required_fields}
            del data[field]

            result = self.loader.parse_gm_json('test.json', data)

            self.assertIsNone(result)
            self.assertIn(field, self.loader.error_msg)

    def test_parse_gm_json_invalid_board(self):
        data = {
            'board_height': 8,
            'base_gm': str(GameMode.BLOCK_THE_BORDER),
            'difficulty': 'Easy',
            'board': 'not_a_list',
            'can_change_gm': True,
            'can_change_difficulty': True
        }

        result = self.loader.parse_gm_json('test.json', data)
        self.assertIsNone(result)
        self.assertIn('Board must be a LIST', self.loader.error_msg)

        data = {
            'board_height': 20,
            'base_gm': str(GameMode.BLOCK_THE_BORDER),
            'difficulty': 'Easy',
            'board': [[None for _ in range(8)] for _ in range(20)],
            'can_change_gm': True,
            'can_change_difficulty': True
        }

        result = self.loader.parse_gm_json('test.json', data)
        self.assertIsNone(result)
        self.assertIn('Board height must be an integer between 6 and 18', self.loader.error_msg)

        data = {
            'board_height': 8,
            'base_gm': str(GameMode.BLOCK_THE_BORDER),
            'difficulty': 'Easy',
            'board': [[None for _ in range(8)] for _ in range(7)] + ['not_a_list'],
            'can_change_gm': True,
            'can_change_difficulty': True
        }

        result = self.loader.parse_gm_json('test.json', data)
        self.assertIsNone(result)
        self.assertIn('Board must be a list of LISTS', self.loader.error_msg)

        data = {
            'board_height': 8,
            'base_gm': str(GameMode.BLOCK_THE_BORDER),
            'difficulty': 'Easy',
            'board': [[None for _ in range(7)] + [123] for _ in range(8)],
            'can_change_gm': True,
            'can_change_difficulty': True
        }

        result = self.loader.parse_gm_json('test.json', data)
        self.assertIsNone(result)
        self.assertIn('Board must be a list of lists of STRINGS/NULLS', self.loader.error_msg)

    def test_parse_gm_json_invalid_game_mode(self):
        data = {
            'board_height': 8,
            'base_gm': 'Invalid Mode',
            'difficulty': 'Easy',
            'board': [[None for _ in range(8)] for _ in range(8)],
            'can_change_gm': True,
            'can_change_difficulty': True
        }

        result = self.loader.parse_gm_json('test.json', data)
        self.assertIsNone(result)
        self.assertIn('Base game mode must be a string representing a valid game mode', self.loader.error_msg)

    def test_parse_gm_json_invalid_difficulty(self):
        data = {
            'board_height': 8,
            'base_gm': str(GameMode.BLOCK_THE_BORDER),
            'difficulty': 'Invalid',
            'board': [[None for _ in range(8)] for _ in range(8)],
            'can_change_gm': True,
            'can_change_difficulty': True
        }

        result = self.loader.parse_gm_json('test.json', data)
        self.assertIsNone(result)
        self.assertIn('Difficulty must be a string representing a valid difficulty', self.loader.error_msg)

    def test_parse_gm_json_invalid_boolean_fields(self):
        data = {
            'board_height': 8,
            'base_gm': str(GameMode.BLOCK_THE_BORDER),
            'difficulty': 'Easy',
            'board': [[None for _ in range(8)] for _ in range(8)],
            'can_change_gm': 'not_a_boolean',
            'can_change_difficulty': True
        }

        result = self.loader.parse_gm_json('test.json', data)
        self.assertIsNone(result)
        self.assertIn("'Can change game mode' must be a boolean", self.loader.error_msg)

        data = {
            'board_height': 8,
            'base_gm': str(GameMode.BLOCK_THE_BORDER),
            'difficulty': 'Easy',
            'board': [[None for _ in range(8)] for _ in range(8)],
            'can_change_gm': True,
            'can_change_difficulty': 'not_a_boolean'
        }

        result = self.loader.parse_gm_json('test.json', data)
        self.assertIsNone(result)
        self.assertIn("'Can change difficulty' must be a boolean", self.loader.error_msg)

    def test_parse_gm_json_valid(self):
        data = {
            'name': 'Test Game Mode',
            'board_height': 8,
            'base_gm': str(GameMode.CAPTURE_THE_MOST),
            'difficulty': 'Hard',
            'board': [[None for _ in range(8)] for _ in range(8)],
            'can_change_gm': False,
            'can_change_difficulty': True
        }

        result = self.loader.parse_gm_json('test.json', data)

        self.assertIsNotNone(result)
        self.assertEqual(result.name, 'Test Game Mode')
        self.assertEqual(result.board_height, 8)
        self.assertEqual(result.base_gm, GameMode.CAPTURE_THE_MOST)
        self.assertEqual(result.difficulty, Difficulty.HARD)
        self.assertFalse(result.can_change_gm)
        self.assertTrue(result.can_change_difficulty)

    def test_parse_gm_json_missing_name(self):
        data = {
            'board_height': 8,
            'base_gm': str(GameMode.BLOCK_THE_BORDER),
            'difficulty': 'Easy',
            'board': [[None for _ in range(8)] for _ in range(8)],
            'can_change_gm': True,
            'can_change_difficulty': True
        }

        result = self.loader.parse_gm_json('test.json', data)

        self.assertIsNotNone(result)
        self.assertEqual(result.name, '<unknown>')

    @patch('os.listdir', side_effect=FileNotFoundError)
    @patch('os.makedirs')
    def test_get_all_directory_not_found(self, mock_makedirs, mock_listdir):
        result = self.loader.get_all()

        self.assertTrue(result)
        mock_makedirs.assert_called_once_with('custom_gm', exist_ok=True)

    @patch('os.listdir', return_value=['test1.json', 'test2.json'])
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_get_all_success(self, mock_json_load, mock_file_open, mock_listdir):
        valid_data = {
            'name': 'Test Game Mode',
            'board_height': 8,
            'base_gm': str(GameMode.BLOCK_THE_BORDER),
            'difficulty': 'Easy',
            'board': [[None for _ in range(8)] for _ in range(8)],
            'can_change_gm': True,
            'can_change_difficulty': True
        }
        mock_json_load.return_value = valid_data

        result = self.loader.get_all()

        self.assertTrue(result)
        self.assertEqual(len(self.loader.game_modes), 2)
        self.assertIn('test1', self.loader.game_modes)
        self.assertIn('test2', self.loader.game_modes)

    @patch('os.listdir', return_value=['test.json'])
    @patch('builtins.open', side_effect=json.JSONDecodeError('Test error', '', 0))
    def test_get_all_json_decode_error(self, mock_file_open, mock_listdir):
        result = self.loader.get_all()

        self.assertFalse(result)
        self.assertIn('Error reading .json file', self.loader.error_msg)
