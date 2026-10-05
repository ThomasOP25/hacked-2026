from __future__ import annotations

"""
GameState class — single source of truth for the chess game state.
Wraps existing functions.py, pieces.py, and ai.py modules.
"""

import logging
from typing import Optional

import pieces
import functions
import ai

logger = logging.getLogger("chess.game_state")

# FEN piece char mapping
FEN_PIECE_MAP = {
    'K': ('King', 'white'), 'Q': ('Queen', 'white'), 'R': ('Rook', 'white'),
    'B': ('Bishop', 'white'), 'N': ('Knight', 'white'), 'P': ('Pawn', 'white'),
    'k': ('King', 'black'), 'q': ('Queen', 'black'), 'r': ('Rook', 'black'),
    'b': ('Bishop', 'black'), 'n': ('Knight', 'black'), 'p': ('Pawn', 'black'),
}

PIECE_CLASS_MAP = {
    'King': pieces.King, 'Queen': pieces.Queen, 'Rook': pieces.Rook,
    'Bishop': pieces.Bishop, 'Knight': pieces.Knight, 'Pawn': pieces.Pawn,
}

PIECE_TO_FEN = {
    ('king', 'white'): 'K', ('queen', 'white'): 'Q', ('rook', 'white'): 'R',
    ('bishop', 'white'): 'B', ('knight', 'white'): 'N', ('pawn', 'white'): 'P',
    ('king', 'black'): 'k', ('queen', 'black'): 'q', ('rook', 'black'): 'r',
    ('bishop', 'black'): 'b', ('knight', 'black'): 'n', ('pawn', 'black'): 'p',
}


