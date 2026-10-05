import re

with open("chess.py", "r") as f:
    content = f.read()

# Fix the nonlocal binding issue
bad_init = """    btn_ai_toggle = pygame.Rect(0,0,0,0)
    btn_ai_depth = pygame.Rect(0,0,0,0)
    btn_restart = pygame.Rect(0,0,0,0)
    btn_game_over_restart = pygame.Rect(0,0,0,0)
    promotion_state = None
    promo_rects = []

    def reset_game():
        nonlocal board, pieces_arr, turn, sq_selected, player_clicks, valid_moves
        nonlocal game_over, last_move, halfmove_clock, history, dead_pieces_white, dead_pieces_black
        nonlocal promotion_state, check, king_in_check_sq
        board = functions.make_board()"""

good_init = """    btn_ai_toggle = pygame.Rect(0,0,0,0)
    btn_ai_depth = pygame.Rect(0,0,0,0)
    btn_restart = pygame.Rect(0,0,0,0)
    btn_game_over_restart = pygame.Rect(0,0,0,0)
    
    board = None
    pieces_arr = None
    turn = None
    sq_selected = None
    player_clicks = None
    valid_moves = None
    game_over = None
    last_move = None
    halfmove_clock = None
    history = None
    dead_pieces_white = None
    dead_pieces_black = None
    promotion_state = None
    promo_rects = []
    check = None
    king_in_check_sq = None

    def reset_game():
        nonlocal board, pieces_arr, turn, sq_selected, player_clicks, valid_moves
        nonlocal game_over, last_move, halfmove_clock, history, dead_pieces_white, dead_pieces_black
        nonlocal promotion_state, check, king_in_check_sq
        board = functions.make_board()"""

content = content.replace(bad_init, good_init)

with open("chess.py", "w") as f:
    f.write(content)
