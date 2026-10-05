from __future__ import annotations

"""
Defines the core game loop for chess with a Pygame GUI.
"""

import pygame
import sys
import functions
import pieces
import ai
import download_assets

# Ensure image assets exist before GUI init
download_assets.ensure_assets()

# Initialize pygame
pygame.init()

# Constants
DIMENSION = 8 # 8x8 chess board
SQ_SIZE = 64
MARGIN_LEFT = 30
MARGIN_BOTTOM = 30
PANEL_WIDTH = 200

WIDTH = DIMENSION * SQ_SIZE + MARGIN_LEFT + PANEL_WIDTH
HEIGHT = DIMENSION * SQ_SIZE + MARGIN_BOTTOM
MAX_FPS = 60

# Colors
COLOR_LIGHT = (235, 235, 208)
COLOR_DARK = (119, 149, 86)
COLOR_HIGHLIGHT = (186, 202, 68)
COLOR_LAST_MOVE = (255, 255, 120)
COLOR_CHECK = (255, 100, 100)

PIECE_IMAGES = {}

def load_images() -> None:
    asset_map = {
        "\u2654": "wK", "\u2655": "wQ", "\u2656": "wR",
        "\u2657": "wB", "\u2658": "wN", "\u2659": "wp",
        "\u265A": "bK", "\u265B": "bQ", "\u265C": "bR",
        "\u265D": "bB", "\u265E": "bN", "\u265F": "bp"
    }
    
    for symbol, filename in asset_map.items():
        try:
            img = pygame.image.load(f"assets/images/{filename}.png")
            PIECE_IMAGES[symbol] = pygame.transform.smoothscale(img, (SQ_SIZE, SQ_SIZE))
            PIECE_IMAGES[f"{symbol}_small"] = pygame.transform.smoothscale(img, (32, 32))
        except Exception as e:
            print(f"Error loading image {filename}: {e}")

