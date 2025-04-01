import sys
import numpy as np
from scipy.io.wavfile import write

with open(sys.argv[1], "r") as file:
    html_content = file.read()

def text_to_frequencies(text, min_freq=50, max_freq=150):
    """Convierte caracteres en frecuencias dentro del rango típico de un didgeridoo."""
    unique_chars = sorted(set(text))
    char_to_freq = {char: np.interp(i, [0, len(unique_chars)], [min_freq, max_freq])
                    for i, char in enumerate(unique_chars)}
    return [char_to_freq[char] for char in text]

def generate_didgeridoo_wave(frequencies, duration=0.3, sample_rate=44100):
    """Genera una señal de audio simulando el sonido de un didgeridoo."""
    audio = np.array([])
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    for freq in frequencies:
        # Generamos el tono fundamental
        fundamental = np.sin(2 * np.pi * freq * t)
        
        # Añadimos armónicos característicos del didgeridoo
        harmonic1 = 0.5 * np.sin(2 * np.pi * freq * 2 * t)  # Segundo armónico
        harmonic2 = 0.25 * np.sin(2 * np.pi * freq * 3 * t)  # Tercer armónico
        
        # Añadimos una modulación suave para simular la vibración de los labios
        modulation = 0.1 * np.sin(2 * np.pi * 5 * t)
        
        # Combinamos todos los componentes
        wave = fundamental + harmonic1 + harmonic2
        wave = wave * (1 + modulation)
        
        # Normalizamos y aplicamos una envolvente suave
        wave = wave / np.max(np.abs(wave))
        envelope = np.exp(-t / duration)  # Envolvente exponencial
        wave = wave * envelope
        
        audio = np.concatenate((audio, wave))
    
    return (audio * 32767).astype(np.int16)

frequencies = text_to_frequencies(html_content)
audio_wave = generate_didgeridoo_wave(frequencies)

output_file = sys.argv[2]
write(output_file, 44100, audio_wave)

