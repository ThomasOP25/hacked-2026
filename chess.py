import pygame
import sys
import functions
import pieces
import download_assets
from game_state import GameState
import config
import sounds

# Ensure image assets exist before GUI init
download_assets.ensure_assets()

pygame.init()
sounds.init_sounds()

PIECE_IMAGES: dict[str, pygame.Surface] = {}

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
            surf_small = pygame.transform.smoothscale(img, (24, 24))
            PIECE_IMAGES[symbol] = surf
            PIECE_IMAGES[filename] = surf
            PIECE_IMAGES[f"{symbol}_small"] = surf_small
            PIECE_IMAGES[f"{filename}_small"] = surf_small
        except Exception as e:
            print(f"Error loading image {filename}: {e}")

def board_to_screen(row: int, col: int, flipped: bool) -> tuple[int, int]:
    return (7 - row, 7 - col) if flipped else (row, col)

def screen_to_board(s_row: int, s_col: int, flipped: bool) -> tuple[int, int]:
    return (7 - s_row, 7 - s_col) if flipped else (s_row, s_col)

def draw_eval_bar(screen: pygame.Surface, eval_score: int, flipped: bool, font: pygame.font.Font) -> None:
    bar_x = 8
    bar_y = 0
    bar_w = config.EVAL_BAR_WIDTH
    bar_h = config.DIMENSION * config.SQ_SIZE

    # Clamp evaluation between -1000 and +1000 centipawns
    clamped = max(-1000, min(1000, eval_score))
    # 0 = Black winning, 1 = White winning
    white_ratio = 0.5 + (clamped / 2000.0)
    
    # If flipped, player is Black (Black on bottom, White on top)
    bottom_ratio = (1.0 - white_ratio) if flipped else white_ratio
    bottom_h = int(bar_h * bottom_ratio)
    top_h = bar_h - bottom_h
    
    top_color = (245, 245, 245) if flipped else (45, 45, 50)
    bottom_color = (45, 45, 50) if flipped else (245, 245, 245)
    
    pygame.draw.rect(screen, top_color, pygame.Rect(bar_x, bar_y, bar_w, top_h))
    pygame.draw.rect(screen, bottom_color, pygame.Rect(bar_x, bar_y + top_h, bar_w, bottom_h))
    pygame.draw.rect(screen, (80, 85, 95), pygame.Rect(bar_x, bar_y, bar_w, bar_h), 1)

