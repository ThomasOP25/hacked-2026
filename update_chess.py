import re

with open("chess.py", "r") as f:
    content = f.read()

# 1. Update draw_panel definition
content = content.replace(
    "def draw_panel(screen: pygame.Surface, turn: str, dead_white: list, dead_black: list, font: pygame.font.Font) -> None:",
    "def draw_panel(screen: pygame.Surface, turn: str, dead_white: list, dead_black: list, font: pygame.font.Font, ai_enabled: bool, ai_depth: int) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect]:"
)

# Replace the internal drawing logic for the panel to include buttons
panel_old = """    # Dead Black (captured by White)
    x_offset, y_offset = 10, HEIGHT - 150
    pygame.draw.line(screen, (100, 100, 100), (panel_rect.x + 10, y_offset - 10), (panel_rect.right - 10, y_offset - 10))
    for dp in dead_black:
        sym = functions.SYM_TO_EMOJI_DICT[str(dp)]
        if f"{sym}_small" in PIECE_IMAGES:
            screen.blit(PIECE_IMAGES[f"{sym}_small"], (panel_rect.x + x_offset, y_offset))
        x_offset += 16
        if x_offset > PANEL_WIDTH - 32:
            x_offset = 10
            y_offset += 32"""

panel_new = """    # Dead Black (captured by White)
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
            
    # Draw Buttons
    btn_x = panel_rect.x + 10
    btn_w = PANEL_WIDTH - 20
    btn_h = 35
    
    btn_ai_toggle = pygame.Rect(btn_x, HEIGHT // 2 - 45, btn_w, btn_h)
    pygame.draw.rect(screen, (80, 120, 150), btn_ai_toggle, border_radius=5)
    toggle_text = font.render(f"AI: {'ON' if ai_enabled else 'OFF'}", True, pygame.Color('white'))
    screen.blit(toggle_text, toggle_text.get_rect(center=btn_ai_toggle.center))
    
    btn_ai_depth = pygame.Rect(btn_x, HEIGHT // 2, btn_w, btn_h)
    pygame.draw.rect(screen, (80, 120, 150), btn_ai_depth, border_radius=5)
    depth_text = font.render(f"AI Depth: {ai_depth}", True, pygame.Color('white'))
    screen.blit(depth_text, depth_text.get_rect(center=btn_ai_depth.center))
    
    btn_restart = pygame.Rect(btn_x, HEIGHT // 2 + 45, btn_w, btn_h)
    pygame.draw.rect(screen, (200, 80, 80), btn_restart, border_radius=5)
    restart_text = font.render("Restart Game", True, pygame.Color('white'))
    screen.blit(restart_text, restart_text.get_rect(center=btn_restart.center))
    
    return btn_ai_toggle, btn_ai_depth, btn_restart"""
content = content.replace(panel_old, panel_new)


# 2. Add reset_game and init button rects in main
main_init_old = """    board = functions.make_board()
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
    ai_depth = 2"""

main_init_new = """    btn_ai_toggle = pygame.Rect(0,0,0,0)
    btn_ai_depth = pygame.Rect(0,0,0,0)
    btn_restart = pygame.Rect(0,0,0,0)
    btn_game_over_restart = pygame.Rect(0,0,0,0)
    promotion_state = None
    promo_rects = []

    def reset_game():
        nonlocal board, pieces_arr, turn, sq_selected, player_clicks, valid_moves
        nonlocal game_over, last_move, halfmove_clock, history, dead_pieces_white, dead_pieces_black
        nonlocal promotion_state, check, king_in_check_sq
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
        dead_pieces_white = []
        dead_pieces_black = []
        promotion_state = None
        check = False
        king_in_check_sq = None

    reset_game()
    AI_ENABLED = True
    AI_COLOR = "black"
    ai_depth = 2"""
content = content.replace(main_init_old, main_init_new)

# Skip AI execution if promotion is pending
ai_turn_old = """        if not game_over and AI_ENABLED and turn == AI_COLOR:"""
ai_turn_new = """        if not game_over and AI_ENABLED and turn == AI_COLOR and not promotion_state:"""
content = content.replace(ai_turn_old, ai_turn_new)


# 3. Handle Events (Buttons and Promotion UI)
event_loop_old = """        for e in pygame.event.get():
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
                    continue"""