def draw_board(screen: pygame.Surface, font: pygame.font.Font) -> None:
    colors = [COLOR_LIGHT, COLOR_DARK]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(MARGIN_LEFT + col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
            
    # Draw Labels
    text_color = pygame.Color('black')
    for r in range(DIMENSION):
        rank_text = font.render(str(8 - r), True, text_color)
        screen.blit(rank_text, (MARGIN_LEFT // 4, r * SQ_SIZE + SQ_SIZE // 2 - rank_text.get_height() // 2))
        
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    for c in range(DIMENSION):
        file_text = font.render(files[c], True, text_color)
        screen.blit(file_text, (MARGIN_LEFT + c * SQ_SIZE + SQ_SIZE // 2 - file_text.get_width() // 2, DIMENSION * SQ_SIZE + 5))

def draw_highlights(screen: pygame.Surface, selected_sq: tuple[int, int] | None, valid_moves: list[tuple[int, int]], last_move: tuple | None, king_in_check_sq: tuple[int, int] | None) -> None:
    if last_move:
        _, start, end = last_move
        s = pygame.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(COLOR_LAST_MOVE)
        screen.blit(s, (MARGIN_LEFT + start[1]*SQ_SIZE, start[0]*SQ_SIZE))
        screen.blit(s, (MARGIN_LEFT + end[1]*SQ_SIZE, end[0]*SQ_SIZE))
        
    if king_in_check_sq:
        s = pygame.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(150)
        s.fill(COLOR_CHECK)
        screen.blit(s, (MARGIN_LEFT + king_in_check_sq[1]*SQ_SIZE, king_in_check_sq[0]*SQ_SIZE))

    if selected_sq:
        row, col = selected_sq
        s = pygame.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(COLOR_HIGHLIGHT)
        screen.blit(s, (MARGIN_LEFT + col*SQ_SIZE, row*SQ_SIZE))
        for move in valid_moves:
            mr, mc = move
            pygame.draw.circle(screen, COLOR_HIGHLIGHT, (MARGIN_LEFT + mc*SQ_SIZE + SQ_SIZE//2, mr*SQ_SIZE + SQ_SIZE//2), SQ_SIZE//6)

def draw_pieces(screen: pygame.Surface, board: list[list]) -> None:
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != 0 and piece in PIECE_IMAGES:
                screen.blit(PIECE_IMAGES[piece], pygame.Rect(MARGIN_LEFT + col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_panel(screen: pygame.Surface, turn: str, dead_white: list, dead_black: list, font: pygame.font.Font) -> None:
    panel_rect = pygame.Rect(MARGIN_LEFT + DIMENSION * SQ_SIZE, 0, PANEL_WIDTH, HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), panel_rect)
    
    turn_text = f"{turn.capitalize()} to move"
    turn_surf = font.render(turn_text, True, pygame.Color("white"))
    screen.blit(turn_surf, (panel_rect.x + 10, 10))
    
    # Dead White (captured by Black)
    x_offset, y_offset = 10, 50
    for dp in dead_white:
        sym = functions.SYM_TO_EMOJI_DICT[str(dp)]
        if f"{sym}_small" in PIECE_IMAGES:
            screen.blit(PIECE_IMAGES[f"{sym}_small"], (panel_rect.x + x_offset, y_offset))
        x_offset += 16
        if x_offset > PANEL_WIDTH - 32:
            x_offset = 10
            y_offset += 32
            
    # Dead Black (captured by White)
    x_offset, y_offset = 10, HEIGHT - 150
    pygame.draw.line(screen, (100, 100, 100), (panel_rect.x + 10, y_offset - 10), (panel_rect.right - 10, y_offset - 10))
    for dp in dead_black:
        sym = functions.SYM_TO_EMOJI_DICT[str(dp)]
        if f"{sym}_small" in PIECE_IMAGES:
            screen.blit(PIECE_IMAGES[f"{sym}_small"], (panel_rect.x + x_offset, y_offset))
        x_offset += 16
        if x_offset > PANEL_WIDTH - 32:
            x_offset = 10
            y_offset += 32

def main() -> None:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess - HackED 2026")
    clock = pygame.time.Clock()
    
    load_images()
    
    ui_font = pygame.font.SysFont("Arial", 18, True)
    large_font = pygame.font.SysFont("Arial", 32, True)

    dead_pieces_white = []
    dead_pieces_black = []

    board = functions.make_board()
    pieces_arr = functions.initialize_pieces()

    turn = "white"
    
    sq_selected = ()
    player_clicks = []
    valid_moves = []
    game_over = False
    
    last_move = None
    halfmove_clock = 0
    history = []
    
    AI_ENABLED = True
    AI_COLOR = "black"
    ai_depth = 2

    def get_board_hash(board, turn, pieces_arr, last_move):
        board_str = "".join([str(p) for row in board for p in row])
        board_str += turn
        for p in pieces_arr:
            if p.alive and (isinstance(p, pieces.King) or isinstance(p, pieces.Rook)):
                board_str += f"{p.piece_type}{p.col}{p.has_moved}"
        if last_move:
            lm_piece, lm_start, lm_end = last_move
            if lm_piece.piece_type == "pawn" and abs(lm_start[0] - lm_end[0]) == 2:
                board_str += f"ep{lm_end[1]}"
        return board_str

    while True:
        check = False
        king_in_check_sq = None
        functions.place_pieces(board, pieces_arr)
        
        king = None
        for piece in pieces_arr:
            if piece.alive and piece.color == turn and isinstance(piece, pieces.King):
                king = piece
                break
        if king is None:
            continue
        
        if functions.king_checked(board, king, pieces_arr):
            check = True
            king_in_check_sq = (king.row, king.col)

        legal_moves_for_turn = []
        for p in pieces_arr:
            if p.alive and p.color == turn:
                legal_moves_for_turn += functions.get_strictly_legal_moves(king, p, board, pieces_arr, last_move)
        
        board_hash = get_board_hash(board, turn, pieces_arr, last_move)
        if len(player_clicks) == 0:
            history.append(board_hash)
        
        is_draw = False
        if history.count(board_hash) >= 3 or halfmove_clock >= 100:
            is_draw = True
            
        if len(legal_moves_for_turn) == 0:
            game_over = True
            is_draw = not check

        if is_draw:
            game_over = True
            
        if not game_over and AI_ENABLED and turn == AI_COLOR:
            best_move = ai.get_best_move(board, pieces_arr, AI_COLOR, ai_depth, last_move)
            if best_move:
                start_coords, end_coords = best_move
                piece = functions.get_piece(start_coords, pieces_arr)
                
                if piece.piece_type == "pawn" or board[end_coords[0]][end_coords[1]] != 0:
                    halfmove_clock = 0
                else:
                    halfmove_clock += 1
                    
                dead_arr = functions.move_piece(start_coords, end_coords, board, piece, pieces_arr, last_move)
                last_move = (piece, start_coords, end_coords)
                
                if piece.piece_type == "pawn":
                    if (piece.color == "white" and piece.row == 0) or (piece.color == "black" and piece.row == 7):
                        piece.alive = False
                        promo = pieces.Queen(piece.row, piece.col, piece.color)
                        pieces_arr.append(promo)

                functions.update_dead_list(dead_arr, dead_pieces_white, dead_pieces_black)
                turn = "white" if turn == "black" else "black"
                continue
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: ai_depth = 1
                elif e.key == pygame.K_2: ai_depth = 2
                elif e.key == pygame.K_3: ai_depth = 3
            
            elif e.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if AI_ENABLED and turn == AI_COLOR:
                    continue
                    
                location = pygame.mouse.get_pos()
                col = (location[0] - MARGIN_LEFT) // SQ_SIZE
                row = location[1] // SQ_SIZE
                
                if not (0 <= col < DIMENSION and 0 <= row < DIMENSION):
                    continue 
                
                if sq_selected == (row, col):
                    sq_selected = ()
                    player_clicks = []
                    valid_moves = []
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)
                
                if len(player_clicks) == 1:
                    start_coords = player_clicks[0]
                    if functions.check_start_position(turn, start_coords, pieces_arr):
                        piece = functions.get_piece(start_coords, pieces_arr)
                        valid_moves = functions.get_strictly_legal_moves(king, piece, board, pieces_arr, last_move)
                    else:
                        sq_selected = ()
                        player_clicks = []
                        valid_moves = []
                        
                elif len(player_clicks) == 2:
                    start_coords = player_clicks[0]
                    end_coords = player_clicks[1]
                    
                    if functions.check_end_position(end_coords, valid_moves):
                        piece = functions.get_piece(start_coords, pieces_arr)
                        
                        if piece.piece_type == "pawn" or board[end_coords[0]][end_coords[1]] != 0:
                            halfmove_clock = 0
                        else:
                            halfmove_clock += 1
                            
                        dead_arr = functions.move_piece(start_coords, end_coords, board, piece, pieces_arr, last_move)
                        last_move = (piece, start_coords, end_coords)
                        
                        if piece.piece_type == "pawn":
                            if (piece.color == "white" and piece.row == 0) or (piece.color == "black" and piece.row == 7):
                                piece.alive = False
                                promo = pieces.Queen(piece.row, piece.col, piece.color)
                                pieces_arr.append(promo)

                        functions.update_dead_list(dead_arr, dead_pieces_white, dead_pieces_black)
                        turn = "white" if turn == "black" else "black"
                            
                    sq_selected = ()
                    player_clicks = []
                    valid_moves = []
            
        screen.fill(pygame.Color('darkgray'))
        draw_board(screen, ui_font)
        draw_highlights(screen, sq_selected, valid_moves, last_move, king_in_check_sq)
        draw_pieces(screen, board)
        draw_panel(screen, turn, dead_pieces_white, dead_pieces_black, ui_font)
        
        depth_text = f"AI Depth: {ai_depth} (Press 1/2/3)"
        text_object = ui_font.render(depth_text, True, pygame.Color('black'))
        screen.blit(text_object, (MARGIN_LEFT, HEIGHT - MARGIN_BOTTOM + 5))
        
        if game_over:
            text = "Draw by Stalemate/Repetition!" if is_draw else f"Checkmate! {'Black' if turn == 'white' else 'White'} wins!"
            text_surf = large_font.render(text, True, pygame.Color('white'))
            
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            bg_rect = pygame.Rect(0, 0, text_surf.get_width() + 40, text_surf.get_height() + 40)
            bg_rect.center = (WIDTH // 2, HEIGHT // 2)
            pygame.draw.rect(screen, (50, 50, 50), bg_rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2, border_radius=10)
            
            text_rect = text_surf.get_rect(center=bg_rect.center)
            screen.blit(text_surf, text_rect)
            
            btn_rect = pygame.Rect(0, 0, 120, 40)
            btn_rect.center = (WIDTH // 2, HEIGHT // 2 + 60)
            pygame.draw.rect(screen, (100, 200, 100), btn_rect, border_radius=5)
            btn_text = ui_font.render("New Game", True, pygame.Color('black'))
            screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))
            
        pygame.display.flip()
        clock.tick(MAX_FPS)

if __name__ == "__main__":
    main()