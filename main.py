from game.game import Game, GameModes, Difficulties


def main():
    game = Game(board_y=10, difficulty=Difficulties.NORMAL, game_mode=GameModes.SURVIVE_THE_LONGEST)
    game.run()


if __name__ == '__main__':
    main()
