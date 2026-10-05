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
            PIECE_IMAGES[symbol] = pygame.transform.smoothscale(img, (config.SQ_SIZE, config.SQ_SIZE))
            PIECE_IMAGES[f"{symbol}_small"] = pygame.transform.smoothscale(img, (32, 32))
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
    pygame.draw.rect(screen, (50, 50, 50), panel_rect)
    
    turn_text = f"{gs.turn.capitalize()} to move"
    turn_surf = font.render(turn_text, True, pygame.Color("white"))
    screen.blit(turn_surf, (panel_rect.x + 10, 10))
    
    # Dead White
    x_offset, y_offset = 10, 50
    for dp in gs.dead_white:
        sym = functions.SYM_TO_EMOJI_DICT[str(dp)]
        if f"{sym}_small" in PIECE_IMAGES:
            screen.blit(PIECE_IMAGES[f"{sym}_small"], (panel_rect.x + x_offset, y_offset))
        x_offset += 16
        if x_offset > config.PANEL_WIDTH - 32:
            x_offset = 10
            y_offset += 32
            
    # Dead Black
    x_offset, y_offset = 10, config.HEIGHT - 150
    pygame.draw.line(screen, (100, 100, 100), (panel_rect.x + 10, y_offset - 10), (panel_rect.right - 10, y_offset - 10))
    for dp in gs.dead_black:
        sym = functions.SYM_TO_EMOJI_DICT[str(dp)]
        if f"{sym}_small" in PIECE_IMAGES:
            screen.blit(PIECE_IMAGES[f"{sym}_small"], (panel_rect.x + x_offset, y_offset))
        x_offset += 16
        if x_offset > config.PANEL_WIDTH - 32:
            x_offset = 10
            y_offset += 32
            
    # Buttons
    btn_x = panel_rect.x + 10
    btn_w = config.PANEL_WIDTH - 20
    btn_h = 35
    
    btn_ai_toggle = pygame.Rect(btn_x, config.HEIGHT // 2 - 45, btn_w, btn_h)
    pygame.draw.rect(screen, (80, 120, 150), btn_ai_toggle, border_radius=5)
    toggle_text = font.render(f"AI: {'ON' if ai_enabled else 'OFF'}", True, pygame.Color('white'))
    screen.blit(toggle_text, toggle_text.get_rect(center=btn_ai_toggle.center))
    
    btn_ai_depth = pygame.Rect(btn_x, config.HEIGHT // 2, btn_w, btn_h)
    pygame.draw.rect(screen, (80, 120, 150), btn_ai_depth, border_radius=5)
    depth_text = font.render(f"AI Depth: {ai_depth}", True, pygame.Color('white'))
    screen.blit(depth_text, depth_text.get_rect(center=btn_ai_depth.center))
    
    btn_restart = pygame.Rect(btn_x, config.HEIGHT // 2 + 45, btn_w, btn_h)
    pygame.draw.rect(screen, (200, 80, 80), btn_restart, border_radius=5)
    restart_text = font.render("Restart Game", True, pygame.Color('white'))
    screen.blit(restart_text, restart_text.get_rect(center=btn_restart.center))
    
    return btn_ai_toggle, btn_ai_depth, btn_restart

def main() -> None:
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Chess - HackED 2026")
    clock = pygame.time.Clock()
    
    load_images()
    
    ui_font = pygame.font.SysFont("Arial", 18, True)
    large_font = pygame.font.SysFont("Arial", 32, True)

    gs = GameState()
    AI_ENABLED = True
    AI_COLOR = "black"
    ai_depth = 2

    sq_selected = ()
    player_clicks = []
    valid_moves_for_sq = []
    btn_game_over_restart = pygame.Rect(0,0,0,0)

    while True:
        # AI Move logic
        if not gs.game_over and AI_ENABLED and gs.turn == AI_COLOR and not gs.promotion_pending:
            gs.make_ai_move(ai_depth)
            # Clear selection if AI moves
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
                    
                # Handle Promotion UI
                if gs.promotion_pending:
                    p_opts = ['Q', 'R', 'B', 'N']
                    menu_w, menu_h = 300, 100
                    menu_rect = pygame.Rect(config.WIDTH//2 - menu_w//2, config.HEIGHT//2 - menu_h//2, menu_w, menu_h)
                    for i, p in enumerate(p_opts):
                        rect = pygame.Rect(menu_rect.x + 20 + i*65, menu_rect.y + (menu_h - config.SQ_SIZE)//2, config.SQ_SIZE, config.SQ_SIZE)
                        if rect.collidepoint(location):
                            full_name = {'Q':'Queen', 'R':'Rook', 'B':'Bishop', 'N':'Knight'}[p]
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
        
        if gs.promotion_pending:
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            menu_w, menu_h = 300, 100
            menu_rect = pygame.Rect(config.WIDTH//2 - menu_w//2, config.HEIGHT//2 - menu_h//2, menu_w, menu_h)
            pygame.draw.rect(screen, (200, 200, 200), menu_rect, border_radius=10)
            pygame.draw.rect(screen, (50, 50, 50), menu_rect, 2, border_radius=10)
            
            p_opts = ['Q', 'R', 'B', 'N']
            prefix = 'w' if gs.promotion_pending['color'] == 'white' else 'b'
            for i, p in enumerate(p_opts):
                rect = pygame.Rect(menu_rect.x + 20 + i*65, menu_rect.y + (menu_h - config.SQ_SIZE)//2, config.SQ_SIZE, config.SQ_SIZE)
                img_key = f"{prefix}{p}"
                if img_key in PIECE_IMAGES:
                    screen.blit(PIECE_IMAGES[img_key], rect)

        if gs.game_over:
            text = "Draw by Stalemate/Repetition!" if gs.is_draw else f"Checkmate! {'Black' if gs.turn == 'white' else 'White'} wins!"
            text_surf = large_font.render(text, True, pygame.Color('white'))
            
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            bg_rect = pygame.Rect(0, 0, text_surf.get_width() + 40, text_surf.get_height() + 40)
            bg_rect.center = (config.WIDTH // 2, config.HEIGHT // 2 - 20)
            pygame.draw.rect(screen, (50, 50, 50), bg_rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2, border_radius=10)
            
            text_rect = text_surf.get_rect(center=bg_rect.center)
            screen.blit(text_surf, text_rect)
            
            btn_game_over_restart = pygame.Rect(0, 0, 120, 40)
            btn_game_over_restart.center = (config.WIDTH // 2, config.HEIGHT // 2 + 50)
            pygame.draw.rect(screen, (100, 200, 100), btn_game_over_restart, border_radius=5)
            btn_text = ui_font.render("New Game", True, pygame.Color('black'))
            screen.blit(btn_text, btn_text.get_rect(center=btn_game_over_restart.center))
            
        pygame.display.flip()
        clock.tick(config.MAX_FPS)

if __name__ == "__main__":
    main()