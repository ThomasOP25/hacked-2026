"""
A library of functions designed for chess.py
"""
import pieces

SYM_TO_EMOJI_DICT = {"wk": "\u2654", "wq": "\u2655", "wr": "\u2656",
                    "wb": "\u2657", "wn": "\u2658", "wp": "\u2659",
                    "bk": "\u265A", "bq": "\u265B", "br": "\u265C",
                    "bb": "\u265D", "bn": "\u265E", "bp": "\u265F"}

def make_board():
    rows = 8
    cols = 8
    board = [[0 for _ in range(cols)] for _ in range(rows)]
    return board

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

def place_pieces(board, pieces_arr):
    # Clear the board
    for row in range(8):
        for col in range(8):
            board[row][col] = 0
  
    for piece in pieces_arr:
        if piece.alive:
            row = piece.row
            col = piece.col
            piece_type = SYM_TO_EMOJI_DICT[str(piece)]
            board[row][col] = piece_type

def check_start_position(turn: str, start_coords: tuple, pieces_arr: list):
    row = start_coords[0]
    col = start_coords[1]

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

def move_piece(start_coords, end_coords, board, piece, pieces_arr, last_move=None):
    dead_arr = []
    
    start_row, start_col = start_coords
    end_row, end_col = end_coords

    # En Passant capture check
    if piece.__class__.__name__.lower() == "pawn" and board[end_row][end_col] == 0 and start_col != end_col:
        # We moved diagonally but the square was empty. This must be an En Passant!
        for p in pieces_arr:
            if p.row == start_row and p.col == end_col and p.alive:
                p.alive = False
                dead_arr.append(p)
                board[p.row][p.col] = 0
    
    # Normal Capture check
    for p in pieces_arr:
        if p.row == end_row and p.col == end_col and p != piece and p.alive:
            p.alive = False
            dead_arr.append(p)

    # Castling check (if King moves 2 squares horizontally)
    if piece.__class__.__name__.lower() == "king" and abs(start_col - end_col) == 2:
        # Move the rook
        if end_col == 6: # Kingside
            rook = get_piece((start_row, 7), pieces_arr)
            if rook:
                board[start_row][7] = 0
                board[start_row][5] = SYM_TO_EMOJI_DICT[str(rook)]
                rook.col = 5
                rook.has_moved = True
        elif end_col == 2: # Queenside
            rook = get_piece((start_row, 0), pieces_arr)
            if rook:
                board[start_row][0] = 0
                board[start_row][3] = SYM_TO_EMOJI_DICT[str(rook)]
                rook.col = 3
                rook.has_moved = True

    # Move piece physically
    temp = board[start_row][start_col]
    board[start_row][start_col] = 0
    board[end_row][end_col] = temp

    piece.row = end_row
    piece.col = end_col
    piece.has_moved = True

    return dead_arr

def update_dead_list(dead_arr, dead_pieces_white, dead_pieces_black):
    for piece in dead_arr:
        if piece.color == "white":
            dead_pieces_white.append(piece)
        else:
            dead_pieces_black.append(piece)

def check_end_position(end_coords: tuple, valid_moves: list):
    return end_coords in valid_moves

def king_checked(board, king, pieces_arr):
    king_pos = (king.row, king.col)
    enemy_color = "black" if king.color == "white" else "white"
    for piece in pieces_arr:
        if piece.alive and piece.color == enemy_color:
            enemy_moves = piece.get_valid_moves(board, pieces_arr)
            if king_pos in enemy_moves:
                return True 
    return False

def get_strictly_legal_moves(king, piece, board, pieces_arr, last_move=None):
    pseudo_moves = piece.get_valid_moves(board, pieces_arr, last_move)
    legal_moves = []
    
    start_row = piece.row
    start_col = piece.col
    
    # Check Castling moves if piece is king
    if piece.__class__.__name__.lower() == "king" and not piece.has_moved:
        if not king_checked(board, king, pieces_arr):
            # Check Kingside (col 5, 6)
            kingside_rook = get_piece((start_row, 7), pieces_arr)
            if kingside_rook and kingside_rook.__class__.__name__.lower() == "rook" and not kingside_rook.has_moved:
                if board[start_row][5] == 0 and board[start_row][6] == 0:
                    # Check if passing through check
                    piece.col = 5
                    if not king_checked(board, king, pieces_arr):
                        piece.col = 6
                        if not king_checked(board, king, pieces_arr):
                            pseudo_moves.append((start_row, 6))
                    piece.col = start_col # restore

            # Check Queenside (col 1, 2, 3)
            queenside_rook = get_piece((start_row, 0), pieces_arr)
            if queenside_rook and queenside_rook.__class__.__name__.lower() == "rook" and not queenside_rook.has_moved:
                if board[start_row][1] == 0 and board[start_row][2] == 0 and board[start_row][3] == 0:
                    # Check passing through
                    piece.col = 3
                    if not king_checked(board, king, pieces_arr):
                        piece.col = 2
                        if not king_checked(board, king, pieces_arr):
                            pseudo_moves.append((start_row, 2))
                    piece.col = start_col # restore

    for move in pseudo_moves:
        end_row, end_col = move
        
        # Simulate move
        captured_piece = None
        for p in pieces_arr:
            if p.alive and p.row == end_row and p.col == end_col:
                captured_piece = p
                captured_piece.alive = False 
                break

        # Simulate En Passant Capture
        ep_captured_piece = None
        if piece.__class__.__name__.lower() == "pawn" and start_col != end_col and captured_piece is None:
            for p in pieces_arr:
                if p.alive and p.row == start_row and p.col == end_col:
                    ep_captured_piece = p
                    ep_captured_piece.alive = False
                    break

        piece.row = end_row
        piece.col = end_col
        
        temp_start_symbol = board[start_row][start_col]
        temp_end_symbol = board[end_row][end_col]
        
        board[start_row][start_col] = 0
        board[end_row][end_col] = temp_start_symbol
        
        if not king_checked(board, king, pieces_arr):
            legal_moves.append(move)
            
        board[start_row][start_col] = temp_start_symbol
        board[end_row][end_col] = temp_end_symbol
        
        piece.row = start_row
        piece.col = start_col
        
        if captured_piece:
            captured_piece.alive = True
        if ep_captured_piece:
            ep_captured_piece.alive = True
            
    return legal_moves
