import pygame
import sys
import functions
import pieces
import download_assets
from game_state import GameState
import config

# Ensure image assets exist before GUI init
download_assets.ensure_assets()

pygame.init()

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
            surf = pygame.transform.smoothscale(img, (config.SQ_SIZE, config.SQ_SIZE))
            surf_small = pygame.transform.smoothscale(img, (26, 26))
            PIECE_IMAGES[symbol] = surf
            PIECE_IMAGES[filename] = surf
            PIECE_IMAGES[f"{symbol}_small"] = surf_small
            PIECE_IMAGES[f"{filename}_small"] = surf_small
        except Exception as e:
            print(f"Error loading image {filename}: {e}")

def draw_board(screen: pygame.Surface, font: pygame.font.Font) -> None:
    colors = [config.COLOR_LIGHT, config.COLOR_DARK]
    for row in range(config.DIMENSION):
        for col in range(config.DIMENSION):
            color = colors[((row + col) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(config.MARGIN_LEFT + col*config.SQ_SIZE, row*config.SQ_SIZE, config.SQ_SIZE, config.SQ_SIZE))
            
    text_color = pygame.Color('black')
    for r in range(config.DIMENSION):
        rank_text = font.render(str(8 - r), True, text_color)
        screen.blit(rank_text, (config.MARGIN_LEFT // 4, r * config.SQ_SIZE + config.SQ_SIZE // 2 - rank_text.get_height() // 2))
        
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    for c in range(config.DIMENSION):
        file_text = font.render(files[c], True, text_color)
        screen.blit(file_text, (config.MARGIN_LEFT + c * config.SQ_SIZE + config.SQ_SIZE // 2 - file_text.get_width() // 2, config.DIMENSION * config.SQ_SIZE + 5))

def draw_highlights(screen: pygame.Surface, selected_sq: tuple[int, int] | None, valid_moves: list[tuple[int, int]], last_move: tuple | None, king_in_check_sq: tuple[int, int] | None) -> None:
    if last_move:
        _, start, end = last_move
        s = pygame.Surface((config.SQ_SIZE, config.SQ_SIZE))
        s.set_alpha(100)
        s.fill(config.COLOR_LAST_MOVE)
        screen.blit(s, (config.MARGIN_LEFT + start[1]*config.SQ_SIZE, start[0]*config.SQ_SIZE))
        screen.blit(s, (config.MARGIN_LEFT + end[1]*config.SQ_SIZE, end[0]*config.SQ_SIZE))
        
    if king_in_check_sq:
        s = pygame.Surface((config.SQ_SIZE, config.SQ_SIZE))
        s.set_alpha(150)
        s.fill(config.COLOR_CHECK)
        screen.blit(s, (config.MARGIN_LEFT + king_in_check_sq[1]*config.SQ_SIZE, king_in_check_sq[0]*config.SQ_SIZE))

    if selected_sq:
        row, col = selected_sq
        s = pygame.Surface((config.SQ_SIZE, config.SQ_SIZE))
        s.set_alpha(100)
        s.fill(config.COLOR_HIGHLIGHT)
        screen.blit(s, (config.MARGIN_LEFT + col*config.SQ_SIZE, row*config.SQ_SIZE))
        for mr, mc in valid_moves:
            pygame.draw.circle(screen, config.COLOR_HIGHLIGHT, (config.MARGIN_LEFT + mc*config.SQ_SIZE + config.SQ_SIZE//2, mr*config.SQ_SIZE + config.SQ_SIZE//2), config.SQ_SIZE//6)

def draw_pieces(screen: pygame.Surface, board: list[list]) -> None:
    for row in range(config.DIMENSION):
        for col in range(config.DIMENSION):
            piece = board[row][col]
            if piece != 0 and piece in PIECE_IMAGES:
                screen.blit(PIECE_IMAGES[piece], pygame.Rect(config.MARGIN_LEFT + col*config.SQ_SIZE, row*config.SQ_SIZE, config.SQ_SIZE, config.SQ_SIZE))

def draw_panel(screen: pygame.Surface, gs: GameState, font: pygame.font.Font, ai_enabled: bool, ai_depth: int) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect]:
    panel_rect = pygame.Rect(config.MARGIN_LEFT + config.DIMENSION * config.SQ_SIZE, 0, config.PANEL_WIDTH, config.HEIGHT)
    pygame.draw.rect(screen, (40, 44, 52), panel_rect)
    
    # Header Status
    if gs.game_over:
        if gs.is_draw:
            status_text = "Draw (Stalemate)"
            status_color = (255, 215, 0)
        else:
            winner = "Black" if gs.turn == "white" else "White"
            status_text = f"{winner} Wins!"
            status_color = (100, 255, 100)
    elif gs.check:
        status_text = f"{gs.turn.capitalize()} in Check!"
        status_color = (255, 100, 100)
    else:
        status_text = f"{gs.turn.capitalize()} to move"
        status_color = (255, 255, 255)

    status_surf = font.render(status_text, True, status_color)
    screen.blit(status_surf, (panel_rect.x + 12, 12))
    
    # Subtitle / Move count
    move_info = f"Move {gs.fullmove_number}"
    sub_surf = pygame.font.SysFont("Arial", 12).render(move_info, True, (170, 178, 190))
    screen.blit(sub_surf, (panel_rect.x + 12, 34))

    # Captured White Pieces (captured by Black)
    cap_title_w = pygame.font.SysFont("Arial", 11, True).render("CAPTURED WHITE", True, (150, 150, 150))
    screen.blit(cap_title_w, (panel_rect.x + 12, 54))
    x_offset, y_offset = 12, 70
    for dp in gs.dead_white:
        sym = functions.SYM_TO_EMOJI_DICT[str(dp)]
        if f"{sym}_small" in PIECE_IMAGES:
            screen.blit(PIECE_IMAGES[f"{sym}_small"], (panel_rect.x + x_offset, y_offset))
        x_offset += 20
        if x_offset > config.PANEL_WIDTH - 30:
            x_offset = 12
            y_offset += 26
            
    # Captured Black Pieces (captured by White)
    cap_title_b = pygame.font.SysFont("Arial", 11, True).render("CAPTURED BLACK", True, (150, 150, 150))
    screen.blit(cap_title_b, (panel_rect.x + 12, 130))
    x_offset, y_offset = 12, 146
    for dp in gs.dead_black:
        sym = functions.SYM_TO_EMOJI_DICT[str(dp)]
        if f"{sym}_small" in PIECE_IMAGES:
            screen.blit(PIECE_IMAGES[f"{sym}_small"], (panel_rect.x + x_offset, y_offset))
        x_offset += 20
        if x_offset > config.PANEL_WIDTH - 30:
            x_offset = 12
            y_offset += 26

    # Recent Move History
    history_box = pygame.Rect(panel_rect.x + 10, 210, config.PANEL_WIDTH - 20, 175)
    pygame.draw.rect(screen, (30, 33, 40), history_box, border_radius=6)
    pygame.draw.rect(screen, (60, 65, 75), history_box, 1, border_radius=6)
    
    hist_title = pygame.font.SysFont("Arial", 11, True).render("MOVE HISTORY", True, (160, 170, 185))
    screen.blit(hist_title, (history_box.x + 8, history_box.y + 6))
    
    # Render last 6 moves
    log_font = pygame.font.SysFont("Arial", 12)
    start_idx = max(0, len(gs.move_log) - 10)
    recent = gs.move_log[start_idx:]
    
    # Pair moves: "1. e4 e5", "2. Nf3 Nc6"
    lines = []
    i = 0
    while i < len(recent):
        abs_move_idx = start_idx + i
        move_num = (abs_move_idx // 2) + 1
        if abs_move_idx % 2 == 0:
            # White move
            w_move = recent[i]
            b_move = recent[i+1] if (i + 1 < len(recent)) else ""
            lines.append(f"{move_num}. {w_move}  {b_move}".strip())
            i += 2
        else:
            # Started on Black move
            lines.append(f"{move_num}... {recent[i]}")
            i += 1
            
    y_line = history_box.y + 26
    for line in lines[-6:]:
        line_surf = log_font.render(line, True, (220, 225, 230))
        screen.blit(line_surf, (history_box.x + 10, y_line))
        y_line += 22

    # Bottom Control Buttons
    btn_x = panel_rect.x + 10
    btn_w = config.PANEL_WIDTH - 20
    btn_h = 34
    
    btn_ai_toggle = pygame.Rect(btn_x, config.HEIGHT - 135, btn_w, btn_h)
    ai_btn_color = (60, 120, 180) if ai_enabled else (85, 90, 100)
    pygame.draw.rect(screen, ai_btn_color, btn_ai_toggle, border_radius=6)
    toggle_text = font.render(f"AI: {'ON' if ai_enabled else 'OFF'}", True, pygame.Color('white'))
    screen.blit(toggle_text, toggle_text.get_rect(center=btn_ai_toggle.center))
    
    btn_ai_depth = pygame.Rect(btn_x, config.HEIGHT - 92, btn_w, btn_h)
    pygame.draw.rect(screen, (70, 80, 95), btn_ai_depth, border_radius=6)
    depth_text = font.render(f"AI Depth: {ai_depth}", True, pygame.Color('white'))
    screen.blit(depth_text, depth_text.get_rect(center=btn_ai_depth.center))
    
    btn_restart = pygame.Rect(btn_x, config.HEIGHT - 49, btn_w, btn_h)
    pygame.draw.rect(screen, (180, 60, 60), btn_restart, border_radius=6)
    restart_text = font.render("Restart Game", True, pygame.Color('white'))
    screen.blit(restart_text, restart_text.get_rect(center=btn_restart.center))
    
    return btn_ai_toggle, btn_ai_depth, btn_restart

def main() -> None:
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Chess - HackED 2026")
    clock = pygame.time.Clock()
    
    load_images()
    
    ui_font = pygame.font.SysFont("Arial", 16, True)
    large_font = pygame.font.SysFont("Arial", 30, True)

    gs = GameState()
    AI_ENABLED = True
    AI_COLOR = "black"
    ai_depth = 2

    sq_selected = ()
    player_clicks = []
    valid_moves_for_sq = []
    btn_game_over_restart = pygame.Rect(0, 0, 0, 0)

    while True:
        # AI Move logic
        if not gs.game_over and AI_ENABLED and gs.turn == AI_COLOR and not gs.promotion_pending:
            gs.make_ai_move(ai_depth)
            sq_selected = ()
            player_clicks = []
            valid_moves_for_sq = []
            
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: ai_depth = 1
                elif e.key == pygame.K_2: ai_depth = 2
                elif e.key == pygame.K_3: ai_depth = 3
            
            elif e.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos()
                
                # Check UI Panel buttons
                panel_rect = pygame.Rect(config.MARGIN_LEFT + config.DIMENSION * config.SQ_SIZE, 0, config.PANEL_WIDTH, config.HEIGHT)
                if location[0] >= panel_rect.x:
                    btn_ai_toggle, btn_ai_depth, btn_restart = draw_panel(screen, gs, ui_font, AI_ENABLED, ai_depth)
                    if btn_ai_toggle.collidepoint(location):
                        AI_ENABLED = not AI_ENABLED
                    elif btn_ai_depth.collidepoint(location):
                        ai_depth = (ai_depth % 3) + 1
                    elif btn_restart.collidepoint(location):
                        gs.reset()
                        sq_selected = ()
                        player_clicks = []
                        valid_moves_for_sq = []
                    continue
                    
                if gs.game_over and btn_game_over_restart.collidepoint(location):
                    gs.reset()
                    sq_selected = ()
                    player_clicks = []
                    valid_moves_for_sq = []
                    continue
                    
                if gs.game_over or (AI_ENABLED and gs.turn == AI_COLOR):
                    continue
                    
                # Handle Promotion UI clicks
                if gs.promotion_pending:
                    menu_w, menu_h = 320, 130
                    menu_rect = pygame.Rect(config.WIDTH//2 - menu_w//2, config.HEIGHT//2 - menu_h//2, menu_w, menu_h)
                    p_opts = [('Q', 'Queen'), ('R', 'Rook'), ('B', 'Bishop'), ('N', 'Knight')]
                    for i, (p, full_name) in enumerate(p_opts):
                        tile_rect = pygame.Rect(menu_rect.x + 16 + i * 72, menu_rect.y + 40, 68, 76)
                        if tile_rect.collidepoint(location):
                            gs.complete_promotion(full_name)
                            break
                    continue
                    
                # Handle Board clicks
                col = (location[0] - config.MARGIN_LEFT) // config.SQ_SIZE
                row = location[1] // config.SQ_SIZE
                
                if not (0 <= col < config.DIMENSION and 0 <= row < config.DIMENSION):
                    continue 
                
                if sq_selected == (row, col):
                    sq_selected = ()
                    player_clicks = []
                    valid_moves_for_sq = []
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)
                
                if len(player_clicks) == 1:
                    start_coords = player_clicks[0]
                    piece = functions.get_piece(start_coords, gs.pieces_arr)
                    if piece and piece.color == gs.turn:
                        valid_moves_for_sq = gs.get_legal_moves_for_piece(piece)
                    else:
                        sq_selected = ()
                        player_clicks = []
                        valid_moves_for_sq = []
                        
                elif len(player_clicks) == 2:
                    start_coords = player_clicks[0]
                    end_coords = player_clicks[1]
                    
                    if end_coords in valid_moves_for_sq:
                        gs.make_move(start_coords, end_coords)
                            
                    sq_selected = ()
                    player_clicks = []
                    valid_moves_for_sq = []
            
        screen.fill(pygame.Color('darkgray'))
        draw_board(screen, ui_font)
        
        king_in_check_sq = None
        if gs.check:
            k = gs.get_king(gs.turn)
            if k: king_in_check_sq = (k.row, k.col)
            
        draw_highlights(screen, sq_selected, valid_moves_for_sq, gs.last_move, king_in_check_sq)
        draw_pieces(screen, gs.board)
        btn_ai_toggle, btn_ai_depth, btn_restart = draw_panel(screen, gs, ui_font, AI_ENABLED, ai_depth)
        
        # Draw Promotion Modal
        if gs.promotion_pending:
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT))
            overlay.set_alpha(160)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            menu_w, menu_h = 320, 130
            menu_rect = pygame.Rect(config.WIDTH//2 - menu_w//2, config.HEIGHT//2 - menu_h//2, menu_w, menu_h)
            pygame.draw.rect(screen, (245, 245, 245), menu_rect, border_radius=12)
            pygame.draw.rect(screen, (40, 44, 52), menu_rect, 3, border_radius=12)
            
            title_text = ui_font.render("Choose Promotion Piece:", True, pygame.Color('black'))
            screen.blit(title_text, title_text.get_rect(center=(menu_rect.centerx, menu_rect.y + 20)))
            
            p_opts = [('Q', 'Queen'), ('R', 'Rook'), ('B', 'Bishop'), ('N', 'Knight')]
            prefix = 'w' if gs.promotion_pending['color'] == 'white' else 'b'
            mouse_pos = pygame.mouse.get_pos()
            
            for i, (p, label) in enumerate(p_opts):
                tile_rect = pygame.Rect(menu_rect.x + 16 + i * 72, menu_rect.y + 40, 68, 76)
                is_hover = tile_rect.collidepoint(mouse_pos)
                tile_bg = (210, 230, 250) if is_hover else (255, 255, 255)
                pygame.draw.rect(screen, tile_bg, tile_rect, border_radius=8)
                pygame.draw.rect(screen, (60, 120, 180) if is_hover else (190, 195, 205), tile_rect, 2, border_radius=8)
                
                img_key = f"{prefix}{p}"
                if img_key in PIECE_IMAGES:
                    piece_img = pygame.transform.smoothscale(PIECE_IMAGES[img_key], (46, 46))
                    screen.blit(piece_img, (tile_rect.x + 11, tile_rect.y + 6))
                    
                lbl_surf = pygame.font.SysFont("Arial", 11, True).render(label, True, pygame.Color('black'))
                screen.blit(lbl_surf, lbl_surf.get_rect(center=(tile_rect.centerx, tile_rect.bottom - 12)))

        # Draw Game Over Overlay
        if gs.game_over:
            text = "Draw by Stalemate/Repetition!" if gs.is_draw else f"Checkmate! {'Black' if gs.turn == 'white' else 'White'} wins!"
            text_surf = large_font.render(text, True, pygame.Color('white'))
            
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT))
            overlay.set_alpha(160)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            bg_rect = pygame.Rect(0, 0, text_surf.get_width() + 50, text_surf.get_height() + 50)
            bg_rect.center = (config.WIDTH // 2, config.HEIGHT // 2 - 20)
            pygame.draw.rect(screen, (40, 44, 52), bg_rect, border_radius=12)
            pygame.draw.rect(screen, (220, 225, 235), bg_rect, 2, border_radius=12)
            
            text_rect = text_surf.get_rect(center=bg_rect.center)
            screen.blit(text_surf, text_rect)
            
            btn_game_over_restart = pygame.Rect(0, 0, 130, 40)
            btn_game_over_restart.center = (config.WIDTH // 2, config.HEIGHT // 2 + 55)
            pygame.draw.rect(screen, (60, 160, 80), btn_game_over_restart, border_radius=6)
            btn_text = ui_font.render("New Game", True, pygame.Color('white'))
            screen.blit(btn_text, btn_text.get_rect(center=btn_game_over_restart.center))
            
        pygame.display.flip()
        clock.tick(config.MAX_FPS)

if __name__ == "__main__":
    main()
