"""Tests for the chess engine."""
from __future__ import annotations
import sys
import os

# Add parent directory to path so we can import the game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pieces
import functions
import ai


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def setup_board():
    """Create a fresh board and pieces in starting position."""
    board = functions.make_board()
    pieces_arr = functions.initialize_pieces()
    functions.place_pieces(board, pieces_arr)
    return board, pieces_arr


def find_king(pieces_arr, color):
    for p in pieces_arr:
        if p.alive and p.color == color and isinstance(p, pieces.King):
            return p
    return None


def find_piece_at(pieces_arr, row, col):
    for p in pieces_arr:
        if p.alive and p.row == row and p.col == col:
            return p
    return None


# ─── Move Generation Tests ──────────────────────────────────────────────────

class TestMoveGeneration:
    def test_initial_pawn_moves(self, setup_board):
        board, pieces_arr = setup_board
        # White pawn at (6, 4) — e2
        pawn = find_piece_at(pieces_arr, 6, 4)
        assert pawn is not None
        assert pawn.piece_type == "pawn"
        king = find_king(pieces_arr, "white")
        moves = functions.get_strictly_legal_moves(king, pawn, board, pieces_arr, None)
        assert len(moves) == 2
        assert (5, 4) in moves  # single step
        assert (4, 4) in moves  # double step

    def test_knight_moves(self, setup_board):
        board, pieces_arr = setup_board
        # Knight at (7, 1) — b1
        knight = find_piece_at(pieces_arr, 7, 1)
        assert knight is not None
        king = find_king(pieces_arr, "white")
        moves = functions.get_strictly_legal_moves(king, knight, board, pieces_arr, None)
        assert len(moves) == 2
        assert (5, 0) in moves  # a3
        assert (5, 2) in moves  # c3

    def test_bishop_blocked(self, setup_board):
        board, pieces_arr = setup_board
        # Bishop at (7, 2) — c1
        bishop = find_piece_at(pieces_arr, 7, 2)
        assert bishop is not None
        king = find_king(pieces_arr, "white")
        moves = functions.get_strictly_legal_moves(king, bishop, board, pieces_arr, None)
        assert len(moves) == 0

    def test_rook_blocked(self, setup_board):
        board, pieces_arr = setup_board
        rook = find_piece_at(pieces_arr, 7, 0)
        assert rook is not None
        king = find_king(pieces_arr, "white")
        moves = functions.get_strictly_legal_moves(king, rook, board, pieces_arr, None)
        assert len(moves) == 0

    def test_king_moves_start(self, setup_board):
        board, pieces_arr = setup_board
        king = find_king(pieces_arr, "white")
        moves = functions.get_strictly_legal_moves(king, king, board, pieces_arr, None)
        assert len(moves) == 0


# ─── Special Moves Tests ────────────────────────────────────────────────────

class TestSpecialMoves:
    def test_en_passant(self):
        board = functions.make_board()
        # White pawn on e5, Black pawn on d5 (just moved from d7)
        wp = pieces.Pawn(3, 4, "white")
        wp.has_moved = True
        bp = pieces.Pawn(3, 3, "black")
        bp.has_moved = True
        wk = pieces.King(7, 4, "white")
        bk = pieces.King(0, 4, "black")
        pieces_arr = [wp, bp, wk, bk]
        functions.place_pieces(board, pieces_arr)

        last_move = (bp, (1, 3), (3, 3))  # Black pawn double-stepped
        king = find_king(pieces_arr, "white")
        moves = functions.get_strictly_legal_moves(king, wp, board, pieces_arr, last_move)
        assert (2, 3) in moves  # en passant capture square

    def test_castling_kingside(self):
        board = functions.make_board()
        wk = pieces.King(7, 4, "white")
        wr = pieces.Rook(7, 7, "white")
        bk = pieces.King(0, 4, "black")
        pieces_arr = [wk, wr, bk]
        functions.place_pieces(board, pieces_arr)

        king = find_king(pieces_arr, "white")
        moves = functions.get_strictly_legal_moves(king, king, board, pieces_arr, None)
        assert (7, 6) in moves  # kingside castling

    def test_castling_blocked(self, setup_board):
        board, pieces_arr = setup_board
        # At game start, pieces block castling
        king = find_king(pieces_arr, "white")
        moves = functions.get_strictly_legal_moves(king, king, board, pieces_arr, None)
        assert (7, 6) not in moves
        assert (7, 2) not in moves

    def test_castling_through_check(self):
        board = functions.make_board()
        wk = pieces.King(7, 4, "white")
        wr = pieces.Rook(7, 7, "white")
        # Enemy rook attacks f1 (col 5)
        br = pieces.Rook(0, 5, "black")
        bk = pieces.King(0, 4, "black")
        pieces_arr = [wk, wr, br, bk]
        functions.place_pieces(board, pieces_arr)

        king = find_king(pieces_arr, "white")
        moves = functions.get_strictly_legal_moves(king, king, board, pieces_arr, None)
        assert (7, 6) not in moves

    def test_pawn_promotion_row(self):
        board = functions.make_board()
        wp = pieces.Pawn(1, 4, "white")
        wp.has_moved = True
        wk = pieces.King(7, 4, "white")
        bk = pieces.King(0, 0, "black")
        pieces_arr = [wp, wk, bk]
        functions.place_pieces(board, pieces_arr)

        king = find_king(pieces_arr, "white")
        moves = functions.get_strictly_legal_moves(king, wp, board, pieces_arr, None)
        assert (0, 4) in moves


