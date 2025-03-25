import sys
import numpy as np
from scipy.io.wavfile import write

with open(sys.argv[1], "r") as file:
    html_content = file.read()

def get_musical_frequency():
    """Retorna un diccionario con las frecuencias de las notas musicales."""
    base_frequencies = {
        'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13,
        'E4': 329.63, 'F4': 349.23, 'F#4': 369.99, 'G4': 392.00,
        'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88
    }
    return base_frequencies

def text_to_frequencies(text):
    """Convierte caracteres en frecuencias usando notas musicales reales."""
    frequencies = get_musical_frequency()
    notes = list(frequencies.values())
    unique_chars = sorted(set(text))
    char_to_freq = {char: notes[i % len(notes)] 
                    for i, char in enumerate(unique_chars)}
    return [char_to_freq[char] for char in text]

def add_reverb(audio, sample_rate=44100):
    """Añade un efecto simple de reverberación."""
    # Parámetros de reverb
    delays = [0.03, 0.05, 0.07]  # Delays en segundos
    amplitudes = [0.3, 0.2, 0.1]  # Amplitud de cada eco
    
    reverb_audio = np.copy(audio)
    
    for delay, amplitude in zip(delays, amplitudes):
        # Convertir delay a samples
        delay_samples = int(sample_rate * delay)
        # Crear eco
        echo = np.zeros_like(audio)
        echo[delay_samples:] = audio[:-delay_samples] * amplitude
        reverb_audio += echo
    
    # Normalizar
    reverb_audio = reverb_audio / np.max(np.abs(reverb_audio))
    return reverb_audio    

def generate_piano_wave(frequency, duration=0.2, sample_rate=44100):
    """Genera un sonido de piano con resonancia simpática."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # Frecuencias relacionadas (octava superior e inferior)
    related_freqs = [
        frequency * 2,    # Octava superior
        frequency / 2,    # Octava inferior
        frequency * 1.5,  # Quinta
        frequency * 1.25  # Tercera mayor
    ]
    related_amps = [0.1, 0.1, 0.05, 0.05]  # Amplitudes de resonancia
    
    # Onda principal
    wave = np.sin(2 * np.pi * frequency * t)
    
    # Añadir resonancias
    for freq, amp in zip(related_freqs, related_amps):
        wave += amp * np.sin(2 * np.pi * freq * t)
    
    # Envolvente ADSR
    attack_time = 0.005
    decay_time = 0.05
    release_time = 0.1
    
    attack_samples = int(sample_rate * attack_time)
    decay_samples = int(sample_rate * decay_time)
    release_samples = int(sample_rate * release_time)
    sustain_samples = len(t) - attack_samples - decay_samples - release_samples
    
    envelope = np.concatenate([
        np.linspace(0, 1, attack_samples),
        np.linspace(1, 0.7, decay_samples),
        0.7 * np.ones(sustain_samples),
        np.linspace(0.7, 0, release_samples)
    ])
    
    return wave * envelope

def generate_wave(frequencies, duration=0.2, sample_rate=44100):
    """Genera una señal de audio usando sonidos de piano."""
    audio = np.array([])
    
    for freq in frequencies:
        wave = generate_piano_wave(freq, duration, sample_rate)
        audio = np.concatenate((audio, wave))
    
    # Normalizar y convertir a 16 bits
    audio = audio / np.max(np.abs(audio))  # Normalizar
    #audio = add_reverb(audio, sample_rate)  # Añadir reverb
    return (audio * 32767).astype(np.int16)    

frequencies = text_to_frequencies(html_content)
audio_wave = generate_wave(frequencies)

output_file = sys.argv[2]

write(output_file, 44100, audio_wave)

