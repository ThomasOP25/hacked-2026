from __future__ import annotations

"""
Defines the core game loop for chess with a Pygame GUI.
"""

import pygame
import sys
import functions
import pieces
import ai

# Initialize pygame
pygame.init()

# Constants
WIDTH = 512
HEIGHT = 512
DIMENSION = 8 # 8x8 chess board
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15

# Colors
COLOR_LIGHT = (235, 235, 208)
COLOR_DARK = (119, 149, 86)
COLOR_HIGHLIGHT = (186, 202, 68)

# Map unicode symbols to letters
SYM_TO_TEXT = {
    "\u2654": "K", "\u2655": "Q", "\u2656": "R",
    "\u2657": "B", "\u2658": "N", "\u2659": "P",
    "\u265A": "K", "\u265B": "Q", "\u265C": "R",
    "\u265D": "B", "\u265E": "N", "\u265F": "P"
}

SYM_TO_COLOR = {
    "\u2654": (255, 255, 255), "\u2655": (255, 255, 255), "\u2656": (255, 255, 255),
    "\u2657": (255, 255, 255), "\u2658": (255, 255, 255), "\u2659": (255, 255, 255),
    "\u265A": (0, 0, 0), "\u265B": (0, 0, 0), "\u265C": (0, 0, 0),
    "\u265D": (0, 0, 0), "\u265E": (0, 0, 0), "\u265F": (0, 0, 0)
}

