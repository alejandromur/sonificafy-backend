import sys
import numpy as np
from scipy.io.wavfile import write

SILENCE_CHARS = {' ': 0.1, '\n': 0.15, '\t': 0.12, '.': 0.08, ',': 0.08, ';': 0.08, '!': 0.1, '?': 0.1}

with open(sys.argv[1], "r") as file:
    html_content = file.read()

def get_musical_frequencies():
    """Genera un diccionario de frecuencias distribuidas en varias octavas."""
    base_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octaves = [3, 4, 5]  # Evitamos octavas muy graves o muy agudas
    frequencies = {}

    for octave in octaves:
        for note in base_notes:
            note_name = f"{note}{octave}"
            frequency = 440.0 * (2 ** ((base_notes.index(note) + (octave - 4) * 12) / 12.0))
            frequencies[note_name] = frequency

    return frequencies

def text_to_frequencies(text):
    """Asigna frecuencias musicales a caracteres con distribución en varias octavas."""
    frequencies = list(get_musical_frequencies().values())
    unique_chars = sorted(set(text))

    char_to_freq = {char: frequencies[i % len(frequencies)] for i, char in enumerate(unique_chars)}

    sequence = []
    for char in text:
        if char in SILENCE_CHARS:
            sequence.append(0)  # Silencio más corto
        else:
            sequence.append(char_to_freq.get(char, np.random.choice(frequencies)))

    return sequence

def generate_piano_wave(frequency, duration=0.25, sample_rate=44100):
    """Genera una onda sinusoidal con envolvente suave."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    if frequency == 0:
        return np.zeros_like(t)  # Silencio

    related_freqs = [frequency * 2, frequency / 2, frequency * 1.5, frequency * 1.25]
    related_amps = [0.15, 0.1, 0.05, 0.05]

    wave = np.sin(2 * np.pi * frequency * t)

    for freq, amp in zip(related_freqs, related_amps):
        wave += amp * np.sin(2 * np.pi * freq * t)

    # Envolvente más suave para eliminar cortes bruscos
    attack_time = 0.02
    release_time = 0.1  

    attack_samples = int(sample_rate * attack_time)
    release_samples = int(sample_rate * release_time)
    sustain_samples = len(t) - attack_samples - release_samples

    envelope = np.concatenate([
        np.linspace(0, 1, attack_samples),  
        np.ones(sustain_samples),  
        np.linspace(1, 0, release_samples)  
    ])

    return wave * envelope * 0.7  # Reducimos la amplitud para evitar saturación

def apply_crossfade(wave1, wave2, fade_duration=0.02, sample_rate=44100):
    """Realiza un fundido cruzado entre dos ondas."""
    fade_samples = int(sample_rate * fade_duration)
    
    # Si la onda es demasiado corta, no aplicamos crossfade
    if len(wave1) < fade_samples or len(wave2) < fade_samples:
        return np.concatenate((wave1, wave2))
    
    fade_out = np.linspace(1, 0, fade_samples)
    fade_in = np.linspace(0, 1, fade_samples)
    
    wave1[-fade_samples:] *= fade_out
    wave2[:fade_samples] *= fade_in

    return np.concatenate((wave1, wave2))

def generate_wave(frequencies, sample_rate=44100):
    """Genera una señal de audio con transiciones suaves entre notas."""
    audio = np.array([])

    for i, freq in enumerate(frequencies):
        duration = SILENCE_CHARS.get(freq, 0.25)  
        wave = generate_piano_wave(freq, duration, sample_rate)

        if i > 0:
            audio = apply_crossfade(audio, wave)  # Aplicamos el fundido cruzado
        else:
            audio = wave

    # Normalizar para evitar distorsión
    audio = audio / np.max(np.abs(audio))  
    return (audio * 32767).astype(np.int16)

frequencies = text_to_frequencies(html_content)
audio_wave = generate_wave(frequencies)

output_file = sys.argv[2]
write(output_file, 44100, audio_wave)
