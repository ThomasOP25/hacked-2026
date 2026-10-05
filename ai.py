import functions
import pieces

PIECE_VALUES = {
    "pawn": 10,
    "knight": 30,
    "bishop": 30,
    "rook": 50,
    "queen": 90,
    "king": 9000
}

# Positional bonus for controlling the center
CENTER_BONUS = {
    (3, 3): 2, (3, 4): 2, (4, 3): 2, (4, 4): 2,
    (2, 2): 1, (2, 3): 1, (2, 4): 1, (2, 5): 1,
    (3, 2): 1, (3, 5): 1, (4, 2): 1, (4, 5): 1,
    (5, 2): 1, (5, 3): 1, (5, 4): 1, (5, 5): 1,
}

def evaluate_board(pieces_arr, ai_color):
    """
    Returns a score from the perspective of the AI.
    Positive means AI is winning, negative means human is winning.
    """
    score = 0
    for p in pieces_arr:
        if p.alive:
            piece_type = p.__class__.__name__.lower()
            val = PIECE_VALUES.get(piece_type, 0)
            
            # Add center control bonus for non-kings
            if piece_type != "king":
                val += CENTER_BONUS.get((p.row, p.col), 0)
                
            if p.color == ai_color:
                score += val
            else:
                score -= val
    return score

def simulate_move(board, pieces_arr, start, end):
    """
    Applies a move and returns state needed to undo it.
    This is a simplified version of move_piece for the AI tree search.
    """
    start_row, start_col = start
    end_row, end_col = end
    
    piece = None
    for p in pieces_arr:
        if p.alive and p.row == start_row and p.col == start_col:
            piece = p
            break
            
    if not piece:
        return None
        
    undo_state = {
        'piece': piece,
        'start': start,
        'end': end,
        'captured': None,
        'ep_captured': None,
        'promoted_piece': None,
        'rook_moved': None,
        'rook_start': None,
        'rook_end': None,
        'orig_has_moved': getattr(piece, 'has_moved', False)
    }
    
    # 1. En Passant Capture Check
    if piece.__class__.__name__.lower() == "pawn" and board[end_row][end_col] == 0 and start_col != end_col:
        for p in pieces_arr:
            if p.alive and p.row == start_row and p.col == end_col:
                undo_state['ep_captured'] = p
                p.alive = False
                board[start_row][end_col] = 0
                break

    # 2. Normal Capture Check
    for p in pieces_arr:
        if p.alive and p.row == end_row and p.col == end_col and p != piece:
            undo_state['captured'] = p
            p.alive = False
            break
            
    # 3. Castling Check
    if piece.__class__.__name__.lower() == "king" and abs(start_col - end_col) == 2:
        if end_col == 6: # Kingside
            for p in pieces_arr:
                if p.alive and p.row == start_row and p.col == 7:
                    undo_state['rook_moved'] = p
                    undo_state['rook_start'] = (start_row, 7)
                    undo_state['rook_end'] = (start_row, 5)
                    p.col = 5
                    board[start_row][7] = 0
                    board[start_row][5] = functions.SYM_TO_EMOJI_DICT[str(p)]
                    break
        elif end_col == 2: # Queenside
            for p in pieces_arr:
                if p.alive and p.row == start_row and p.col == 0:
                    undo_state['rook_moved'] = p
                    undo_state['rook_start'] = (start_row, 0)
                    undo_state['rook_end'] = (start_row, 3)
                    p.col = 3
                    board[start_row][0] = 0
                    board[start_row][3] = functions.SYM_TO_EMOJI_DICT[str(p)]
                    break
                    
    # 4. Handle Promotion
    if piece.__class__.__name__.lower() == "pawn" and (end_row == 0 or end_row == 7):
        piece.alive = False
        promo = pieces.Queen(end_row, end_col, piece.color)
        pieces_arr.append(promo)
        undo_state['promoted_piece'] = promo
        board[end_row][end_col] = functions.SYM_TO_EMOJI_DICT[str(promo)]
    else:
        # Normal move
        board[end_row][end_col] = board[start_row][start_col]
        piece.row = end_row
        piece.col = end_col
        
    board[start_row][start_col] = 0
    if hasattr(piece, 'has_moved'):
        piece.has_moved = True
        
    return undo_state

