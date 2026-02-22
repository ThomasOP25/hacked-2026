"""
Defines the core game loop for chess.
"""

import functions
import pieces

def main():
    sym_to_emoji_dict = {"wk": "\u2654", "wq": "\u2655", "wr": "\u2656",
                        "wb": "\u2657", "wn": "\u2658", "wp": "\u2659",
                        "bk": "\u265A", "bq": "\u265B", "br": "\u265C",
                        "bb": "\u265D", "bn": "\u265E", "bp": "\u265F"}
    
    dead_pieces_white = []
    dead_pieces_black = []

    board = functions.make_board()
    pieces_arr = functions.initialize_pieces()
    pos_dict = functions.chess_pos_to_coords_dict() 

    check = False
    turn = "white"

    while True:
        check = False
        functions.place_pieces(board, pieces_arr, sym_to_emoji_dict)

        # Stalemate by repetition

        # Run testcases to see whether the player's king is in check,
        # checkmate or stalemate

        # Find whether the player's king is in check
        for piece in pieces_arr:
            if piece.color == turn and isinstance(piece, pieces.King):
                king = piece
        if functions.king_checked(board, king, pieces_arr):
            check = True
            
        # If the player's king is in check, find whether it is checkmate
        legal_moves = []
        for p in pieces_arr:
            if p.alive and p.color == turn:
                legal_moves += functions.get_strictly_legal_moves(king, p, board, pieces_arr)
        if check:
            if len(legal_moves) == 0:
                print("Checkmate!")
                break
        else:
            if len(legal_moves) == 0:
                print("Stalemate!")
                break
            
        if turn == "white":
            print("It is white's turn.")
        elif turn == "black":
            print("It is black's turn.")

        if check == True:
            print("You are in check.")

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
            continue

        # Check that the square that the player wants to move to is in
        # a list of valid moves
        piece = functions.get_piece(start_coords, pieces_arr)
        moves = functions.get_strictly_legal_moves(king, piece, board, pieces_arr)
        print("Valid moves: " + str(moves))

        # Move the piece if it passes all testcases
        validate = functions.check_end_position(end_coords, moves)
        if validate:
            print("Valid move")
            # Move the piece. If this move captures an enemy piece
            # the function returns that piece.
            dead_arr = functions.move_piece(start_coords, end_coords, board, piece, pieces_arr)
        else:
            print("Invalid move")
            continue

        # If a pawn reaches the furthest opposite row, it may be promoted.
        # The user can choose which piece to promote to.
        if piece.__class__.__name__.lower() == "pawn":
            pass

        # Add dead pieces to a list
        functions.update_dead_list(dead_arr, dead_pieces_white, dead_pieces_black)
        print(f"White dead list: {dead_pieces_white}")
        print(f"Black dead list: {dead_pieces_black}")

        if turn == "white":
            turn = "black"
        else:
            turn = "white"

main()