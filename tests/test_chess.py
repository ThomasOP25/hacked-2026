"""Comprehensive tests for the chess engine and UI."""
from __future__ import annotations
import sys
import os

# Add parent directory to path so we can import the game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pieces
import functions
import ai
import game_state


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


# ─── Castling Tests ─────────────────────────────────────────────────────────

class TestCastling:
    def test_castling_kingside_and_queenside_path_clear(self):
        gs = game_state.GameState()
        for p in gs.pieces_arr:
            if p.alive and p.color == 'white' and (p.col in [1, 2, 3, 5, 6]) and p.row == 7:
                p.alive = False
        functions.place_pieces(gs.board, gs.pieces_arr)
        wk = gs.get_king('white')
        legal = functions.get_strictly_legal_moves(wk, wk, gs.board, gs.pieces_arr, None)
        assert (7, 6) in legal  # Kingside
        assert (7, 2) in legal  # Queenside

    def test_castling_blocked_by_pieces(self, setup_board):
        board, pieces_arr = setup_board
        king = find_king(pieces_arr, "white")
        moves = functions.get_strictly_legal_moves(king, king, board, pieces_arr, None)
        assert (7, 6) not in moves
        assert (7, 2) not in moves

    def test_cannot_castle_if_king_moved(self):
        gs = game_state.GameState()
        for p in gs.pieces_arr:
            if p.alive and p.color == 'white' and (p.col in [1, 2, 3, 5, 6]) and p.row == 7:
                p.alive = False
        wk = gs.get_king('white')
        wk.has_moved = True
        functions.place_pieces(gs.board, gs.pieces_arr)
        legal = functions.get_strictly_legal_moves(wk, wk, gs.board, gs.pieces_arr, None)
        assert (7, 6) not in legal
        assert (7, 2) not in legal

    def test_cannot_castle_if_rook_moved(self):
        gs = game_state.GameState()
        for p in gs.pieces_arr:
            if p.alive and p.color == 'white' and (p.col in [1, 2, 3, 5, 6]) and p.row == 7:
                p.alive = False
        wr_k = functions.get_piece((7, 7), gs.pieces_arr)
        wr_k.has_moved = True
        functions.place_pieces(gs.board, gs.pieces_arr)
        wk = gs.get_king('white')
        legal = functions.get_strictly_legal_moves(wk, wk, gs.board, gs.pieces_arr, None)
        assert (7, 6) not in legal
        assert (7, 2) in legal  # Queenside rook has not moved

    def test_cannot_castle_out_of_check(self):
        gs = game_state.GameState()
        for p in gs.pieces_arr:
            if p.alive and p.color == 'white' and (p.col in [1, 2, 3, 5, 6]) and p.row == 7:
                p.alive = False
        functions.get_piece((6, 4), gs.pieces_arr).alive = False  # e2
        functions.get_piece((1, 4), gs.pieces_arr).alive = False  # e7
        br = pieces.Rook(0, 4, 'black')
        gs.pieces_arr.append(br)
        functions.place_pieces(gs.board, gs.pieces_arr)
        wk = gs.get_king('white')
        legal = functions.get_strictly_legal_moves(wk, wk, gs.board, gs.pieces_arr, None)
        assert (7, 6) not in legal
        assert (7, 2) not in legal

    def test_cannot_castle_through_check(self):
        gs = game_state.GameState()
        for p in gs.pieces_arr:
            if p.alive and p.color == 'white' and (p.col in [1, 2, 3, 5, 6]) and p.row == 7:
                p.alive = False
        functions.get_piece((6, 5), gs.pieces_arr).alive = False  # f2
        functions.get_piece((1, 5), gs.pieces_arr).alive = False  # f7
        br = pieces.Rook(0, 5, 'black')
        gs.pieces_arr.append(br)
        functions.place_pieces(gs.board, gs.pieces_arr)
        wk = gs.get_king('white')
        legal = functions.get_strictly_legal_moves(wk, wk, gs.board, gs.pieces_arr, None)
        assert (7, 6) not in legal
        assert (7, 2) in legal

    def test_cannot_castle_into_check(self):
        gs = game_state.GameState()
        for p in gs.pieces_arr:
            if p.alive and p.color == 'white' and (p.col in [1, 2, 3, 5, 6]) and p.row == 7:
                p.alive = False
        functions.get_piece((6, 6), gs.pieces_arr).alive = False  # g2
        functions.get_piece((1, 6), gs.pieces_arr).alive = False  # g7
        br = pieces.Rook(0, 6, 'black')
        gs.pieces_arr.append(br)
        functions.place_pieces(gs.board, gs.pieces_arr)
        wk = gs.get_king('white')
        legal = functions.get_strictly_legal_moves(wk, wk, gs.board, gs.pieces_arr, None)
        assert (7, 6) not in legal

    def test_queenside_castling_allowed_when_b1_attacked(self):
        """Under FIDE rules, king only crosses d1 and lands on c1; b1 can be attacked."""
        gs = game_state.GameState()
        for p in gs.pieces_arr:
            if p.alive and p.color == 'white' and (p.col in [1, 2, 3, 5, 6]) and p.row == 7:
                p.alive = False
        functions.get_piece((6, 1), gs.pieces_arr).alive = False  # b2
        functions.get_piece((1, 1), gs.pieces_arr).alive = False  # b7
        br = pieces.Rook(0, 1, 'black')
        gs.pieces_arr.append(br)
        functions.place_pieces(gs.board, gs.pieces_arr)
        wk = gs.get_king('white')
        legal = functions.get_strictly_legal_moves(wk, wk, gs.board, gs.pieces_arr, None)
        assert (7, 2) in legal

    def test_cannot_castle_if_enemy_piece_on_rook_square(self):
        gs = game_state.GameState()
        for p in gs.pieces_arr:
            if p.alive and p.color == 'white' and (p.col in [1, 2, 3, 5, 6]) and p.row == 7:
                p.alive = False
        functions.get_piece((7, 0), gs.pieces_arr).alive = False
        enemy_rook = pieces.Rook(7, 0, 'black')
        enemy_rook.has_moved = False
        gs.pieces_arr.append(enemy_rook)
        functions.place_pieces(gs.board, gs.pieces_arr)
        wk = gs.get_king('white')
        legal = functions.get_strictly_legal_moves(wk, wk, gs.board, gs.pieces_arr, None)
        assert (7, 2) not in legal


