from game import Game


def main():
    board_y = 12
    game_modes = {'easy': 1, 'normal': 2, 'hard': 3}
    game_mode = game_modes['normal']
    game = Game(board_y, game_mode)
    game.run()


if __name__ == "__main__":
    main()
