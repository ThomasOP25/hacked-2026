"""
Defines the main game loop for a local chess multiplayer game.
"""
def make_board():
    rows = 8
    cols = 8

    board = [[0 for _ in range(cols)] for _ in range(rows)]
    return board

def chess_pos_to_coords_dict():
    """
    Creates a dictionary  position in the form "<letter><number>" to matrix coordinates
    in the form (<row>, <col>)
    """

    # Create a list of possible positions
    pos_list = []
    letters = ("a", "b", "c", "d", "e", "f", "g", "h")

    for letter in letters:
        for i in range(1, 9):
            pos_list.append(f"{letter}{str(i)}")

    # Map the list of positions to coordinates on the matrix
    pos_dict = {}

    for pos in pos_list:
        letter = pos[0]
        col = letters.index(letter)
        row = 8 - int(pos[1])
        pos_dict[pos] = (row, col)

    return pos_dict

def get_move():
    """
    Prompt the player for their move. This function calls itself recursively
    until a valid move is entered.
    """
    move = input("Enter your move using chess postions e.g. \"a2 --> b3\" <starting position> <end position>: ")  
    letters = ("a", "b", "c", "d", "e", "f", "g", "h")

    # Run checks to make sure the move is valid
    try:
        a, b = move.split()
        if len(a) != 2 or len(b) != 2:
            raise ValueError
        if a[0] not in letters or b[0] not in letters:
            raise ValueError
        if int(a[1]) not in range(1, 9) or int(b[1]) not in range(1, 9):
            raise ValueError
        if a == b:
            raise ValueError
    except ValueError:
        print("Your move was entered in an invalid format.")
        return get_move()
    else:
        print(f"Your input was entered in the correct format: {a} --> {b}.")
        return (a, b)


def main():
    board = make_board()
    pos_dict = chess_pos_to_coords_dict()
    turn = "white"

    while True:
        if turn == "white":
            print("It is white's turn.")
        elif turn == "black":
            print("It is black's turn.")

        # Display board
        print("-" * 33)
        for i in range(len(board)):
            print("|", end="")
            for j in range(len(board[i]) - 1):
                square = str(board[i][j])
                print(square.center(3), end="")
                print("|", end="")
            square = str(board[i][j])
            print(square.center(3), end="")
            print("|")
            print("-" * 33)
        
        # Get user input
        get_move()

        # Run testcases to see if the move is valid

        # Exit the loop when the game is over
        break

main()