class GameState:
    """Encapsulates the full state of a chess game."""

    def __init__(self) -> None:
        self.board: list[list] = []
        self.pieces_arr: list[pieces.Piece] = []
        self.turn: str = "white"
        self.last_move: tuple | None = None
        self.halfmove_clock: int = 0
        self.fullmove_number: int = 1
        self.history: list[str] = []
        self.dead_white: list[pieces.Piece] = []
        self.dead_black: list[pieces.Piece] = []
        self.game_over: bool = False
        self.is_draw: bool = False
        self.check: bool = False
        self.promotion_pending: dict | None = None
        self.move_log: list[str] = []
        self.reset()

    def reset(self) -> None:
        """Reset to starting position."""
        self.board = functions.make_board()
        self.pieces_arr = functions.initialize_pieces()
        self.turn = "white"
        self.last_move = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.history = []
        self.dead_white = []
        self.dead_black = []
        self.game_over = False
        self.is_draw = False
        self.check = False
        self.promotion_pending = None
        self.move_log = []
        functions.place_pieces(self.board, self.pieces_arr)
        logger.info("Game reset to starting position")

    def get_king(self, color: str) -> pieces.King | None:
        """Find the king of the given color."""
        for p in self.pieces_arr:
            if p.alive and p.color == color and isinstance(p, pieces.King):
                return p
        return None

    def is_check(self) -> bool:
        """Check if the current turn's king is in check."""
        king = self.get_king(self.turn)
        if king is None:
            return False
        return functions.king_checked(self.board, king, self.pieces_arr)

    def get_legal_moves(self) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        """Get all legal moves for the current turn."""
        king = self.get_king(self.turn)
        if king is None:
            return []
        moves = []
        for p in self.pieces_arr:
            if p.alive and p.color == self.turn:
                legal = functions.get_strictly_legal_moves(
                    king, p, self.board, self.pieces_arr, self.last_move
                )
                for end_pos in legal:
                    moves.append(((p.row, p.col), end_pos))
        return moves

    def get_legal_moves_for_piece(self, piece: pieces.Piece) -> list[tuple[int, int]]:
        """Get legal moves for a specific piece."""
        king = self.get_king(piece.color)
        if king is None:
            return []
        return functions.get_strictly_legal_moves(
            king, piece, self.board, self.pieces_arr, self.last_move
        )

    def make_move(self, start: tuple[int, int], end: tuple[int, int]) -> bool:
        """
        Execute a human player move. Returns True if successful.
        Sets promotion_pending if pawn reaches the end rank.
        """
        if self.game_over or self.promotion_pending:
            return False

        piece = functions.get_piece(start, self.pieces_arr)
        if piece is None or piece.color != self.turn:
            return False

        king = self.get_king(self.turn)
        if king is None:
            return False

        legal = functions.get_strictly_legal_moves(
            king, piece, self.board, self.pieces_arr, self.last_move
        )
        if end not in legal:
            return False

        # Determine if capture for notation
        is_capture = self.board[end[0]][end[1]] != 0
        if piece.piece_type == "pawn" and start[1] != end[1] and not is_capture:
            is_capture = True  # en passant

        # Reset 50-move clock
        if piece.piece_type == "pawn" or is_capture:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        dead_arr = functions.move_piece(
            start, end, self.board, piece, self.pieces_arr, self.last_move
        )
        self.last_move = (piece, start, end)

        # Log move notation
        notation = self.to_move_notation(piece, start, end, is_capture)
        self.move_log.append(notation)
        logger.info(f"Move: {notation}")

        # Check for promotion
        if piece.piece_type == "pawn" and (piece.row == 0 or piece.row == 7):
            self.promotion_pending = {
                'piece': piece, 'row': piece.row, 'col': piece.col,
                'color': piece.color, 'dead_arr': dead_arr
            }
            return True

        functions.update_dead_list(dead_arr, self.dead_white, self.dead_black)

        if self.turn == "black":
            self.fullmove_number += 1
        self.turn = "black" if self.turn == "white" else "white"

        functions.place_pieces(self.board, self.pieces_arr)
        self.check_game_end()
        return True

    def complete_promotion(self, piece_type: str) -> None:
        """Complete a pending pawn promotion."""
        if not self.promotion_pending:
            return

        state = self.promotion_pending
        old_pawn = state['piece']
        old_pawn.alive = False
        row, col, color = state['row'], state['col'], state['color']

        cls_map = {
            'queen': pieces.Queen, 'rook': pieces.Rook,
            'bishop': pieces.Bishop, 'knight': pieces.Knight,
        }
        cls = cls_map.get(piece_type.lower(), pieces.Queen)
        promo = cls(row, col, color)
        self.pieces_arr.append(promo)

        functions.update_dead_list(
            state['dead_arr'], self.dead_white, self.dead_black
        )
        self.promotion_pending = None

        if self.turn == "black":
            self.fullmove_number += 1
        self.turn = "black" if self.turn == "white" else "white"

        functions.place_pieces(self.board, self.pieces_arr)
        self.check_game_end()
        logger.info(f"Promoted to {piece_type}")

    def make_ai_move(self, depth: int) -> bool:
        """Execute an AI move. Returns True if a move was made."""
        if self.game_over or self.promotion_pending:
            return False

        best = ai.get_best_move(
            self.board, self.pieces_arr, self.turn, depth, self.last_move
        )
        if best is None:
            return False

        start, end = best
        piece = functions.get_piece(start, self.pieces_arr)
        if piece is None:
            return False

        is_capture = self.board[end[0]][end[1]] != 0
        if piece.piece_type == "pawn" and start[1] != end[1] and not is_capture:
            is_capture = True

        if piece.piece_type == "pawn" or is_capture:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        dead_arr = functions.move_piece(
            start, end, self.board, piece, self.pieces_arr, self.last_move
        )
        self.last_move = (piece, start, end)

        notation = self.to_move_notation(piece, start, end, is_capture)
        self.move_log.append(notation)
        logger.info(f"AI Move: {notation}")

        # Auto-queen for AI
        if piece.piece_type == "pawn" and (piece.row == 0 or piece.row == 7):
            piece.alive = False
            promo = pieces.Queen(piece.row, piece.col, piece.color)
            self.pieces_arr.append(promo)

        functions.update_dead_list(dead_arr, self.dead_white, self.dead_black)

        if self.turn == "black":
            self.fullmove_number += 1
        self.turn = "black" if self.turn == "white" else "white"

        functions.place_pieces(self.board, self.pieces_arr)
        self.check_game_end()
        return True

    def get_board_hash(self) -> str:
        """Position hash for 3-fold repetition detection."""
        board_str = "".join([str(p) for row in self.board for p in row])
        board_str += self.turn
        for p in self.pieces_arr:
            if p.alive and (isinstance(p, pieces.King) or isinstance(p, pieces.Rook)):
                board_str += f"{p.piece_type}{p.col}{p.has_moved}"
        if self.last_move:
            lm_piece, lm_start, lm_end = self.last_move
            if lm_piece.piece_type == "pawn" and abs(lm_start[0] - lm_end[0]) == 2:
                board_str += f"ep{lm_end[1]}"
        return board_str

    def check_game_end(self) -> None:
        """Update game_over, is_draw, check fields."""
        functions.place_pieces(self.board, self.pieces_arr)
        self.check = self.is_check()

        legal = self.get_legal_moves()

        # Record position for repetition
        bh = self.get_board_hash()
        self.history.append(bh)

        self.is_draw = False
        if self.history.count(bh) >= 3:
            self.is_draw = True
        if self.halfmove_clock >= 100:
            self.is_draw = True
        if self.is_insufficient_material():
            self.is_draw = True

        if len(legal) == 0:
            self.game_over = True
            self.is_draw = not self.check
        elif self.is_draw:
            self.game_over = True

    def is_insufficient_material(self) -> bool:
        """Detect automatic draws due to insufficient material."""
        alive = [p for p in self.pieces_arr if p.alive]
        white = [p for p in alive if p.color == "white"]
        black = [p for p in alive if p.color == "black"]

        white_types = sorted([p.piece_type for p in white])
        black_types = sorted([p.piece_type for p in black])

        # K vs K
        if white_types == ["king"] and black_types == ["king"]:
            return True

        # K+minor vs K
        if white_types == ["king"] and black_types in [["bishop", "king"], ["king", "knight"]]:
            return True
        if black_types == ["king"] and white_types in [["bishop", "king"], ["king", "knight"]]:
            return True

        # K+B vs K+B same color bishops
        if white_types == ["bishop", "king"] and black_types == ["bishop", "king"]:
            wb = next(p for p in white if p.piece_type == "bishop")
            bb = next(p for p in black if p.piece_type == "bishop")
            if (wb.row + wb.col) % 2 == (bb.row + bb.col) % 2:
                return True

        return False

    def to_fen(self) -> str:
        """Export position as FEN string."""
        # 1. Piece placement
        rows = []
        for r in range(8):
            empty = 0
            row_str = ""
            for c in range(8):
                p = None
                for piece in self.pieces_arr:
                    if piece.alive and piece.row == r and piece.col == c:
                        p = piece
                        break
                if p is None:
                    empty += 1
                else:
                    if empty > 0:
                        row_str += str(empty)
                        empty = 0
                    row_str += PIECE_TO_FEN.get((p.piece_type, p.color), '?')
            if empty > 0:
                row_str += str(empty)
            rows.append(row_str)
        placement = "/".join(rows)

        # 2. Active color
        active = "w" if self.turn == "white" else "b"

        # 3. Castling
        castling = ""
        wk = self.get_king("white")
        bk = self.get_king("black")
        if wk and not wk.has_moved:
            wr_k = functions.get_piece((7, 7), self.pieces_arr)
            if wr_k and wr_k.piece_type == "rook" and not wr_k.has_moved:
                castling += "K"
            wr_q = functions.get_piece((7, 0), self.pieces_arr)
            if wr_q and wr_q.piece_type == "rook" and not wr_q.has_moved:
                castling += "Q"
        if bk and not bk.has_moved:
            br_k = functions.get_piece((0, 7), self.pieces_arr)
            if br_k and br_k.piece_type == "rook" and not br_k.has_moved:
                castling += "k"
            br_q = functions.get_piece((0, 0), self.pieces_arr)
            if br_q and br_q.piece_type == "rook" and not br_q.has_moved:
                castling += "q"
        if not castling:
            castling = "-"

        # 4. En passant
        ep = "-"
        if self.last_move:
            lm_piece, lm_start, lm_end = self.last_move
            if lm_piece.piece_type == "pawn" and abs(lm_start[0] - lm_end[0]) == 2:
                ep_row = (lm_start[0] + lm_end[0]) // 2
                ep_col = lm_end[1]
                ep = chr(ord('a') + ep_col) + str(8 - ep_row)

        # 5 & 6. Clocks
        return f"{placement} {active} {castling} {ep} {self.halfmove_clock} {self.fullmove_number}"

    @classmethod
    def from_fen(cls, fen: str) -> 'GameState':
        """Create a GameState from a FEN string."""
        gs = cls.__new__(cls)
        gs.board = functions.make_board()
        gs.pieces_arr = []
        gs.history = []
        gs.dead_white = []
        gs.dead_black = []
        gs.game_over = False
        gs.is_draw = False
        gs.check = False
        gs.promotion_pending = None
        gs.move_log = []

        parts = fen.strip().split()
        placement = parts[0]
        gs.turn = "white" if parts[1] == "w" else "black"
        castling_str = parts[2] if len(parts) > 2 else "-"
        ep_str = parts[3] if len(parts) > 3 else "-"
        gs.halfmove_clock = int(parts[4]) if len(parts) > 4 else 0
        gs.fullmove_number = int(parts[5]) if len(parts) > 5 else 1

        # Parse placement
        rows = placement.split("/")
        for r, row_str in enumerate(rows):
            c = 0
            for ch in row_str:
                if ch.isdigit():
                    c += int(ch)
                else:
                    cls_name, color = FEN_PIECE_MAP[ch]
                    piece_cls = PIECE_CLASS_MAP[cls_name]
                    p = piece_cls(r, c, color)
                    gs.pieces_arr.append(p)
                    c += 1

        # Set has_moved based on castling rights
        for p in gs.pieces_arr:
            p.has_moved = True  # Assume all have moved

        if 'K' in castling_str:
            wk = gs.get_king("white")
            if wk:
                wk.has_moved = False
            wr_k = functions.get_piece((7, 7), gs.pieces_arr)
            if wr_k:
                wr_k.has_moved = False
        if 'Q' in castling_str:
            wk = gs.get_king("white")
            if wk:
                wk.has_moved = False
            wr_q = functions.get_piece((7, 0), gs.pieces_arr)
            if wr_q:
                wr_q.has_moved = False
        if 'k' in castling_str:
            bk = gs.get_king("black")
            if bk:
                bk.has_moved = False
            br_k = functions.get_piece((0, 7), gs.pieces_arr)
            if br_k:
                br_k.has_moved = False
        if 'q' in castling_str:
            bk = gs.get_king("black")
            if bk:
                bk.has_moved = False
            br_q = functions.get_piece((0, 0), gs.pieces_arr)
            if br_q:
                br_q.has_moved = False

        # Set has_moved = False for pawns on their starting rank
        for p in gs.pieces_arr:
            if p.piece_type == "pawn":
                if (p.color == "white" and p.row == 6) or (p.color == "black" and p.row == 1):
                    p.has_moved = False

        # En passant — reconstruct last_move if needed
        gs.last_move = None
        if ep_str != "-":
            ep_col = ord(ep_str[0]) - ord('a')
            ep_rank = 8 - int(ep_str[1])
            # The pawn that made the double push
            if gs.turn == "white":
                # Black just moved, pawn is at ep_rank + 1
                pawn_row = ep_rank + 1
                pawn_start = (ep_rank - 1, ep_col)
            else:
                pawn_row = ep_rank - 1
                pawn_start = (ep_rank + 1, ep_col)
            for p in gs.pieces_arr:
                if p.alive and p.piece_type == "pawn" and p.row == pawn_row and p.col == ep_col:
                    gs.last_move = (p, pawn_start, (pawn_row, ep_col))
                    break

        functions.place_pieces(gs.board, gs.pieces_arr)
        gs.check = gs.is_check()
        logger.info(f"Loaded FEN: {fen}")
        return gs

    def to_move_notation(self, piece: pieces.Piece, start: tuple[int, int],
                          end: tuple[int, int], is_capture: bool) -> str:
        """Generate algebraic notation for a move."""
        files = 'abcdefgh'
        end_sq = files[end[1]] + str(8 - end[0])

        # Castling
        if piece.piece_type == "king" and abs(start[1] - end[1]) == 2:
            return "O-O" if end[1] == 6 else "O-O-O"

        # Piece prefix
        prefix_map = {
            'king': 'K', 'queen': 'Q', 'rook': 'R',
            'bishop': 'B', 'knight': 'N', 'pawn': ''
        }
        prefix = prefix_map.get(piece.piece_type, '')

        # Pawn captures include file
        cap = "x" if is_capture else ""
        if piece.piece_type == "pawn" and is_capture:
            prefix = files[start[1]]

        return f"{prefix}{cap}{end_sq}"