event_loop_new = """        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: ai_depth = 1
                elif e.key == pygame.K_2: ai_depth = 2
                elif e.key == pygame.K_3: ai_depth = 3
            
            elif e.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos()
                
                if btn_ai_toggle.collidepoint(location):
                    AI_ENABLED = not AI_ENABLED
                    continue
                if btn_ai_depth.collidepoint(location):
                    ai_depth = (ai_depth % 3) + 1
                    continue
                if btn_restart.collidepoint(location) or (game_over and btn_game_over_restart.collidepoint(location)):
                    reset_game()
                    continue

                if game_over or (AI_ENABLED and turn == AI_COLOR):
                    continue
                    
                if promotion_state:
                    for rect, p_type in promo_rects:
                        if rect.collidepoint(location):
                            old_pawn = promotion_state['piece']
                            old_pawn.alive = False
                            p_color = promotion_state['color']
                            p_row, p_col = promotion_state['row'], promotion_state['col']
                            
                            if p_type == 'Q': promo = pieces.Queen(p_row, p_col, p_color)
                            elif p_type == 'R': promo = pieces.Rook(p_row, p_col, p_color)
                            elif p_type == 'B': promo = pieces.Bishop(p_row, p_col, p_color)
                            elif p_type == 'N': promo = pieces.Knight(p_row, p_col, p_color)
                            
                            pieces_arr.append(promo)
                            board[p_row][p_col] = functions.SYM_TO_EMOJI_DICT[str(promo)]
                            
                            functions.update_dead_list(promotion_state['dead_arr'], dead_pieces_white, dead_pieces_black)
                            turn = "black" if turn == "white" else "white"
                            promotion_state = None
                            break
                    continue
                    
                col = (location[0] - MARGIN_LEFT) // SQ_SIZE
                row = location[1] // SQ_SIZE
                
                if not (0 <= col < DIMENSION and 0 <= row < DIMENSION):
                    continue"""
content = content.replace(event_loop_old, event_loop_new)

# 4. Human move logic update for promotion
human_move_old = """                        if piece.piece_type == "pawn":
                            if (piece.color == "white" and piece.row == 0) or (piece.color == "black" and piece.row == 7):
                                piece.alive = False
                                promo = pieces.Queen(piece.row, piece.col, piece.color)
                                pieces_arr.append(promo)

                        functions.update_dead_list(dead_arr, dead_pieces_white, dead_pieces_black)
                        turn = "white" if turn == "black" else "black"
                            
                    sq_selected = ()
                    player_clicks = []
                    valid_moves = []"""

human_move_new = """                        if piece.piece_type == "pawn" and (piece.row == 0 or piece.row == 7):
                            promotion_state = {'piece': piece, 'row': piece.row, 'col': piece.col, 'color': piece.color, 'dead_arr': dead_arr}
                        else:
                            functions.update_dead_list(dead_arr, dead_pieces_white, dead_pieces_black)
                            turn = "white" if turn == "black" else "black"
                            
                    sq_selected = ()
                    player_clicks = []
                    valid_moves = []"""
content = content.replace(human_move_old, human_move_new)


# 5. Drawing Updates
draw_update_old = """        screen.fill(pygame.Color('darkgray'))
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
            screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))"""

draw_update_new = """        screen.fill(pygame.Color('darkgray'))
        draw_board(screen, ui_font)
        draw_highlights(screen, sq_selected, valid_moves, last_move, king_in_check_sq)
        draw_pieces(screen, board)
        btn_ai_toggle, btn_ai_depth, btn_restart = draw_panel(screen, turn, dead_pieces_white, dead_pieces_black, ui_font, AI_ENABLED, ai_depth)
        
        promo_rects = []
        if promotion_state:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            menu_w, menu_h = 300, 100
            menu_rect = pygame.Rect(WIDTH//2 - menu_w//2, HEIGHT//2 - menu_h//2, menu_w, menu_h)
            pygame.draw.rect(screen, (200, 200, 200), menu_rect, border_radius=10)
            pygame.draw.rect(screen, (50, 50, 50), menu_rect, 2, border_radius=10)
            
            p_opts = ['Q', 'R', 'B', 'N']
            prefix = 'w' if promotion_state['color'] == 'white' else 'b'
            for i, p in enumerate(p_opts):
                rect = pygame.Rect(menu_rect.x + 20 + i*65, menu_rect.y + (menu_h - SQ_SIZE)//2, SQ_SIZE, SQ_SIZE)
                promo_rects.append((rect, p))
                img_key = f"{prefix}{p}"
                if img_key in PIECE_IMAGES:
                    screen.blit(PIECE_IMAGES[img_key], rect)

        if game_over:
            text = "Draw by Stalemate/Repetition!" if is_draw else f"Checkmate! {'Black' if turn == 'white' else 'White'} wins!"
            text_surf = large_font.render(text, True, pygame.Color('white'))
            
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            bg_rect = pygame.Rect(0, 0, text_surf.get_width() + 40, text_surf.get_height() + 40)
            bg_rect.center = (WIDTH // 2, HEIGHT // 2 - 20)
            pygame.draw.rect(screen, (50, 50, 50), bg_rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2, border_radius=10)
            
            text_rect = text_surf.get_rect(center=bg_rect.center)
            screen.blit(text_surf, text_rect)
            
            btn_game_over_restart = pygame.Rect(0, 0, 120, 40)
            btn_game_over_restart.center = (WIDTH // 2, HEIGHT // 2 + 50)
            pygame.draw.rect(screen, (100, 200, 100), btn_game_over_restart, border_radius=5)
            btn_text = ui_font.render("New Game", True, pygame.Color('black'))
            screen.blit(btn_text, btn_text.get_rect(center=btn_game_over_restart.center))"""
content = content.replace(draw_update_old, draw_update_new)

with open("chess.py", "w") as f:
    f.write(content)
