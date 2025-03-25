import sys
import numpy as np
from scipy.io.wavfile import write

with open(sys.argv[1], "r") as file:
    html_content = file.read()

def create_instrument_envelope(instrument_type, duration, sample_rate=44100):
    """Crea diferentes tipos de envolventes según el instrumento"""
    total_samples = int(duration * sample_rate)
    
    if instrument_type == "piano":
        # 20% del total para todas las fases excepto sustain
        phase_samples = int(total_samples * 0.2)
        return {
            'attack': int(phase_samples * 0.1),    # 2% del total
            'decay': int(phase_samples * 0.3),     # 6% del total
            'sustain_level': 0.7,
            'release': int(phase_samples * 0.6)    # 12% del total
        }
    
    elif instrument_type == "strings":
        # 30% del total para todas las fases excepto sustain
        phase_samples = int(total_samples * 0.3)
        return {
            'attack': int(phase_samples * 0.3),    # 9% del total
            'decay': int(phase_samples * 0.2),     # 6% del total
            'sustain_level': 0.8,
            'release': int(phase_samples * 0.5)    # 15% del total
        }
    
    elif instrument_type == "organ":
        # 30% del total para todas las fases excepto sustain
        phase_samples = int(total_samples * 0.3)
        return {
            'attack': int(phase_samples * 0.3),    # 9% del total
            'decay': int(phase_samples * 0.2),     # 6% del total
            'sustain_level': 0.8,
            'release': int(phase_samples * 0.5)    # 15% del total
        }
    
    elif instrument_type == "pluck":
        # 40% del total para todas las fases excepto sustain
        phase_samples = int(total_samples * 0.4)
        return {
            'attack': int(phase_samples * 0.1),    # 4% del total
            'decay': int(phase_samples * 0.6),     # 24% del total
            'sustain_level': 0.0,
            'release': int(phase_samples * 0.3)    # 12% del total
        }

def apply_envelope(wave, envelope_type="piano", sample_rate=44100):
    """Aplica diferentes tipos de envolventes al sonido"""
    env_params = create_instrument_envelope(envelope_type, len(wave)/sample_rate, sample_rate)
    
    # Crear la envolvente
    envelope = np.concatenate([
        # Attack: curva exponencial
        1 - np.exp(-5 * np.linspace(0, 1, env_params['attack'])),
        
        # Decay: curva exponencial hasta nivel de sustain
        np.exp(-3 * np.linspace(0, 1, env_params['decay'])) * 
            (1 - env_params['sustain_level']) + env_params['sustain_level'],
        
        # Sustain: nivel constante
        env_params['sustain_level'] * np.ones(
            len(wave) - env_params['attack'] - env_params['decay'] - env_params['release']
        ),
        
        # Release: fade out exponencial
        np.exp(-5 * np.linspace(0, 1, env_params['release'])) * env_params['sustain_level']
    ])
    
    return wave * envelope

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

def generate_piano_wave(frequency, duration=0.2, sample_rate=44100, instrument_type="piano"):
    """Genera un sonido con la envolvente especificada"""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # Generar onda base con armónicos
    wave = np.sin(2 * np.pi * frequency * t)
    for i, amp in enumerate([0.5, 0.25, 0.125], 2):
        wave += amp * np.sin(2 * np.pi * frequency * i * t)
    
    # Aplicar la envolvente seleccionada
    wave = apply_envelope(wave, instrument_type, sample_rate)
    
    return wave

def generate_wave(frequencies, duration=0.25, sample_rate=44100):
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

