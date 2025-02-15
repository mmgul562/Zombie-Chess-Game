from game.game import Game, GameModes, Difficulties


def main():
    game = Game(board_y=8, difficulty=Difficulties.NORMAL, game_mode=GameModes.BLOCK_THE_BORDER)
    game.run()


if __name__ == '__main__':
    main()
