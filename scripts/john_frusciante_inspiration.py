import sys
import numpy as np
from scipy.io.wavfile import write
import random

def get_musical_frequency():
    """Retorna un diccionario con frecuencias de notas en diferentes octavas."""
    base_frequencies = {
        'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13,
        'E4': 329.63, 'F4': 349.23, 'F#4': 369.99, 'G4': 392.00,
        'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88,
        'C5': 523.25, 'D5': 587.33, 'E5': 659.25
    }
    return base_frequencies

def text_to_frequencies(text):
    """Asigna frecuencias y duraciones a los caracteres."""
    frequencies = get_musical_frequency()
    notes = list(frequencies.values())
    durations = [0.15, 0.3, 0.45, 0.6]  # Corcheas, negras, blancas
    
    unique_chars = sorted(set(text))
    char_to_freq = {char: (notes[i % len(notes)], random.choice(durations)) 
                    for i, char in enumerate(unique_chars)}
    
    return [char_to_freq[char] for char in text]

def generate_wave(frequencies, sample_rate=44100):
    """Genera una señal de audio con envolvente suave y vibrato."""
    audio = np.array([])
    
    for freq, duration in frequencies:
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        vibrato = np.sin(2 * np.pi * 5 * t) * 3  # Ligero vibrato
        wave = np.sin(2 * np.pi * (freq + vibrato) * t) 
        envelope = np.linspace(0, 1, len(t)) * np.linspace(1, 0, len(t))
        wave *= envelope  # Suavizar inicio y final
        
        audio = np.concatenate((audio, wave))
    
    # Reverb simulada
    reverb = np.convolve(audio, np.ones(500) / 500, mode='same')
    audio = 0.6 * audio + 0.4 * reverb
    
    # Normalizar
    audio = audio / np.max(np.abs(audio))
    return (audio * 32767).astype(np.int16)

if __name__ == "__main__":
    with open(sys.argv[1], "r") as file:
        html_content = file.read()
    
    frequencies = text_to_frequencies(html_content)
    audio_wave = generate_wave(frequencies)
    
    output_file = sys.argv[2]
    write(output_file, 44100, audio_wave)
