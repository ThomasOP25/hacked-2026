import os
import pygame

def ensure_assets() -> None:
    os.makedirs('assets/images', exist_ok=True)
    
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
    # Use Arial Unicode MS which has full chess piece support on macOS
    try:
        font = pygame.font.SysFont('arialunicode', 100)
    except:
        font = pygame.font.SysFont('applesymbols', 100)
        
    if not font.metrics('\u265A'):
        font = pygame.font.SysFont(None, 100)
    
    for filename, (unicode_char, color) in piece_data.items():
        filepath = f'assets/images/{filename}.png'
        print(f'Generating {filename}.png...')
        text_surf = font.render(unicode_char, True, color)
        
        size = max(text_surf.get_width(), text_surf.get_height()) + 10
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Outline for contrast
        outline_color = (0, 0, 0) if color == (255, 255, 255) else (255, 255, 255)
        outline = font.render(unicode_char, True, outline_color)
        
        # Draw outline
        for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2), (0,3), (3,0), (-3,0), (0,-3)]:
            surf.blit(outline, (size//2 - outline.get_width()//2 + dx, size//2 - outline.get_height()//2 + dy))
            
        # Draw main text
        surf.blit(text_surf, (size//2 - text_surf.get_width()//2, size//2 - text_surf.get_height()//2))
        
        pygame.image.save(surf, filepath)

if __name__ == "__main__":
    ensure_assets()
    print("Done.")