# ─── En Passant Tests ───────────────────────────────────────────────────────

class TestEnPassant:
    def test_en_passant_valid_immediately(self):
        gs = game_state.GameState.from_fen("rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2")
        wp = functions.get_piece((3, 4), gs.pieces_arr)
        legal = functions.get_strictly_legal_moves(gs.get_king('white'), wp, gs.board, gs.pieces_arr, gs.last_move)
        assert (2, 3) in legal

    def test_en_passant_expires_after_other_move(self):
        gs = game_state.GameState.from_fen("rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2")
        wp = functions.get_piece((3, 4), gs.pieces_arr)
        gs.last_move = (wp, (6, 4), (4, 4))
        legal = functions.get_strictly_legal_moves(gs.get_king('white'), wp, gs.board, gs.pieces_arr, gs.last_move)
        assert (2, 3) not in legal

    def test_en_passant_illegal_if_pinned_to_king(self):
        """Horizontal pin: king and pawn on rank 4, capturing leaves king exposed to enemy rook."""
        board = functions.make_board()
        wk = pieces.King(3, 4, 'white')
        wp = pieces.Pawn(3, 3, 'white')
        bp = pieces.Pawn(3, 2, 'black')
        br = pieces.Rook(3, 0, 'black')
        bk = pieces.King(0, 0, 'black')
        pieces_arr = [wk, wp, bp, br, bk]
        functions.place_pieces(board, pieces_arr)

        last_move = (bp, (1, 2), (3, 2))
        legal = functions.get_strictly_legal_moves(wk, wp, board, pieces_arr, last_move)
        assert (2, 2) not in legal

    def test_en_passant_execution_clears_captured_square(self):
        gs = game_state.GameState.from_fen("rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2")
        bp_d5 = functions.get_piece((3, 3), gs.pieces_arr)
        res = gs.make_move((3, 4), (2, 3))
        assert res is True
        assert not bp_d5.alive
        assert gs.board[3][3] == 0
        assert bp_d5 in gs.dead_black


