import sys
import numpy as np
from scipy.io.wavfile import write

with open(sys.argv[1], "r") as file:
    html_content = file.read()

def text_to_frequencies(text, min_freq=50, max_freq=200):
    """Converts characters to frequencies within a given range."""
    """The range between 50 and 200 Hz will produce deeper and more relaxing sounds"""
    unique_chars = sorted(set(text))
    char_to_freq = {char: np.interp(i, [0, len(unique_chars)], [min_freq, max_freq])
                    for i, char in enumerate(unique_chars)}
    return [char_to_freq[char] for char in text]

def generate_wave(frequencies, duration=0.5, sample_rate=44100):
    """Generates an audio signal by concatenating sine waves."""
    """Increasing duration makes each character have a longer duration, like making the wave longer"""
    total_samples = int(sample_rate * duration)
    if total_samples <= 0:
        raise ValueError("Duration must result in at least 1 sample")
        
    t = np.linspace(0, duration, total_samples, endpoint=False)
    audio = np.zeros(len(frequencies) * total_samples)
    
    for i, freq in enumerate(frequencies):
        start_idx = i * total_samples
        end_idx = (i + 1) * total_samples
        audio[start_idx:end_idx] = np.sin(2 * np.pi * freq * t)
    
    return (audio * 32767).astype(np.int16)  # Scale to 16 bits

frequencies = text_to_frequencies(html_content)
audio_wave = generate_wave(frequencies)

output_file = sys.argv[2]

write(output_file, 44100, audio_wave)

