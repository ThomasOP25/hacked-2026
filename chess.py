"""
Defines the core game loop for chess with a Pygame GUI.
"""

import pygame
import sys
import functions
import pieces

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

def draw_board(screen):
    colors = [COLOR_LIGHT, COLOR_DARK]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_highlights(screen, selected_sq, valid_moves):
    if selected_sq:
        row, col = selected_sq
        s = pygame.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100) # transparency
        s.fill(COLOR_HIGHLIGHT)
        screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))
        for move in valid_moves:
            mr, mc = move
            pygame.draw.circle(screen, COLOR_HIGHLIGHT, (mc*SQ_SIZE + SQ_SIZE//2, mr*SQ_SIZE + SQ_SIZE//2), SQ_SIZE//6)

def draw_pieces(screen, board, font):
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

def main():
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

    while True:
        check = False
        functions.place_pieces(board, pieces_arr)
        
        # Check for king check/checkmate
        for piece in pieces_arr:
            if piece.color == turn and isinstance(piece, pieces.King):
                king = piece
        
        if functions.king_checked(board, king, pieces_arr):
            check = True

        legal_moves_for_turn = []
        for p in pieces_arr:
            if p.alive and p.color == turn:
                legal_moves_for_turn += functions.get_strictly_legal_moves(king, p, board, pieces_arr)
        
        if len(legal_moves_for_turn) == 0:
            game_over = True
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif e.type == pygame.MOUSEBUTTONDOWN and not game_over:
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
                        valid_moves = functions.get_strictly_legal_moves(king, piece, board, pieces_arr)
                    else:
                        sq_selected = ()
                        player_clicks = []
                        valid_moves = []
                        
                elif len(player_clicks) == 2:
                    start_coords = player_clicks[0]
                    end_coords = player_clicks[1]
                    
                    if functions.check_end_position(end_coords, valid_moves):
                        piece = functions.get_piece(start_coords, pieces_arr)
                        dead_arr = functions.move_piece(start_coords, end_coords, board, piece, pieces_arr)
                        
                        # Handle Pawn Promotion (Auto-queen for now)
                        if piece.__class__.__name__.lower() == "pawn":
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