# ─── Pins and Check Tests ───────────────────────────────────────────────────

class TestPinsAndChecks:
    def test_absolute_pin_piece_cannot_move(self):
        gs = game_state.GameState()
        for p in gs.pieces_arr:
            p.alive = False
        wk = pieces.King(7, 4, 'white')
        wn = pieces.Knight(5, 4, 'white')
        br = pieces.Rook(0, 4, 'black')
        bk = pieces.King(0, 0, 'black')
        gs.pieces_arr = [wk, wn, br, bk]
        functions.place_pieces(gs.board, gs.pieces_arr)
        legal = functions.get_strictly_legal_moves(wk, wn, gs.board, gs.pieces_arr, None)
        assert len(legal) == 0

    def test_double_check_only_king_can_move(self):
        gs = game_state.GameState()
        for p in gs.pieces_arr:
            p.alive = False
        wk = pieces.King(7, 4, 'white')
        wb = pieces.Bishop(6, 4, 'white')
        br = pieces.Rook(0, 4, 'black')
        bb = pieces.Bishop(4, 7, 'black')
        bk = pieces.King(0, 0, 'black')
        gs.pieces_arr = [wk, wb, br, bb, bk]
        functions.place_pieces(gs.board, gs.pieces_arr)
        legal_bishop = functions.get_strictly_legal_moves(wk, wb, gs.board, gs.pieces_arr, None)
        assert len(legal_bishop) == 0

    def test_back_rank_checkmate(self):
        board = functions.make_board()
        wk = pieces.King(7, 4, "white")
        wr = pieces.Rook(0, 0, "white")
        bk = pieces.King(0, 7, "black")
        bp_g = pieces.Pawn(1, 6, "black")
        bp_h = pieces.Pawn(1, 7, "black")
        pieces_arr = [wk, wr, bk, bp_g, bp_h]
        functions.place_pieces(board, pieces_arr)

        assert functions.king_checked(board, bk, pieces_arr) is True
        all_legal = []
        for p in pieces_arr:
            if p.alive and p.color == "black":
                legal = functions.get_strictly_legal_moves(bk, p, board, pieces_arr, None)
                all_legal.extend(legal)
        assert len(all_legal) == 0


# ─── Promotion Tests ────────────────────────────────────────────────────────

class TestPromotion:
    def test_pawn_promotion_flow(self):
        gs = game_state.GameState.from_fen("8/4P3/8/8/8/8/8/4K2k w - - 0 1")
        assert not gs.game_over
        moved = gs.make_move((1, 4), (0, 4))
        assert moved is True
        assert gs.promotion_pending is not None
        gs.complete_promotion("Knight")
        p = functions.get_piece((0, 4), gs.pieces_arr)
        assert p is not None and p.piece_type == "knight"
        assert gs.turn == "black"

    def test_promotion_delivers_check(self):
        gs = game_state.GameState.from_fen("k7/4P3/8/8/8/8/8/4K3 w - - 0 1")
        gs.make_move((1, 4), (0, 4))
        gs.complete_promotion("Queen")
        assert gs.check is True


# ─── Draw Condition Tests ───────────────────────────────────────────────────

