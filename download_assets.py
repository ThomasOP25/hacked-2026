import urllib.request
import os

os.makedirs('assets/images', exist_ok=True)
pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']

base_url = 'https://raw.githubusercontent.com/Thomas-George-T/Chess-Engine-in-Python/master/images/'

for piece in pieces:
    print(f'Downloading {piece}...')
    try:
        urllib.request.urlretrieve(base_url + piece + '.png', f'assets/images/{piece}.png')
    except Exception as e:
        print(f"Error downloading {piece}: {e}")
print("Done.")
