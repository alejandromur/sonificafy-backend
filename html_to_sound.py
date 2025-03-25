import sys
import numpy as np
from scipy.io.wavfile import write

with open(sys.argv[1], "r") as file:
    html_content = file.read()

def text_to_frequencies(text, min_freq=100, max_freq=300):
    """Convierte caracteres en frecuencias dentro de un rango dado."""
    """El rango entre 200 y 1000 está equilibrado. Más bajo es más grave, más alto más agudo"""
    unique_chars = sorted(set(text))  # Obtiene caracteres únicos
    char_to_freq = {char: np.interp(i, [0, len(unique_chars)], [min_freq, max_freq])
                    for i, char in enumerate(unique_chars)}
    return [char_to_freq[char] for char in text]

def generate_wave(frequencies, duration=0.1, sample_rate=44100):
    """Genera una señal de audio concatenando ondas sinusoidales."""
    """Incrementando duration hacemos que cada caracter tenga una duración mayor, es como si hicieras la onda más larga"""
    audio = np.array([])
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
  
    for freq in frequencies:
        wave = np.sin(2 * np.pi * freq * t)  # Genera onda sinusoidal
        audio = np.concatenate((audio, wave))
  
    return (audio * 32767).astype(np.int16)  # Escalar a 16 bits

frequencies = text_to_frequencies(html_content)
audio_wave = generate_wave(frequencies)

output_file = sys.argv[2]

write(output_file, 44100, audio_wave)

