"""
A library of functions designed for chess.py
"""
import pieces

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
   

def print_current_board(board):
    print("-" * 33)
    for i in range(len(board)):
        print("|", end="")
        for j in range(len(board[i]) - 1):
            square = str(board[i][j])
            print(square.center(3), end="")
            print("|", end="")
        j += 1
        square = str(board[i][j])
        print(square.center(3), end="")
        print("|")
        print("-" * 33)


def initialize_pieces():
    wk = pieces.King(7, 4, "white")
    wq = pieces.Queen(7, 3, "white")
    wr1 = pieces.Rook(7, 0, "white")
    wr2 = pieces.Rook(7, 7, "white")
    wn1 = pieces.Knight(7, 1, "white")
    wn2 = pieces.Knight(7, 6, "white")
    wb1 = pieces.Bishop(7, 2, "white")
    wb2 = pieces.Bishop(7, 5, "white")
    wp1 = pieces.Pawn(6, 0, "white")
    wp2 = pieces.Pawn(6, 1, "white")
    wp3 = pieces.Pawn(6, 2, "white")
    wp4 = pieces.Pawn(6, 3, "white")
    wp5 = pieces.Pawn(6, 4, "white")
    wp6 = pieces.Pawn(6, 5, "white")
    wp7 = pieces.Pawn(6, 6, "white")
    wp8 = pieces.Pawn(6, 7, "white")
    bk = pieces.King(0, 4, "black")
    bq = pieces.Queen(0, 3, "black")
    br1 = pieces.Rook(0, 0, "black")
    br2 = pieces.Rook(0, 7, "black")
    bn1 = pieces.Knight(0, 1, "black")
    bn2 = pieces.Knight(0, 6, "black")
    bb1 = pieces.Bishop(0, 2, "black")
    bb2 = pieces.Bishop(0, 5, "black")
    bp1 = pieces.Pawn(1, 0, "black")
    bp2 = pieces.Pawn(1, 1, "black")
    bp3 = pieces.Pawn(1, 2, "black")
    bp4 = pieces.Pawn(1, 3, "black")
    bp5 = pieces.Pawn(1, 4, "black")
    bp6 = pieces.Pawn(1, 5, "black")
    bp7 = pieces.Pawn(1, 6, "black")
    bp8 = pieces.Pawn(1, 7, "black")

    pieces_arr = [wk, wq, wr1, wr2, wn1, wn2, wb1, wb2, wp1, wp2, wp3,
                 wp4, wp5, wp6, wp7, wp8, bk, bq, br1, br2, bn1, bn2,
                 bb1, bb2, bp1, bp2, bp3, bp4, bp5, bp6, bp7, bp8]
  
    return pieces_arr


def place_pieces(board, pieces_arr, sym_to_emoji_dict):
    # Create a dictionary to convert the string representation of the
    # piece type to a chess symbol in Unicode

    # Clear the board
    for row in range(8):
        for col in range(8):
            board[row][col] = 0
  
    for piece in pieces_arr:
        if piece.alive:
            row = piece.row
            col = piece.col
            piece_type = sym_to_emoji_dict[str(piece)]
            board[row][col] = piece_type


def chess_pos_to_mtx_coords(chess_pos: str, pos_dict: dict):
    """
    Returns tuple.
    """
    coords = pos_dict[chess_pos]
    return coords


def check_start_position(turn: str, start_coords: tuple, pieces_arr: list):
    """
    Ensures that the player's starting position contains one of their pieces.
    """
    row = start_coords[0]
    col = start_coords[1]

    # Check if any of the piece's current positions match with start_pos
    for piece in pieces_arr:
        if piece.alive:
            if piece.row == row and piece.col == col:
                if piece.color == turn:
                    return True
    return False


def get_piece(start_coords, pieces_arr):
    row = start_coords[0]
    col = start_coords[1]

    for piece in pieces_arr:
        if piece.alive and row == piece.row and col == piece.col:
            return piece
    return False


