from game import Game


def main():
    board_y = 10
    game_modes = {'easy': 0, 'normal': 1, 'hard': 2, 'extreme': 3}
    game_mode = game_modes['easy']
    game = Game(board_y, game_mode)
    game.run()


if __name__ == "__main__":
    main()
