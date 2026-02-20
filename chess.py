"""
Defines the main game loop for a local chess multiplayer game.
"""
def make_board():
    rows = 8
    cols = 8

    board = [[0 for _ in range(cols)] for _ in range(rows)]
    return board


def main():
    board = make_board()
    print(board) 

main()