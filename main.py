from game.game import Game, GameModes


def main():
    game = Game(board_y=10, difficulty=1, game_mode=GameModes.BLOCK_THE_BORDER)
    game.run()


if __name__ == '__main__':
    main()