class TestDraws:
    def test_stalemate(self):
        gs = game_state.GameState.from_fen("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
        assert gs.game_over is True
        assert gs.is_draw is True
        assert gs.check is False

    def test_insufficient_material_k_vs_k(self):
        gs = game_state.GameState.from_fen("8/8/8/4k3/8/8/4K3/8 w - - 0 1")
        assert gs.is_insufficient_material() is True

    def test_insufficient_material_kb_vs_k(self):
        gs = game_state.GameState.from_fen("8/8/8/4k3/8/8/4KB2/8 w - - 0 1")
        assert gs.is_insufficient_material() is True

    def test_insufficient_material_kn_vs_k(self):
        gs = game_state.GameState.from_fen("8/8/8/4k3/8/8/4KN2/8 w - - 0 1")
        assert gs.is_insufficient_material() is True

    def test_insufficient_material_same_color_bishops(self):
        gs = game_state.GameState.from_fen("5b1k/8/8/8/8/8/8/2B1K3 w - - 0 1")
        assert gs.is_insufficient_material() is True

    def test_opposite_color_bishops_not_insufficient(self):
        gs = game_state.GameState.from_fen("2b4k/8/8/8/8/8/8/2B1K3 w - - 0 1")
        assert gs.is_insufficient_material() is False

    def test_fifty_move_rule(self):
        gs = game_state.GameState.from_fen("8/8/8/4k3/8/8/4K3/8 w - - 100 50")
        assert gs.is_draw is True

    def test_threefold_repetition(self):
        gs = game_state.GameState()
        moves = [
            ((7, 6), (5, 5)), ((0, 6), (2, 5)),  # 1. Nf3 Nf6
            ((5, 5), (7, 6)), ((2, 5), (0, 6)),  # 2. Ng1 Ng8
            ((7, 6), (5, 5)), ((0, 6), (2, 5)),  # 3. Nf3 Nf6
            ((5, 5), (7, 6)), ((2, 5), (0, 6)),  # 4. Ng1 Ng8
        ]
        for s, e in moves:
            gs.make_move(s, e)
        assert gs.is_draw is True
        assert gs.game_over is True


# ─── FEN & Algebraic Notation Tests ─────────────────────────────────────────

class TestFENAndNotation:
    def test_starting_fen_roundtrip(self):
        start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        gs = game_state.GameState.from_fen(start_fen)
        assert gs.to_fen() == start_fen

    def test_fen_checkmate_loaded(self):
        fen = "r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4"
        gs = game_state.GameState.from_fen(fen)
        assert gs.game_over is True
        assert gs.check is True
        assert gs.is_draw is False

    def test_move_notation(self):
        gs = game_state.GameState()
        p_e2 = functions.get_piece((6, 4), gs.pieces_arr)
        assert gs.to_move_notation(p_e2, (6, 4), (4, 4), False) == "e4"
        assert gs.to_move_notation(p_e2, (4, 4), (3, 3), True) == "exd5"
        wk = gs.get_king('white')
        assert gs.to_move_notation(wk, (7, 4), (7, 6), False) == "O-O"
        assert gs.to_move_notation(wk, (7, 4), (7, 2), False) == "O-O-O"


# ─── AI Engine Tests ─────────────────────────────────────────────────────────

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
        wk = pieces.King(7, 0, "white")
        wp = pieces.Pawn(4, 4, "white")
        wp.has_moved = True
        bq = pieces.Queen(3, 5, "black")
        bk = pieces.King(0, 7, "black")
        pieces_arr = [wk, wp, bq, bk]
        functions.place_pieces(board, pieces_arr)

        move = ai.get_best_move(board, pieces_arr, "white", 2, None)
        assert move is not None
        _, end = move
        assert end == (3, 5)

    def test_evaluate_board_starting(self, setup_board):
        board, pieces_arr = setup_board
        score = ai.evaluate_board(pieces_arr, "white")
        assert -50 <= score <= 50


# ─── Headless Pygame UI & New Features Tests ─────────────────────────────────

class TestNewFeatures:
    def test_coordinate_flipping(self):
        import chess
        # Not flipped: (0, 0) -> (0, 0)
        assert chess.board_to_screen(0, 0, False) == (0, 0)
        assert chess.screen_to_board(0, 0, False) == (0, 0)
        assert chess.board_to_screen(7, 4, False) == (7, 4)

        # Flipped: (0, 0) -> (7, 7)
        assert chess.board_to_screen(0, 0, True) == (7, 7)
        assert chess.screen_to_board(7, 7, True) == (0, 0)
        assert chess.board_to_screen(7, 4, True) == (0, 3)
        assert chess.screen_to_board(0, 3, True) == (7, 4)

    def test_undo_move_pvp(self):
        gs = game_state.GameState()
        # Move 1: e4
        assert gs.make_move((6, 4), (4, 4)) is True
        assert gs.turn == "black"
        assert len(gs.fen_history) == 2
        # Undo 1 move in PvP
        assert gs.undo_move(against_ai=False) is True
        assert gs.turn == "white"
        assert len(gs.fen_history) == 1
        p = functions.get_piece((6, 4), gs.pieces_arr)
        assert p is not None and p.piece_type == "pawn"

    def test_undo_move_against_ai(self):
        gs = game_state.GameState()
        # White human moves e4
        assert gs.make_move((6, 4), (4, 4)) is True
        # Black AI moves
        assert gs.make_ai_move(1) is True
        assert gs.turn == "white"
        assert len(gs.fen_history) == 3
        # Undo against AI should roll back 2 plies to White's initial turn
        assert gs.undo_move(against_ai=True) is True
        assert gs.turn == "white"
        assert len(gs.fen_history) == 1

    def test_clocks_and_time_control(self):
        gs = game_state.GameState()
        gs.set_time_control(60)
        assert gs.white_time == 60.0
        assert gs.black_time == 60.0

        # Update clock by 1.5 seconds during White's turn
        flagged = gs.update_clock(1.5)
        assert flagged is False
        assert abs(gs.white_time - 58.5) < 0.01
        assert gs.black_time == 60.0

        # Fast forward White's clock to 0
        flagged = gs.update_clock(60.0)
        assert flagged is True
        assert gs.game_over is True
        assert gs.timed_out_color == "white"

    def test_get_evaluation(self):
        gs = game_state.GameState()
        score = gs.get_evaluation()
        assert -60 <= score <= 60  # Initial board roughly balanced


class TestPygameUI:
    def test_ui_headless_simulation(self):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        import pygame
        import chess
        import config

        pygame.init()
        screen = pygame.Surface((config.WIDTH, config.HEIGHT))
        chess.load_images()
        ui_font = pygame.font.SysFont("Arial", 16, True)

        # 1. Images loaded for both Unicode and string keys
        for key in ['wK', 'wQ', 'wR', 'wB', 'wN', 'wp', 'bK', 'bQ', 'bR', 'bB', 'bN', 'bp']:
            assert key in chess.PIECE_IMAGES
            assert f"{key}_small" in chess.PIECE_IMAGES

        # 2. Game state and moves
        gs = chess.GameState()
        assert not gs.game_over
        assert gs.turn == "white"

        # Simulate e2-e4 move
        e2_piece = functions.get_piece((6, 4), gs.pieces_arr)
        valid = gs.get_legal_moves_for_piece(e2_piece)
        assert (4, 4) in valid
        assert gs.make_move((6, 4), (4, 4)) is True
        assert gs.turn == "black"

        # Render board with Green theme (not flipped)
        screen.fill(pygame.Color('darkgray'))
        chess.draw_eval_bar(screen, gs.get_evaluation(), False, ui_font)
        chess.draw_board(screen, ui_font, 'Green', False)
        chess.draw_pieces(screen, gs.board, False)
        buttons = chess.draw_panel(
            screen, gs, ui_font, True, 1, 'white', 'Green', True, False
        )
        assert 'undo' in buttons
        assert 'flip' in buttons
        assert 'side' in buttons
        assert 'theme' in buttons

        # Render board flipped (playing as Black) with Wood theme
        screen.fill(pygame.Color('darkgray'))
        chess.draw_eval_bar(screen, gs.get_evaluation(), True, ui_font)
        chess.draw_board(screen, ui_font, 'Wood', True)
        chess.draw_pieces(screen, gs.board, True)
        chess.draw_panel(
            screen, gs, ui_font, True, 1, 'black', 'Wood', True, True
        )

        # 3. Promotion pending modal render
        gs_promo = chess.GameState.from_fen("k7/4P3/8/8/8/8/8/4K3 w - - 0 1")
        gs_promo.make_move((1, 4), (0, 4))
        assert gs_promo.promotion_pending is not None
        prefix = 'w' if gs_promo.promotion_pending['color'] == 'white' else 'b'
        for p in ['Q', 'R', 'B', 'N']:
            assert f"{prefix}{p}" in chess.PIECE_IMAGES