def draw_board(screen: pygame.Surface, font: pygame.font.Font, theme_name: str, flipped: bool) -> None:
    light_color, dark_color = config.THEMES.get(theme_name, config.THEMES[config.DEFAULT_THEME])
    
    for s_row in range(config.DIMENSION):
        for s_col in range(config.DIMENSION):
            b_row, b_col = screen_to_board(s_row, s_col, flipped)
            color = light_color if ((b_row + b_col) % 2 == 0) else dark_color
            sq_rect = pygame.Rect(config.MARGIN_LEFT + s_col * config.SQ_SIZE, s_row * config.SQ_SIZE, config.SQ_SIZE, config.SQ_SIZE)
            pygame.draw.rect(screen, color, sq_rect)
            
    # Rank labels (numbers)
    text_color = pygame.Color('black')
    for s_r in range(config.DIMENSION):
        b_r, _ = screen_to_board(s_r, 0, flipped)
        rank_str = str(8 - b_r)
        rank_text = font.render(rank_str, True, text_color)
        screen.blit(rank_text, (config.MARGIN_LEFT - 16, s_r * config.SQ_SIZE + config.SQ_SIZE // 2 - rank_text.get_height() // 2))
        
    # File labels (letters)
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    for s_c in range(config.DIMENSION):
        _, b_c = screen_to_board(0, s_c, flipped)
        file_text = font.render(files[b_c], True, text_color)
        screen.blit(file_text, (config.MARGIN_LEFT + s_c * config.SQ_SIZE + config.SQ_SIZE // 2 - file_text.get_width() // 2, config.DIMENSION * config.SQ_SIZE + 5))

def draw_highlights(screen: pygame.Surface, selected_sq: tuple[int, int] | None, valid_moves: list[tuple[int, int]], last_move: tuple | None, king_in_check_sq: tuple[int, int] | None, gs: GameState, flipped: bool) -> None:
    if last_move:
        _, start, end = last_move
        s = pygame.Surface((config.SQ_SIZE, config.SQ_SIZE))
        s.set_alpha(100)
        s.fill(config.COLOR_LAST_MOVE)
        sr1, sc1 = board_to_screen(start[0], start[1], flipped)
        sr2, sc2 = board_to_screen(end[0], end[1], flipped)
        screen.blit(s, (config.MARGIN_LEFT + sc1 * config.SQ_SIZE, sr1 * config.SQ_SIZE))
        screen.blit(s, (config.MARGIN_LEFT + sc2 * config.SQ_SIZE, sr2 * config.SQ_SIZE))
        
    if king_in_check_sq:
        s = pygame.Surface((config.SQ_SIZE, config.SQ_SIZE))
        s.set_alpha(150)
        s.fill(config.COLOR_CHECK)
        kr, kc = board_to_screen(king_in_check_sq[0], king_in_check_sq[1], flipped)
        screen.blit(s, (config.MARGIN_LEFT + kc * config.SQ_SIZE, kr * config.SQ_SIZE))

    if selected_sq:
        b_row, b_col = selected_sq
        sr, sc = board_to_screen(b_row, b_col, flipped)
        s = pygame.Surface((config.SQ_SIZE, config.SQ_SIZE))
        s.set_alpha(120)
        s.fill(config.COLOR_HIGHLIGHT)
        screen.blit(s, (config.MARGIN_LEFT + sc * config.SQ_SIZE, sr * config.SQ_SIZE))
        
        for mr, mc in valid_moves:
            smr, smc = board_to_screen(mr, mc, flipped)
            center_x = config.MARGIN_LEFT + smc * config.SQ_SIZE + config.SQ_SIZE // 2
            center_y = smr * config.SQ_SIZE + config.SQ_SIZE // 2
            target_piece = functions.get_piece((mr, mc), gs.pieces_arr)
            if target_piece and target_piece.color != gs.turn:
                # Target square has an enemy piece: Draw capture ring
                pygame.draw.circle(screen, config.COLOR_HIGHLIGHT, (center_x, center_y), config.SQ_SIZE // 2 - 2, 4)
            else:
                # Quiet move: Small solid dot
                pygame.draw.circle(screen, config.COLOR_HIGHLIGHT, (center_x, center_y), config.SQ_SIZE // 6)

def draw_pieces(screen: pygame.Surface, board: list[list], flipped: bool) -> None:
    for b_row in range(config.DIMENSION):
        for b_col in range(config.DIMENSION):
            piece = board[b_row][b_col]
            if piece != 0 and piece in PIECE_IMAGES:
                sr, sc = board_to_screen(b_row, b_col, flipped)
                screen.blit(PIECE_IMAGES[piece], pygame.Rect(config.MARGIN_LEFT + sc * config.SQ_SIZE, sr * config.SQ_SIZE, config.SQ_SIZE, config.SQ_SIZE))

def format_clock(seconds: float) -> str:
    secs = max(0, int(seconds))
    mins = secs // 60
    rem = secs % 60
    return f"{mins:02d}:{rem:02d}"

def draw_panel(
    screen: pygame.Surface, gs: GameState, font: pygame.font.Font,
    ai_enabled: bool, ai_depth: int, player_color: str,
    theme_name: str, sound_on: bool, flipped: bool,
    review_idx: int | None = None
) -> dict[str, pygame.Rect]:
    panel_rect = pygame.Rect(config.MARGIN_LEFT + config.DIMENSION * config.SQ_SIZE, 0, config.PANEL_WIDTH, config.HEIGHT)
    pygame.draw.rect(screen, (36, 40, 48), panel_rect)
    buttons = {}
    
    # 1. Header Status
    if gs.game_over:
        if gs.timed_out_color:
            winner = "Black" if gs.timed_out_color == "white" else "White"
            status_text = f"{winner} Wins (Time)"
            status_color = (255, 120, 120)
        elif gs.is_draw:
            status_text = "Draw (Stalemate)"
            status_color = (255, 215, 0)
        else:
            winner = "Black" if gs.turn == "white" else "White"
            status_text = f"{winner} Wins!"
            status_color = (100, 255, 100)
    elif review_idx is not None:
        status_text = f"Reviewing ({review_idx}/{len(gs.fen_history)-1})"
        status_color = (140, 200, 255)
    elif gs.check:
        status_text = f"{gs.turn.capitalize()} in Check!"
        status_color = (255, 100, 100)
    else:
        status_text = f"{gs.turn.capitalize()} to move"
        status_color = (255, 255, 255)

    status_surf = font.render(status_text, True, status_color)
    screen.blit(status_surf, (panel_rect.x + 12, 12))
    
    # Mode and sub-info
    mode_str = f"Mode: {'PvP' if not ai_enabled else ('AI Depth ' + str(ai_depth))}"
    sub_surf = pygame.font.SysFont("Arial", 11).render(mode_str, True, (160, 170, 185))
    screen.blit(sub_surf, (panel_rect.x + 12, 34))

    # 2. Clocks (if time control active)
    clock_y = 54
    if gs.time_control > 0:
        top_color = "black" if not flipped else "white"
        bot_color = "white" if not flipped else "black"
        top_time = gs.black_time if not flipped else gs.white_time
        bot_time = gs.white_time if not flipped else gs.black_time
        
        top_box = pygame.Rect(panel_rect.x + 10, clock_y, 105, 28)
        bot_box = pygame.Rect(panel_rect.right - 115, clock_y, 105, 28)
        
        # Draw top clock
        is_top_turn = (gs.turn == top_color and not gs.game_over)
        pygame.draw.rect(screen, (55, 62, 75) if is_top_turn else (42, 46, 56), top_box, border_radius=4)
        pygame.draw.rect(screen, (100, 160, 240) if is_top_turn else (70, 75, 85), top_box, 1, border_radius=4)
        top_txt = pygame.font.SysFont("Arial", 14, True).render(f"{top_color[0].upper()}: {format_clock(top_time)}", True, (255, 100, 100) if top_time < 30 else (240, 240, 240))
        screen.blit(top_txt, top_txt.get_rect(center=top_box.center))

        # Draw bottom clock
        is_bot_turn = (gs.turn == bot_color and not gs.game_over)
        pygame.draw.rect(screen, (55, 62, 75) if is_bot_turn else (42, 46, 56), bot_box, border_radius=4)
        pygame.draw.rect(screen, (100, 160, 240) if is_bot_turn else (70, 75, 85), bot_box, 1, border_radius=4)
        bot_txt = pygame.font.SysFont("Arial", 14, True).render(f"{bot_color[0].upper()}: {format_clock(bot_time)}", True, (255, 100, 100) if bot_time < 30 else (240, 240, 240))
        screen.blit(bot_txt, bot_txt.get_rect(center=bot_box.center))
        clock_y += 34

    # 3. Captured Pieces
    cap_y = clock_y
    x_offset, y_offset = 12, cap_y
    for dp in (gs.dead_black if not flipped else gs.dead_white):
        sym = functions.SYM_TO_EMOJI_DICT[str(dp)]
        if f"{sym}_small" in PIECE_IMAGES:
            screen.blit(PIECE_IMAGES[f"{sym}_small"], (panel_rect.x + x_offset, y_offset))
        x_offset += 18
        if x_offset > config.PANEL_WIDTH - 25:
            x_offset = 12
            y_offset += 22

    # 4. Interactive Move History Log
    hist_top = cap_y + 36
    history_box = pygame.Rect(panel_rect.x + 10, hist_top, config.PANEL_WIDTH - 20, 150)
    pygame.draw.rect(screen, (28, 31, 38), history_box, border_radius=6)
    pygame.draw.rect(screen, (55, 60, 72), history_box, 1, border_radius=6)
    
    hist_title = pygame.font.SysFont("Arial", 11, True).render("MOVE HISTORY", True, (150, 160, 175))
    screen.blit(hist_title, (history_box.x + 8, history_box.y + 6))
    
    # Display recent moves
    log_font = pygame.font.SysFont("Arial", 11)
    lines = []
    i = 0
    while i < len(gs.move_log):
        move_num = (i // 2) + 1
        w_move = gs.move_log[i]
        b_move = gs.move_log[i+1] if (i + 1 < len(gs.move_log)) else ""
        lines.append(f"{move_num}. {w_move}  {b_move}".strip())
        i += 2
        
    y_line = history_box.y + 24
    for line in lines[-5:]:
        line_surf = log_font.render(line, True, (215, 220, 225))
        screen.blit(line_surf, (history_box.x + 10, y_line))
        y_line += 22

    # 5. Buttons: Undo, Flip Board, Side / Mode, Theme, Sound, Restart
    btn_x = panel_rect.x + 10
    btn_w = config.PANEL_WIDTH - 20
    b_y = hist_top + 160
    
    # Row 1: Side selection & Flip Board
    b1_w = (btn_w - 6) // 2
    btn_side = pygame.Rect(btn_x, b_y, b1_w, 28)
    pygame.draw.rect(screen, (60, 70, 85), btn_side, border_radius=4)
    side_lbl = "Side: White" if player_color == 'white' else ("Side: Black" if player_color == 'black' else "Side: 2P")
    s_txt = pygame.font.SysFont("Arial", 11, True).render(side_lbl, True, (240, 240, 240))
    screen.blit(s_txt, s_txt.get_rect(center=btn_side.center))
    buttons['side'] = btn_side

    btn_flip = pygame.Rect(btn_x + b1_w + 6, b_y, b1_w, 28)
    pygame.draw.rect(screen, (60, 70, 85), btn_flip, border_radius=4)
    f_txt = pygame.font.SysFont("Arial", 11, True).render("Flip (F)", True, (240, 240, 240))
    screen.blit(f_txt, f_txt.get_rect(center=btn_flip.center))
    buttons['flip'] = btn_flip

    b_y += 33
    # Row 2: Undo Move & AI Toggle
    btn_undo = pygame.Rect(btn_x, b_y, b1_w, 28)
    pygame.draw.rect(screen, (75, 85, 100), btn_undo, border_radius=4)
    u_txt = pygame.font.SysFont("Arial", 11, True).render("Undo (U)", True, (240, 240, 240))
    screen.blit(u_txt, u_txt.get_rect(center=btn_undo.center))
    buttons['undo'] = btn_undo

    btn_ai = pygame.Rect(btn_x + b1_w + 6, b_y, b1_w, 28)
    ai_col = (55, 115, 175) if ai_enabled else (70, 75, 85)
    pygame.draw.rect(screen, ai_col, btn_ai, border_radius=4)
    ai_txt = pygame.font.SysFont("Arial", 11, True).render(f"AI: {'ON' if ai_enabled else 'OFF'}", True, (240, 240, 240))
    screen.blit(ai_txt, ai_txt.get_rect(center=btn_ai.center))
    buttons['ai_toggle'] = btn_ai

    b_y += 33
    # Row 3: Theme & Sound
    btn_theme = pygame.Rect(btn_x, b_y, b1_w, 28)
    pygame.draw.rect(screen, (60, 70, 85), btn_theme, border_radius=4)
    th_txt = pygame.font.SysFont("Arial", 11, True).render(f"Theme: {theme_name}", True, (240, 240, 240))
    screen.blit(th_txt, th_txt.get_rect(center=btn_theme.center))
    buttons['theme'] = btn_theme

    btn_sound = pygame.Rect(btn_x + b1_w + 6, b_y, b1_w, 28)
    pygame.draw.rect(screen, (60, 70, 85), btn_sound, border_radius=4)
    snd_txt = pygame.font.SysFont("Arial", 11, True).render(f"Audio: {'ON' if sound_on else 'OFF'}", True, (240, 240, 240))
    screen.blit(snd_txt, snd_txt.get_rect(center=btn_sound.center))
    buttons['sound'] = btn_sound

    b_y += 33
    # Row 4: Restart Game
    btn_restart = pygame.Rect(btn_x, b_y, btn_w, 28)
    pygame.draw.rect(screen, (170, 60, 60), btn_restart, border_radius=4)
    rst_txt = pygame.font.SysFont("Arial", 12, True).render("New / Restart Game", True, pygame.Color('white'))
    screen.blit(rst_txt, rst_txt.get_rect(center=btn_restart.center))
    buttons['restart'] = btn_restart

    return buttons

def main() -> None:
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Chess - HackED 2026")
    clock = pygame.time.Clock()
    
    load_images()
    
    ui_font = pygame.font.SysFont("Arial", 15, True)
    large_font = pygame.font.SysFont("Arial", 28, True)

    gs = GameState()
    AI_ENABLED = True
    ai_depth = 2
    player_color = "white" # 'white', 'black', or '2player'
    flipped = False
    current_theme = config.DEFAULT_THEME
    review_idx: int | None = None # None means live game

    sq_selected = ()
    player_clicks = []
    valid_moves_for_sq = []
    btn_game_over_restart = pygame.Rect(0, 0, 0, 0)

    while True:
        dt = clock.tick(config.MAX_FPS) / 1000.0

        # Update chess clocks
        if gs.update_clock(dt):
            sounds.play_game_over()

        # AI Turn trigger
        ai_color = "black" if player_color == "white" else ("white" if player_color == "black" else None)
        if not gs.game_over and AI_ENABLED and ai_color and gs.turn == ai_color and not gs.promotion_pending:
            prev_board_piece_count = sum(1 for p in gs.pieces_arr if p.alive)
            moved = gs.make_ai_move(ai_depth)
            if moved:
                curr_piece_count = sum(1 for p in gs.pieces_arr if p.alive)
                if curr_piece_count < prev_board_piece_count:
                    sounds.play_capture()
                elif gs.check:
                    sounds.play_check()
                else:
                    sounds.play_move()
            sq_selected = ()
            player_clicks = []
            valid_moves_for_sq = []

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif e.type == pygame.KEYDOWN:
                # Key shortcuts
                if e.key == pygame.K_f:
                    flipped = not flipped
                elif e.key == pygame.K_u:
                    # Undo move
                    gs.undo_move(against_ai=(player_color in ['white', 'black'] and AI_ENABLED))
                    sq_selected = ()
                    player_clicks = []
                    valid_moves_for_sq = []
                elif e.key == pygame.K_m:
                    sounds.toggle_sound()
                elif e.key == pygame.K_t:
                    themes_list = list(config.THEMES.keys())
                    current_theme = themes_list[(themes_list.index(current_theme) + 1) % len(themes_list)]
                elif e.key == pygame.K_LEFT:
                    # Step back in review
                    if review_idx is None:
                        review_idx = max(0, len(gs.fen_history) - 2)
                    else:
                        review_idx = max(0, review_idx - 1)
                elif e.key == pygame.K_RIGHT:
                    if review_idx is not None:
                        review_idx += 1
                        if review_idx >= len(gs.fen_history) - 1:
                            review_idx = None # return to live
                elif e.key == pygame.K_ESCAPE:
                    review_idx = None

            elif e.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos()
                
                # Side Panel Button clicks
                panel_rect = pygame.Rect(config.MARGIN_LEFT + config.DIMENSION * config.SQ_SIZE, 0, config.PANEL_WIDTH, config.HEIGHT)
                if location[0] >= panel_rect.x:
                    buttons = draw_panel(
                        screen, gs, ui_font, AI_ENABLED, ai_depth,
                        player_color, current_theme, sounds.sound_enabled, flipped, review_idx
                    )
                    if buttons['flip'].collidepoint(location):
                        flipped = not flipped
                    elif buttons['undo'].collidepoint(location):
                        gs.undo_move(against_ai=(player_color in ['white', 'black'] and AI_ENABLED))
                        sq_selected = ()
                        player_clicks = []
                        valid_moves_for_sq = []
                    elif buttons['ai_toggle'].collidepoint(location):
                        AI_ENABLED = not AI_ENABLED
                    elif buttons['theme'].collidepoint(location):
                        themes_list = list(config.THEMES.keys())
                        current_theme = themes_list[(themes_list.index(current_theme) + 1) % len(themes_list)]
                    elif buttons['sound'].collidepoint(location):
                        sounds.toggle_sound()
                    elif buttons['side'].collidepoint(location):
                        # Cycle side: White -> Black -> 2Player -> White
                        if player_color == 'white':
                            player_color = 'black'
                            flipped = True
                            AI_ENABLED = True
                        elif player_color == 'black':
                            player_color = '2player'
                            flipped = False
                            AI_ENABLED = False
                        else:
                            player_color = 'white'
                            flipped = False
                            AI_ENABLED = True
                        gs.reset()
                        review_idx = None
                        sq_selected = ()
                        player_clicks = []
                        valid_moves_for_sq = []
                    elif buttons['restart'].collidepoint(location):
                        gs.reset()
                        review_idx = None
                        sq_selected = ()
                        player_clicks = []
                        valid_moves_for_sq = []
                    continue
                    
                if gs.game_over and btn_game_over_restart.collidepoint(location):
                    gs.reset()
                    review_idx = None
                    sq_selected = ()
                    player_clicks = []
                    valid_moves_for_sq = []
                    continue
                    
                # Block board interaction if AI's turn or game over
                is_player_turn = True
                if player_color == 'white' and gs.turn != 'white':
                    is_player_turn = False
                elif player_color == 'black' and gs.turn != 'black':
                    is_player_turn = False
                    
                if gs.game_over or not is_player_turn or review_idx is not None:
                    continue
                    
                # Promotion Modal clicks
                if gs.promotion_pending:
                    menu_w, menu_h = 320, 130
                    menu_rect = pygame.Rect(config.WIDTH//2 - menu_w//2, config.HEIGHT//2 - menu_h//2, menu_w, menu_h)
                    p_opts = [('Q', 'Queen'), ('R', 'Rook'), ('B', 'Bishop'), ('N', 'Knight')]
                    for i, (p, full_name) in enumerate(p_opts):
                        tile_rect = pygame.Rect(menu_rect.x + 16 + i * 72, menu_rect.y + 40, 68, 76)
                        if tile_rect.collidepoint(location):
                            gs.complete_promotion(full_name)
                            sounds.play_move()
                            break
                    continue
                    
                # Board clicks
                s_col = (location[0] - config.MARGIN_LEFT) // config.SQ_SIZE
                s_row = location[1] // config.SQ_SIZE
                
                if not (0 <= s_col < config.DIMENSION and 0 <= s_row < config.DIMENSION):
                    continue 
                
                b_row, b_col = screen_to_board(s_row, s_col, flipped)
                
                if sq_selected == (b_row, b_col):
                    sq_selected = ()
                    player_clicks = []
                    valid_moves_for_sq = []
                else:
                    sq_selected = (b_row, b_col)
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
                        is_cap = (gs.board[end_coords[0]][end_coords[1]] != 0)
                        moved = gs.make_move(start_coords, end_coords)
                        if moved:
                            if is_cap:
                                sounds.play_capture()
                            elif gs.check:
                                sounds.play_check()
                            else:
                                sounds.play_move()
                                
                            if gs.game_over:
                                sounds.play_game_over()
                                
                    sq_selected = ()
                    player_clicks = []
                    valid_moves_for_sq = []
            
        screen.fill(pygame.Color('darkgray'))
        
        # Draw Evaluation Bar
        eval_score = gs.get_evaluation()
        draw_eval_bar(screen, eval_score, flipped, ui_font)

        # Draw Board & Coordinates
        draw_board(screen, ui_font, current_theme, flipped)
        
        # Active position for rendering (review or live)
        display_board = gs.board
        if review_idx is not None and review_idx < len(gs.fen_history):
            temp_gs = GameState.from_fen(gs.fen_history[review_idx])
            display_board = temp_gs.board

        king_in_check_sq = None
        if gs.check:
            k = gs.get_king(gs.turn)
            if k: king_in_check_sq = (k.row, k.col)
            
        draw_highlights(screen, sq_selected, valid_moves_for_sq, gs.last_move, king_in_check_sq, gs, flipped)
        draw_pieces(screen, display_board, flipped)
        
        # Draw Side Panel
        draw_panel(
            screen, gs, ui_font, AI_ENABLED, ai_depth,
            player_color, current_theme, sounds.sound_enabled, flipped, review_idx
        )
        
        # Promotion Modal
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

        # Game Over Overlay
        if gs.game_over:
            if gs.timed_out_color:
                winner = "Black" if gs.timed_out_color == "white" else "White"
                text = f"{winner} wins on time!"
            else:
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

if __name__ == "__main__":
    main()