def unmake_move(board, pieces_arr, undo_state):
    """Restores the board and pieces from an undo_state"""
    if not undo_state: return
    
    piece = undo_state['piece']
    start_row, start_col = undo_state['start']
    end_row, end_col = undo_state['end']
    
    # Revert piece position
    piece.row = start_row
    piece.col = start_col
    if hasattr(piece, 'has_moved'):
        piece.has_moved = undo_state['orig_has_moved']
        
    # Revert promotion
    if undo_state['promoted_piece']:
        pieces_arr.remove(undo_state['promoted_piece'])
        piece.alive = True
        
    # Restore board for main piece
    board[start_row][start_col] = functions.SYM_TO_EMOJI_DICT[str(piece)]
    board[end_row][end_col] = 0
    
    # Revert captures
    if undo_state['captured']:
        cap = undo_state['captured']
        cap.alive = True
        board[cap.row][cap.col] = functions.SYM_TO_EMOJI_DICT[str(cap)]
        
    if undo_state['ep_captured']:
        ep_cap = undo_state['ep_captured']
        ep_cap.alive = True
        board[ep_cap.row][ep_cap.col] = functions.SYM_TO_EMOJI_DICT[str(ep_cap)]
        
    # Revert castling
    if undo_state['rook_moved']:
        rook = undo_state['rook_moved']
        rr_start, rc_start = undo_state['rook_start']
        rr_end, rc_end = undo_state['rook_end']
        rook.col = rc_start
        rook.has_moved = False
        board[rr_end][rc_end] = 0
        board[rr_start][rc_start] = functions.SYM_TO_EMOJI_DICT[str(rook)]

def get_all_legal_moves_for_color(board, pieces_arr, color, last_move):
    moves = []
    king = None
    for p in pieces_arr:
        if p.alive and p.color == color and p.__class__.__name__.lower() == "king":
            king = p
            break
            
    if not king:
        return moves
        
    for p in pieces_arr:
        if p.alive and p.color == color:
            legal = functions.get_strictly_legal_moves(king, p, board, pieces_arr, last_move)
            for end_pos in legal:
                moves.append(((p.row, p.col), end_pos))
    return moves

def minimax(board, pieces_arr, depth, alpha, beta, is_maximizing, ai_color, last_move):
    if depth == 0:
        return evaluate_board(pieces_arr, ai_color)
        
    current_color = ai_color if is_maximizing else ("white" if ai_color == "black" else "black")
    moves = get_all_legal_moves_for_color(board, pieces_arr, current_color, last_move)
    
    if not moves:
        # No moves -> Checkmate or Stalemate
        king = next((p for p in pieces_arr if p.alive and p.color == current_color and p.__class__.__name__.lower() == "king"), None)
        if king and functions.king_checked(board, king, pieces_arr):
            return -99999 if is_maximizing else 99999 # Checkmate
        return 0 # Stalemate
        
    if is_maximizing:
        max_eval = -float('inf')
        for start, end in moves:
            undo_state = simulate_move(board, pieces_arr, start, end)
            
            # The last move for the next state is just a mock representing this move
            mock_last_move = (undo_state['piece'], start, end)
            
            eval = minimax(board, pieces_arr, depth - 1, alpha, beta, False, ai_color, mock_last_move)
            unmake_move(board, pieces_arr, undo_state)
            
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for start, end in moves:
            undo_state = simulate_move(board, pieces_arr, start, end)
            
            mock_last_move = (undo_state['piece'], start, end)
            
            eval = minimax(board, pieces_arr, depth - 1, alpha, beta, True, ai_color, mock_last_move)
            unmake_move(board, pieces_arr, undo_state)
            
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def get_best_move(board, pieces_arr, ai_color, depth, last_move):
    """
    Entry point for the AI. Returns (start_coords, end_coords).
    """
    best_move = None
    max_eval = -float('inf')
    alpha = -float('inf')
    beta = float('inf')
    
    moves = get_all_legal_moves_for_color(board, pieces_arr, ai_color, last_move)
    
    # Sort moves slightly to improve pruning (e.g., captures first could be done here)
    # But for simplicity, we just iterate.
    
    for start, end in moves:
        undo_state = simulate_move(board, pieces_arr, start, end)
        mock_last_move = (undo_state['piece'], start, end)
        
        eval = minimax(board, pieces_arr, depth - 1, alpha, beta, False, ai_color, mock_last_move)
        
        unmake_move(board, pieces_arr, undo_state)
        
        if eval > max_eval:
            max_eval = eval
            best_move = (start, end)
            
    # Fallback to random move if all are equally bad
    if best_move is None and len(moves) > 0:
        import random
        best_move = random.choice(moves)
        
    return best_move
