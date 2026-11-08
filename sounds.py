from __future__ import annotations
import math
import array
import pygame

sound_enabled: bool = True
_sounds_initialized: bool = False
_move_sound: pygame.mixer.Sound | None = None
_capture_sound: pygame.mixer.Sound | None = None
_check_sound: pygame.mixer.Sound | None = None
_game_over_sound: pygame.mixer.Sound | None = None

def init_sounds() -> None:
    global _sounds_initialized, _move_sound, _capture_sound, _check_sound, _game_over_sound
    if _sounds_initialized:
        return
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        
        # 1. Move Sound: Gentle wooden tap (300Hz decaying sine)
        _move_sound = _generate_tone(freq=280, duration=0.045, decay=60.0, volume=0.5)
        
        # 2. Capture Sound: Crisp snap (460Hz punchy decay)
        _capture_sound = _generate_tone(freq=460, duration=0.07, decay=45.0, volume=0.7)
        
        # 3. Check Sound: Dual alert chime (620Hz + 840Hz)
        _check_sound = _generate_dual_tone(freq1=620, freq2=840, duration=0.15, decay=20.0, volume=0.6)
        
        # 4. Game Over Sound: Finish chord
        _game_over_sound = _generate_dual_tone(freq1=440, freq2=660, duration=0.3, decay=10.0, volume=0.6)
        
        _sounds_initialized = True
    except Exception as e:
        # Mixer might not be available in headless environments
        _sounds_initialized = False

def _generate_tone(freq: float, duration: float, decay: float, volume: float) -> pygame.mixer.Sound:
    sample_rate = 22050
    total_samples = int(sample_rate * duration)
    buf = array.array('h')
    for i in range(total_samples):
        t = i / sample_rate
        amp = math.exp(-t * decay) * 32767 * volume
        sample = int(amp * math.sin(2 * math.pi * freq * t))
        buf.append(max(-32767, min(32767, sample)))
    return pygame.mixer.Sound(buffer=buf)

def _generate_dual_tone(freq1: float, freq2: float, duration: float, decay: float, volume: float) -> pygame.mixer.Sound:
    sample_rate = 22050
    total_samples = int(sample_rate * duration)
    buf = array.array('h')
    for i in range(total_samples):
        t = i / sample_rate
        amp = math.exp(-t * decay) * 16383 * volume
        sample = int(amp * (math.sin(2 * math.pi * freq1 * t) + math.sin(2 * math.pi * freq2 * t)))
        buf.append(max(-32767, min(32767, sample)))
    return pygame.mixer.Sound(buffer=buf)

def play_move() -> None:
    if sound_enabled and _move_sound:
        try: _move_sound.play()
        except Exception: pass

def play_capture() -> None:
    if sound_enabled and _capture_sound:
        try: _capture_sound.play()
        except Exception: pass

def play_check() -> None:
    if sound_enabled and _check_sound:
        try: _check_sound.play()
        except Exception: pass

def play_game_over() -> None:
    if sound_enabled and _game_over_sound:
        try: _game_over_sound.play()
        except Exception: pass

def toggle_sound() -> bool:
    global sound_enabled
    sound_enabled = not sound_enabled
    return sound_enabled