def draw_board(screen: pygame.Surface) -> None:
    colors = [COLOR_LIGHT, COLOR_DARK]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_highlights(screen: pygame.Surface, selected_sq: tuple[int, int] | None, valid_moves: list[tuple[int, int]]) -> None:
    if selected_sq:
        row, col = selected_sq
        s = pygame.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100) # transparency
        s.fill(COLOR_HIGHLIGHT)
        screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))
        for move in valid_moves:
            mr, mc = move
            pygame.draw.circle(screen, COLOR_HIGHLIGHT, (mc*SQ_SIZE + SQ_SIZE//2, mr*SQ_SIZE + SQ_SIZE//2), SQ_SIZE//6)

def draw_pieces(screen: pygame.Surface, board: list[list], font: pygame.font.Font) -> None:
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != 0:
                text = SYM_TO_TEXT.get(piece, "")
                color = SYM_TO_COLOR.get(piece, (0, 0, 0))
                
                # Draw piece text
                text_object = font.render(text, True, color)
                # Shadow/Outline for better visibility
                shadow_object = font.render(text, True, (128, 128, 128))
                
                # Center text in square
                text_rect = text_object.get_rect(center=(col*SQ_SIZE + SQ_SIZE//2, row*SQ_SIZE + SQ_SIZE//2))
                shadow_rect = shadow_object.get_rect(center=(col*SQ_SIZE + SQ_SIZE//2 + 2, row*SQ_SIZE + SQ_SIZE//2 + 2))
                
                screen.blit(shadow_object, shadow_rect)
                screen.blit(text_object, text_rect)

def main() -> None:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess - HackED 2026")
    clock = pygame.time.Clock()
    
    # Initialize font for pieces
    piece_font = pygame.font.SysFont("Arial", 48, True)

    dead_pieces_white = []
    dead_pieces_black = []

    board = functions.make_board()
    pieces_arr = functions.initialize_pieces()

    turn = "white"
    
    sq_selected = () # (row, col)
    player_clicks = [] # [(row, col), (row, col)]
    valid_moves = []
    game_over = False
    
    last_move = None
    halfmove_clock = 0
    history = []
    
    # AI Config
    AI_ENABLED = True
    AI_COLOR = "black"
    ai_depth = 2 # Medium by default

    def get_board_hash(board, turn, pieces_arr, last_move):
        # Include piece positions
        board_str = "".join([str(p) for row in board for p in row])
        # Include turn
        board_str += turn
        # Include castling rights
        for p in pieces_arr:
            if p.alive and (isinstance(p, pieces.King) or isinstance(p, pieces.Rook)):
                board_str += f"{p.piece_type}{p.col}{p.has_moved}"
        # Include en passant target
        if last_move:
            lm_piece, lm_start, lm_end = last_move
            if lm_piece.piece_type == "pawn" and abs(lm_start[0] - lm_end[0]) == 2:
                board_str += f"ep{lm_end[1]}"
        return board_str

    while True:
        check = False
        functions.place_pieces(board, pieces_arr)
        
        # Check for king check/checkmate
        king = None
        for piece in pieces_arr:
            if piece.alive and piece.color == turn and isinstance(piece, pieces.King):
                king = piece
                break
        if king is None:
            # Should never happen in a valid game
            continue
        
        if functions.king_checked(board, king, pieces_arr):
            check = True

        legal_moves_for_turn = []
        for p in pieces_arr:
            if p.alive and p.color == turn:
                legal_moves_for_turn += functions.get_strictly_legal_moves(king, p, board, pieces_arr, last_move)
        
        # 3-Fold Repetition Check
        board_hash = get_board_hash(board, turn, pieces_arr, last_move)
        if len(player_clicks) == 0: # Only check at the start of a turn, before a click
            history.append(board_hash)
        
        is_draw = False
        if history.count(board_hash) >= 3:
            is_draw = True
            
        if halfmove_clock >= 100:
            is_draw = True
            
        if len(legal_moves_for_turn) == 0:
            game_over = True
            is_draw = not check # if no legal moves and not in check -> draw

        if is_draw:
            game_over = True
            
        # AI Turn Handling
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
                continue # Skip event handling for this frame
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    ai_depth = 1
                    print("AI Difficulty set to EASY (Depth 1)")
                elif e.key == pygame.K_2:
                    ai_depth = 2
                    print("AI Difficulty set to MEDIUM (Depth 2)")
                elif e.key == pygame.K_3:
                    ai_depth = 3
                    print("AI Difficulty set to HARD (Depth 3)")
            
            elif e.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if AI_ENABLED and turn == AI_COLOR:
                    continue # Ignore clicks during AI turn
                    
                location = pygame.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                
                if sq_selected == (row, col): # Deselect
                    sq_selected = ()
                    player_clicks = []
                    valid_moves = []
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)
                
                if len(player_clicks) == 1:
                    # check if the selected piece is valid
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
                        
                        # Reset 50-move rule if Pawn moves or capture happens
                        if piece.piece_type == "pawn" or board[end_coords[0]][end_coords[1]] != 0:
                            halfmove_clock = 0
                        else:
                            halfmove_clock += 1
                            
                        dead_arr = functions.move_piece(start_coords, end_coords, board, piece, pieces_arr, last_move)
                        last_move = (piece, start_coords, end_coords)
                        
                        # Handle Pawn Promotion (Auto-queen for now)
                        if piece.piece_type == "pawn":
                            if (piece.color == "white" and piece.row == 0) or (piece.color == "black" and piece.row == 7):
                                piece.alive = False
                                promo = pieces.Queen(piece.row, piece.col, piece.color)
                                pieces_arr.append(promo)

                        functions.update_dead_list(dead_arr, dead_pieces_white, dead_pieces_black)
                        
                        if turn == "white":
                            turn = "black"
                        else:
                            turn = "white"
                            
                    # Reset clicks
                    sq_selected = ()
                    player_clicks = []
                    valid_moves = []
            
        # Draw everything
        draw_board(screen)
        draw_highlights(screen, sq_selected, valid_moves)
        draw_pieces(screen, board, piece_font)
        
        # Draw AI info
        font = pygame.font.SysFont("Helvetica", 16, True, False)
        depth_text = f"AI Depth: {ai_depth} (Press 1/2/3)"
        text_object = font.render(depth_text, True, pygame.Color('Black'))
        screen.blit(text_object, (10, 10))
        
        # Display checkmate text
        if game_over:
            font = pygame.font.SysFont("Helvetica", 32, True, False)
            text = "Checkmate!" if check else "Stalemate!"
            text_object = font.render(text, 0, pygame.Color('Black'))
            
            # Draw text with a background for visibility
            text_bg = pygame.Surface((text_object.get_width() + 20, text_object.get_height() + 20))
            text_bg.fill((200, 200, 200))
            text_bg.set_alpha(200)
            text_bg_rect = text_bg.get_rect(center=(WIDTH/2, HEIGHT/2))
            screen.blit(text_bg, text_bg_rect)
            
            text_location = text_object.get_rect(center=(WIDTH/2, HEIGHT/2))
            screen.blit(text_object, text_location)
            
        pygame.display.flip()
        clock.tick(MAX_FPS)

if __name__ == "__main__":
    main()