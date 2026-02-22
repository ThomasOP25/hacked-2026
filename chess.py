"""
Defines the core game loop for chess.
"""

import pieces
import functions
def main():
    sym_to_emoji_dict = {"wk": "\u2654", "wq": "\u2655", "wr": "\u2656",
                        "wb": "\u2657", "wn": "\u2658", "wp": "\u2659",
                        "bk": "\u265A", "bq": "\u265B", "br": "\u265C",
                        "bb": "\u265D", "bn": "\u265E", "bp": "\u265F"}
    board = functions.make_board()
    pieces_arr = functions.initialize_pieces()
    pos_dict = functions.chess_pos_to_coords_dict() 
    check = False
    checkmate = False
    stalemate = False
    invalid_move = False

    turn = "white"
       
    # Stalemate by repetition

    # Run testcases to see whether the player's king is in check,
    # checkmate or stalemate

    # Find whether the player's king is in check

    # If the player's king is in check, find whether it is checkmate

    while True:
        functions.place_pieces(board, pieces_arr, sym_to_emoji_dict)
        if turn == "white":
            print("It is white's turn.")
        elif turn == "black":
            print("It is black's turn.")

        functions.print_current_board(board)
      
        # Get user input (position to move from --> position to move to)
        start_pos, end_pos = functions.get_move()

        # Convert chess position to matrix coordinates
        start_coords = functions.chess_pos_to_mtx_coords(start_pos, pos_dict)
        end_coords = functions.chess_pos_to_mtx_coords(end_pos, pos_dict)
        print(start_coords)
        print(end_coords)

        """
        Run testcases to check if move is valid
        """
        # Check if the square the player wants to move from contains
        # one of their pieces
        if functions.check_start_position(turn, start_coords, pieces_arr):
            print("Valid starting position")
        else:
            print("Invalid start position")
            invalid_move = True
            continue

        # Check that the square that the player wants to move to is in
        # the list of valid moves
        # This list is not strictly valid, it contains the moves that do not 
        # result in a collision
        piece = functions.get_piece(start_coords, pieces_arr)
        moves = piece.get_valid_moves(board, pieces_arr)
        print("Valid moves: " + str(moves))

        # Move the piece if it passes all testcases
        soft_validate = functions.check_end_position(end_coords, moves)
        if soft_validate:
            print("No collisions or out of bounds")
        else:
            print("There was a collision or out of bounds")

        if end_coords in moves:
            functions.move_piece(start_coords, end_coords, board, piece, pieces_arr)
        else:
            print("Invalid move")
            continue
        # Exit the loop when the game is over

        if checkmate or stalemate:
            break

        if turn == "white":
            turn = "black"
        else:
            turn = "white"

main()