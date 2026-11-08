from __future__ import annotations

# Board
DIMENSION = 8
SQ_SIZE = 64

# UI Layout  
EVAL_BAR_WIDTH = 14
MARGIN_LEFT = 46
MARGIN_BOTTOM = 30
PANEL_WIDTH = 250

WIDTH = DIMENSION * SQ_SIZE + MARGIN_LEFT + PANEL_WIDTH
HEIGHT = DIMENSION * SQ_SIZE + MARGIN_BOTTOM
MAX_FPS = 60

# Themes (Light square, Dark square)
THEMES: dict[str, tuple[tuple[int, int, int], tuple[int, int, int]]] = {
    'Green': ((235, 235, 208), (119, 149, 86)),
    'Wood': ((240, 217, 181), (181, 136, 99)),
    'Blue': ((222, 227, 230), (140, 162, 173)),
    'Dark': ((180, 180, 180), (90, 95, 105)),
}

DEFAULT_THEME = 'Green'
COLOR_LIGHT, COLOR_DARK = THEMES[DEFAULT_THEME]

# Highlights
COLOR_HIGHLIGHT = (186, 202, 68)
COLOR_LAST_MOVE = (255, 255, 120)
COLOR_CHECK = (255, 100, 100)

# Time control presets (seconds)
TIME_CONTROLS: dict[str, int] = {
    'None': 0,
    '10 min': 600,
    '5 min': 300,
    '3 min': 180,
}
