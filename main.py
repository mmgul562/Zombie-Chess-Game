from game.game import Game, GameModes, Checkmate, Win


def main():
    game = Game(board_y=10, difficulty=1, game_mode=GameModes.BLOCK_THE_BORDER)
    try:
        game.run()
    except Checkmate:
        print('Checkmate! The king was turned.')
    except Win:
        print("You win!")


if __name__ == '__main__':
    main()
