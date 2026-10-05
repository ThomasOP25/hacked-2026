import re

# Complete replacement for ai.py
NEW_AI_PY = '''from __future__ import annotations

import functions
import pieces
import random

# Base Piece values
PIECE_VALUES = {
    "pawn": 100,
    "knight": 320,
    "bishop": 330,
    "rook": 500,
    "queen": 900,
    "king": 20000
}

# Piece-Square Tables (PST) adapted from standard PeSTO weights
# Arrays are [row][col] from White's perspective (row 0 is top, row 7 is bottom)
# To use for Black, flip the row index (7 - row).

PST_PAWN_MG = [
    [  0,  0,  0,  0,  0,  0,  0,  0],
    [ 50, 50, 50, 50, 50, 50, 50, 50],
    [ 10, 10, 20, 30, 30, 20, 10, 10],
    [  5,  5, 10, 25, 25, 10,  5,  5],
    [  0,  0,  0, 20, 20,  0,  0,  0],
    [  5, -5,-10,  0,  0,-10, -5,  5],
    [  5, 10, 10,-20,-20, 10, 10,  5],
    [  0,  0,  0,  0,  0,  0,  0,  0]
]

PST_KNIGHT_MG = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

PST_BISHOP_MG = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]

PST_ROOK_MG = [
    [  0,  0,  0,  0,  0,  0,  0,  0],
    [  5, 10, 10, 10, 10, 10, 10,  5],
    [ -5,  0,  0,  0,  0,  0,  0, -5],
    [ -5,  0,  0,  0,  0,  0,  0, -5],
    [ -5,  0,  0,  0,  0,  0,  0, -5],
    [ -5,  0,  0,  0,  0,  0,  0, -5],
    [ -5,  0,  0,  0,  0,  0,  0, -5],
    [  0,  0,  0,  5,  5,  0,  0,  0]
]

PST_QUEEN_MG = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [ -5,  0,  5,  5,  5,  5,  0, -5],
    [  0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
]

PST_KING_MG = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [ 20, 20,  0,  0,  0,  0, 20, 20],
    [ 20, 30, 10,  0,  0, 10, 30, 20]
]

PST_KING_EG = [
    [-50,-40,-30,-20,-20,-30,-40,-50],
    [-30,-20,-10,  0,  0,-10,-20,-30],
    [-30,-10, 20, 30, 30, 20,-10,-30],
    [-30,-10, 30, 40, 40, 30,-10,-30],
    [-30,-10, 30, 40, 40, 30,-10,-30],
    [-30,-10, 20, 30, 30, 20,-10,-30],
    [-30,-30,  0,  0,  0,  0,-30,-30],
    [-50,-30,-30,-30,-30,-30,-30,-50]
]

PST_MAP = {
    "pawn": (PST_PAWN_MG, PST_PAWN_MG), # Simplification: endgames identical for non-king
    "knight": (PST_KNIGHT_MG, PST_KNIGHT_MG),
    "bishop": (PST_BISHOP_MG, PST_BISHOP_MG),
    "rook": (PST_ROOK_MG, PST_ROOK_MG),
    "queen": (PST_QUEEN_MG, PST_QUEEN_MG),
    "king": (PST_KING_MG, PST_KING_EG)
}

def get_game_phase(pieces_arr: list) -> float:
    """Returns a float between 0.0 (Endgame) and 1.0 (Middlegame) based on material."""
    total_phase = 0
    phase_weights = {"knight": 1, "bishop": 1, "rook": 2, "queen": 4}
    for p in pieces_arr:
        if p.alive:
            total_phase += phase_weights.get(p.piece_type, 0)
    
    max_phase = 24 # 4*knights + 4*bishops + 4*rooks + 2*queens
    return min(1.0, total_phase / max_phase)

def evaluate_board(pieces_arr: list, ai_color: str) -> int:
    """
    Returns a score from the perspective of the AI.
    Positive means AI is winning, negative means human is winning.
    """
    score = 0
    phase = get_game_phase(pieces_arr)
    
    for p in pieces_arr:
        if not p.alive:
            continue
            
        piece_type = p.piece_type
        base_val = PIECE_VALUES.get(piece_type, 0)
        
        # Piece-Square Table lookup
        row = p.row if p.color == "black" else (7 - p.row) # Assume white starts at bottom (row 7)
        col = p.col
        
        pst_mg, pst_eg = PST_MAP.get(piece_type, (None, None))
        if pst_mg and pst_eg:
            mg_score = pst_mg[row][col]
            eg_score = pst_eg[row][col]
            pst_val = int(mg_score * phase + eg_score * (1.0 - phase))
        else:
            pst_val = 0
            
        val = base_val + pst_val
            
        if p.color == ai_color:
            score += val
        else:
            score -= val
            
    return score

def get_piece_value(piece_type: str) -> int:
    return PIECE_VALUES.get(piece_type, 0)

def order_moves(moves: list[tuple[tuple[int, int], tuple[int, int]]], board: list[list], pieces_arr: list) -> list:
    """
    Sorts moves for better alpha-beta pruning (MVV-LVA heuristic).
    Captures are sorted by Most Valuable Victim - Least Valuable Attacker.
    """
    def move_score(move):
        start, end = move
        score = 0
        
        attacker = None
        victim = None
        
        for p in pieces_arr:
            if p.alive:
                if p.row == start[0] and p.col == start[1]:
                    attacker = p
                elif p.row == end[0] and p.col == end[1]:
                    victim = p
                    
        if victim:
            # MVV-LVA: High value victim + low value attacker = high score
            score = 10 * get_piece_value(victim.piece_type) - get_piece_value(attacker.piece_type)
            
        # Promotion bonus
        if attacker and attacker.piece_type == "pawn" and (end[0] == 0 or end[0] == 7):
            score += 900
            
        return score

    moves.sort(key=move_score, reverse=True)
    return moves

def simulate_move(board: list[list], pieces_arr: list, start: tuple[int, int], end: tuple[int, int]) -> dict | None:
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
    
    if piece.piece_type == "pawn" and board[end_row][end_col] == 0 and start_col != end_col:
        for p in pieces_arr:
            if p.alive and p.row == start_row and p.col == end_col:
                undo_state['ep_captured'] = p
                p.alive = False
                board[start_row][end_col] = 0
                break

    for p in pieces_arr:
        if p.alive and p.row == end_row and p.col == end_col and p != piece:
            undo_state['captured'] = p
            p.alive = False
            break
            
    if piece.piece_type == "king" and abs(start_col - end_col) == 2:
        if end_col == 6: 
            for p in pieces_arr:
                if p.alive and p.row == start_row and p.col == 7:
                    rook = p
                    undo_state['rook_moved'] = rook
                    undo_state['rook_start'] = (start_row, 7)
                    undo_state['rook_end'] = (start_row, 5)
                    undo_state['rook_orig_has_moved'] = rook.has_moved
                    rook.has_moved = True
                    rook.col = 5
                    board[start_row][7] = 0
                    board[start_row][5] = functions.SYM_TO_EMOJI_DICT[str(rook)]
                    break
        elif end_col == 2:
            for p in pieces_arr:
                if p.alive and p.row == start_row and p.col == 0:
                    rook = p
                    undo_state['rook_moved'] = rook
                    undo_state['rook_start'] = (start_row, 0)
                    undo_state['rook_end'] = (start_row, 3)
                    undo_state['rook_orig_has_moved'] = rook.has_moved
                    rook.has_moved = True
                    rook.col = 3
                    board[start_row][0] = 0
                    board[start_row][3] = functions.SYM_TO_EMOJI_DICT[str(rook)]
                    break
                    
    if piece.piece_type == "pawn" and (end_row == 0 or end_row == 7):
        piece.alive = False
        promo = pieces.Queen(end_row, end_col, piece.color)
        pieces_arr.append(promo)
        undo_state['promoted_piece'] = promo
        board[end_row][end_col] = functions.SYM_TO_EMOJI_DICT[str(promo)]
    else:
        board[end_row][end_col] = board[start_row][start_col]
        piece.row = end_row
        piece.col = end_col
        
    board[start_row][start_col] = 0
    if hasattr(piece, 'has_moved'):
        piece.has_moved = True
        
    return undo_state

def unmake_move(board: list[list], pieces_arr: list, undo_state: dict) -> None:
    if not undo_state: return
    
    piece = undo_state['piece']
    start_row, start_col = undo_state['start']
    end_row, end_col = undo_state['end']
    
    piece.row = start_row
    piece.col = start_col
    if hasattr(piece, 'has_moved'):
        piece.has_moved = undo_state['orig_has_moved']
        
    if undo_state['promoted_piece']:
        pieces_arr.remove(undo_state['promoted_piece'])
        piece.alive = True
        
    board[start_row][start_col] = functions.SYM_TO_EMOJI_DICT[str(piece)]
    board[end_row][end_col] = 0
    
    if undo_state['captured']:
        cap = undo_state['captured']
        cap.alive = True
        board[cap.row][cap.col] = functions.SYM_TO_EMOJI_DICT[str(cap)]
        
    if undo_state['ep_captured']:
        ep_cap = undo_state['ep_captured']
        ep_cap.alive = True
        board[ep_cap.row][ep_cap.col] = functions.SYM_TO_EMOJI_DICT[str(ep_cap)]
        
    if undo_state['rook_moved']:
        rook = undo_state['rook_moved']
        rr_start, rc_start = undo_state['rook_start']
        rr_end, rc_end = undo_state['rook_end']
        rook.col = rc_start
        rook.has_moved = undo_state.get('rook_orig_has_moved', False)
        board[rr_end][rc_end] = 0
        board[rr_start][rc_start] = functions.SYM_TO_EMOJI_DICT[str(rook)]

def get_all_legal_moves_for_color(board: list[list], pieces_arr: list, color: str, last_move: tuple | None) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    moves = []
    king = None
    for p in pieces_arr:
        if p.alive and p.color == color and p.piece_type == "king":
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

def quiescence_search(board: list[list], pieces_arr: list, alpha: float, beta: float, is_maximizing: bool, ai_color: str, last_move: tuple | None) -> float:
    stand_pat = evaluate_board(pieces_arr, ai_color)
    
    if is_maximizing:
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat
    else:
        if stand_pat <= alpha:
            return alpha
        if stand_pat < beta:
            beta = stand_pat
            
    current_color = ai_color if is_maximizing else ("white" if ai_color == "black" else "black")
    moves = get_all_legal_moves_for_color(board, pieces_arr, current_color, last_move)
    
    # Filter for captures only
    capture_moves = []
    for move in moves:
        start, end = move
        if board[end[0]][end[1]] != 0:
            capture_moves.append(move)
            
    capture_moves = order_moves(capture_moves, board, pieces_arr)
    
    for start, end in capture_moves:
        undo_state = simulate_move(board, pieces_arr, start, end)
        mock_last_move = (undo_state['piece'], start, end)
        
        eval = quiescence_search(board, pieces_arr, alpha, beta, not is_maximizing, ai_color, mock_last_move)
        
        unmake_move(board, pieces_arr, undo_state)
        
        if is_maximizing:
            if eval >= beta:
                return beta
            if eval > alpha:
                alpha = eval
        else:
            if eval <= alpha:
                return alpha
            if eval < beta:
                beta = eval
                
    return alpha if is_maximizing else beta

def minimax(board: list[list], pieces_arr: list, depth: int, alpha: float, beta: float, is_maximizing: bool, ai_color: str, last_move: tuple | None) -> float:
    if depth == 0:
        return quiescence_search(board, pieces_arr, alpha, beta, is_maximizing, ai_color, last_move)
        
    current_color = ai_color if is_maximizing else ("white" if ai_color == "black" else "black")
    moves = get_all_legal_moves_for_color(board, pieces_arr, current_color, last_move)
    
    if not moves:
        king = next((p for p in pieces_arr if p.alive and p.color == current_color and p.piece_type == "king"), None)
        if king and functions.king_checked(board, king, pieces_arr):
            return -999999 if is_maximizing else 999999 # Checkmate
        return 0 # Stalemate
        
    moves = order_moves(moves, board, pieces_arr)
        
    if is_maximizing:
        max_eval = -float('inf')
        for start, end in moves:
            undo_state = simulate_move(board, pieces_arr, start, end)
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

def get_best_move(board: list[list], pieces_arr: list, ai_color: str, depth: int, last_move: tuple | None) -> tuple[tuple[int, int], tuple[int, int]] | None:
    best_move = None
    max_eval = -float('inf')
    alpha = -float('inf')
    beta = float('inf')
    
    moves = get_all_legal_moves_for_color(board, pieces_arr, ai_color, last_move)
    moves = order_moves(moves, board, pieces_arr)
    
    for start, end in moves:
        undo_state = simulate_move(board, pieces_arr, start, end)
        mock_last_move = (undo_state['piece'], start, end)
        
        eval = minimax(board, pieces_arr, depth - 1, alpha, beta, False, ai_color, mock_last_move)
        
        unmake_move(board, pieces_arr, undo_state)
        
        if eval > max_eval:
            max_eval = eval
            best_move = (start, end)
            
    if best_move is None and len(moves) > 0:
        best_move = random.choice(moves)
        
    return best_move
'''

with open("ai.py", "w") as f:
    f.write(NEW_AI_PY)
