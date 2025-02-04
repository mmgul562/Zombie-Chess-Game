from game import Game, Checkmate, Win


def main():
    board_y = 10
    game = Game(board_y, difficulty=1, game_mode='block')
    try:
        game.run()
    except Checkmate:
        print('Checkmate! The king was turned.')
    except Win:
        print("You win!")


if __name__ == '__main__':
    main()
