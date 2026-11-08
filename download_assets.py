import os
import urllib.request
import pygame

PIECE_NAMES = ['wK', 'wQ', 'wR', 'wB', 'wN', 'wp', 'bK', 'bQ', 'bR', 'bB', 'bN', 'bp']

def ensure_assets() -> None:
    os.makedirs('assets/images', exist_ok=True)
    
    # Check if all piece images already exist and are valid
    missing = [name for name in PIECE_NAMES if not os.path.exists(f'assets/images/{name}.png') or os.path.getsize(f'assets/images/{name}.png') < 500]
    if not missing:
        return

    print(f"Acquiring chess piece assets for: {missing}...")

    # 1. Primary: Download clean tournament Staunton PNG piece set from official chessboardjs repository
    base_url = "https://raw.githubusercontent.com/oakmac/chessboardjs/master/website/img/chesspieces/wikipedia/"
    download_success = True
    
    for name in missing:
        remote_name = 'wP' if name == 'wp' else ('bP' if name == 'bp' else name)
        url = f"{base_url}{remote_name}.png"
        filepath = f"assets/images/{name}.png"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read()
                if len(content) > 500:
                    with open(filepath, 'wb') as f:
                        f.write(content)
                else:
                    download_success = False
                    break
        except Exception as e:
            print(f"Network download error for {name}: {e}")
            download_success = False
            break

    # 2. Fallback: If network is unavailable, generate using Pygame font glyphs
    if not download_success:
        print("Falling back to local font asset generation...")
        fallback_font_generation()

def fallback_font_generation() -> None:
    piece_data = {
        'wK': ('\u265A', (255, 255, 255)),
        'wQ': ('\u265B', (255, 255, 255)),
        'wR': ('\u265C', (255, 255, 255)),
        'wB': ('\u265D', (255, 255, 255)),
        'wN': ('\u265E', (255, 255, 255)),
        'wp': ('\u265F', (255, 255, 255)),
        'bK': ('\u265A', (0, 0, 0)),
        'bQ': ('\u265B', (0, 0, 0)),
        'bR': ('\u265C', (0, 0, 0)),
        'bB': ('\u265D', (0, 0, 0)),
        'bN': ('\u265E', (0, 0, 0)),
        'bp': ('\u265F', (0, 0, 0)),
    }
    
    pygame.font.init()
    font = None
    for fname in ['arialunicode', 'applesymbols', 'segoe ui symbol', 'lucidagrande']:
        try:
            f = pygame.font.SysFont(fname, 100)
            if f.metrics('\u265A'):
                font = f
                break
        except Exception:
            pass
            
    if not font:
        font = pygame.font.SysFont(None, 100)

    for filename, (unicode_char, color) in piece_data.items():
        filepath = f'assets/images/{filename}.png'
        text_surf = font.render(unicode_char, True, color)
        size = max(text_surf.get_width(), text_surf.get_height()) + 10
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        outline_color = (0, 0, 0) if color == (255, 255, 255) else (255, 255, 255)
        outline = font.render(unicode_char, True, outline_color)
        for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2), (0,3), (3,0), (-3,0), (0,-3)]:
            surf.blit(outline, (size//2 - outline.get_width()//2 + dx, size//2 - outline.get_height()//2 + dy))
        surf.blit(text_surf, (size//2 - text_surf.get_width()//2, size//2 - text_surf.get_height()//2))
        pygame.image.save(surf, filepath)

if __name__ == "__main__":
    ensure_assets()
    print("Piece assets check complete.")