# ─── Check/Checkmate Tests ──────────────────────────────────────────────────

class TestCheckAndMate:
    def test_king_in_check(self):
        board = functions.make_board()
        wk = pieces.King(7, 4, "white")
        bq = pieces.Queen(5, 4, "black")  # Queen attacks king
        bk = pieces.King(0, 4, "black")
        pieces_arr = [wk, bq, bk]
        functions.place_pieces(board, pieces_arr)

        assert functions.king_checked(board, wk, pieces_arr) is True

    def test_checkmate_back_rank(self):
        """Back rank mate: White Rook delivers checkmate on 8th rank."""
        board = functions.make_board()
        wk = pieces.King(7, 4, "white")
        wr = pieces.Rook(0, 0, "white")  # Ra8 delivers mate
        bk = pieces.King(0, 7, "black")  # Kh8
        bp_g = pieces.Pawn(1, 6, "black")  # g7 blocks escape
        bp_h = pieces.Pawn(1, 7, "black")  # h7 blocks escape
        bp_g.has_moved = False
        bp_h.has_moved = False
        pieces_arr = [wk, wr, bk, bp_g, bp_h]
        functions.place_pieces(board, pieces_arr)

        assert functions.king_checked(board, bk, pieces_arr) is True
        all_legal = []
        for p in pieces_arr:
            if p.alive and p.color == "black":
                legal = functions.get_strictly_legal_moves(bk, p, board, pieces_arr, None)
                all_legal.extend(legal)
        assert len(all_legal) == 0

    def test_stalemate(self):
        board = functions.make_board()
        # K on a8 vs K+Q — classic stalemate setup
        bk = pieces.King(0, 0, "black")  # Ka8
        wk = pieces.King(2, 1, "white")  # Kb6
        wq = pieces.Queen(1, 2, "white")  # Qc7
        pieces_arr = [bk, wk, wq]
        functions.place_pieces(board, pieces_arr)

        assert functions.king_checked(board, bk, pieces_arr) is False
        all_legal = []
        for p in pieces_arr:
            if p.alive and p.color == "black":
                legal = functions.get_strictly_legal_moves(bk, p, board, pieces_arr, None)
                all_legal.extend(legal)
        assert len(all_legal) == 0


# ─── AI Tests ────────────────────────────────────────────────────────────────

class TestAI:
    def test_ai_returns_move(self, setup_board):
        board, pieces_arr = setup_board
        move = ai.get_best_move(board, pieces_arr, "white", 1, None)
        assert move is not None
        start, end = move
        assert len(start) == 2
        assert len(end) == 2

    def test_ai_captures_free_piece(self):
        board = functions.make_board()
        # White king cornered, only legal capture is pawn takes queen
        wk = pieces.King(7, 0, "white")
        wp = pieces.Pawn(4, 4, "white")
        wp.has_moved = True
        # Free black queen diagonally in front of pawn (capture square)
        bq = pieces.Queen(3, 5, "black")
        bk = pieces.King(0, 7, "black")
        pieces_arr = [wk, wp, bq, bk]
        functions.place_pieces(board, pieces_arr)

        move = ai.get_best_move(board, pieces_arr, "white", 2, None)
        assert move is not None
        _, end = move
        assert end == (3, 5)  # pawn captures queen

    def test_evaluate_board_starting(self, setup_board):
        board, pieces_arr = setup_board
        score = ai.evaluate_board(pieces_arr, "white")
        assert -50 <= score <= 50  # Should be roughly equal


# ─── Edge Cases ──────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_get_piece_returns_none(self, setup_board):
        board, pieces_arr = setup_board
        result = functions.get_piece((4, 4), pieces_arr)
        assert result is None

    def test_piece_type_attribute(self):
        assert pieces.Pawn(0, 0, "white").piece_type == "pawn"
        assert pieces.Rook(0, 0, "white").piece_type == "rook"
        assert pieces.Knight(0, 0, "white").piece_type == "knight"
        assert pieces.Bishop(0, 0, "white").piece_type == "bishop"
        assert pieces.Queen(0, 0, "white").piece_type == "queen"
        assert pieces.King(0, 0, "white").piece_type == "king"