def move_piece(start_coords, end_coords, board, piece, pieces_arr):
    """
    Moves a piece from one position to another. If the piece takes another,
    the dead piece is added to an array.
    """
    # Mark captured piece as dead
    dead_arr = []
    for p in pieces_arr:
        if p.row == end_coords[0] and p.col == end_coords[1] and p != piece:
            p.alive = False
            dead_arr.append(p)

    start_row = start_coords[0]
    start_col = start_coords[1]
    end_row = end_coords[0]
    end_col = end_coords[1]

    temp = board[start_row][start_col]
    board[start_row][start_col] = 0
    board[end_row][end_col] = temp

    piece.row = end_coords[0]
    piece.col = end_coords[1]

    return dead_arr


def update_dead_list(dead_arr, dead_pieces_white, dead_pieces_black):
    for piece in dead_arr:
        if piece.color == "white":
            dead_pieces_white.append(piece)
        else:
            dead_pieces_black.append(piece)


def check_end_position(end_coords: tuple, valid_moves: list):
    if end_coords in valid_moves:
        return True
    else:
        return False


def promote_pawn(piece, board):
    """
    Must pass piece of type "Pawn".
    """
    possible_choices = ("q", "r", "k", "b")
    if piece.color == "white":
        if piece.row == 0:
            print("You can promote your pawn!")
            promotion_piece = input("Choose a piece to promote to "
                            "(queen: \"q\", rook: \"r\", knight: \"k\", bishop: \"b\"): ")
        while promotion_piece not in possible_choices:
            print("You can promote your pawn!")
            promotion_piece = input("Choose a piece to promote to "
                            "(queen: \"q\", rook: \"r\", knight: \"k\", bishop: \"b\"): ")
        col = piece.col
        board[0][col] == 0
        pass

            
    elif piece.color == "black":
        if piece.row == 7:
            print("You can promote your pawn!")
            promotion_piece = input("Choose a piece to promote to "
                            "(queen: \"q\", rook: \"r\", knight: \"k\", bishop: \"b\"): ")
            

def king_checked(board, king, pieces_arr):
    """
    Returns True if the specified color's King is currently under attack.
    """
    king_pos = (king.row, king.col)
            
    # Ask all alive enemy pieces if they can hit the King's coordinate
    enemy_color = "black" if king.color == "white" else "white"
    for piece in pieces_arr:
        if piece.alive and piece.color == enemy_color:
            enemy_moves = piece.get_valid_moves(board, pieces_arr)
            if king_pos in enemy_moves:
                return True # Check!!!
                
    return False


def get_strictly_legal_moves(king, piece, board, pieces_arr):
    """
    Filters pseudo-legal moves by simulating them and checking for King safety.
    """
    pseudo_moves = piece.get_valid_moves(board, pieces_arr)
    legal_moves = []
    
    start_row = piece.row
    start_col = piece.col
    
    for move in pseudo_moves:
        end_row, end_col = move
        
        # Simulate the move
        captured_piece = None
        for p in pieces_arr:
            # Check if there's a piece at the target square that would be captured
            if p.alive and p.row == end_row and p.col == end_col:
                captured_piece = p
                captured_piece.alive = False 
                break

        # Update the piece's position
        piece.row = end_row
        piece.col = end_col
        
        # Remember the original board state to restore later
        temp_start_symbol = board[start_row][start_col]
        temp_end_symbol = board[end_row][end_col]
        
        # Update the board to reflect the simulated move
        board[start_row][start_col] = 0
        board[end_row][end_col] = temp_start_symbol
        
        # Check if the move leaves the player's own King in check
        if not king_checked(board, king, pieces_arr):
            legal_moves.append(move)
            
        # Undo the simulated move
        board[start_row][start_col] = temp_start_symbol
        board[end_row][end_col] = temp_end_symbol
        
        # Restore the piece's original position
        piece.row = start_row
        piece.col = start_col
        
        # If a piece was captured in the simulation, restore it
        if captured_piece:
            captured_piece.alive = True
            
    return legal_moves
