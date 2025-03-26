import sys
import numpy as np
from scipy.io.wavfile import write

def create_variable_ngrams(text, pattern=[3, 2, 4]):
    """Crea grupos de tamaño variable siguiendo un patrón."""
    ngrams = []
    current_pos = 0
    pattern_index = 0
    
    while current_pos < len(text):
        # Obtener el tamaño actual del grupo
        ngram_size = pattern[pattern_index % len(pattern)]
        
        # Asegurarse de no sobrepasar el texto
        if current_pos + ngram_size > len(text):
            ngram_size = len(text) - current_pos
        
        # Crear el ngram y añadirlo
        ngram = text[current_pos:current_pos + ngram_size]
        ngrams.append(ngram)
        
        # Avanzar a la siguiente posición
        current_pos += ngram_size
        pattern_index += 1
        
    return ngrams

def create_ngram(text, n):
    """Crea grupos de n caracteres."""
    ngrams = [text[i:i+n] for i in range(0, len(text)-(n-1))]
    if len(text) % n != 0:
        ngrams.append(text[-(len(text) % n):])
    return ngrams

def calculate_frequency(ngram, min_freq=50, max_freq=200, method='hash'):
    """Calcula la frecuencia para un ngram usando diferentes métodos."""
    if method == 'hash':
        # Método original usando hash
        value = hash(ngram) % 1000
        return np.interp(value, [0, 1000], [min_freq, max_freq])
    
    elif method == 'ascii_sum':
        # Suma los valores ASCII de los caracteres
        ascii_sum = sum(ord(c) for c in ngram)
        return np.interp(ascii_sum, [0, 255 * len(ngram)], [min_freq, max_freq])
    
    elif method == 'vowel_weight':
        # Da más peso a las vocales
        vowels = sum(1 for c in ngram.lower() if c in 'aeiou')
        value = (sum(ord(c) for c in ngram) + vowels * 50)
        return np.interp(value, [0, 255 * len(ngram)], [min_freq, max_freq])

def calculate_duration(ngram, base_duration=1.0, method='fixed'):
    """Calcula la duración para un ngram usando diferentes métodos."""
    if method == 'fixed':
        return base_duration
    
    elif method == 'length':
        # Duración basada en la longitud del ngram
        return base_duration * (len(ngram) / 3)
    
    elif method == 'complexity':
        # Duración basada en la complejidad del ngram
        unique_chars = len(set(ngram))
        return base_duration * (0.5 + unique_chars / len(ngram))

def generate_waveform(frequency, time, waveform_type='sine'):
    """Genera diferentes tipos de forma de onda."""
    if waveform_type == 'sine':
        # Onda sinusoidal (suave y redonda)
        return np.sin(2 * np.pi * frequency * time)
    
    elif waveform_type == 'square':
        # Onda cuadrada (más áspera, como un bajo sintético)
        return np.sign(np.sin(2 * np.pi * frequency * time))
    
    elif waveform_type == 'sawtooth':
        # Onda sierra (rica en armónicos, brillante)
        return 2 * (frequency * time - np.floor(0.5 + frequency * time))
    
    elif waveform_type == 'triangle':
        # Onda triangular (suave pero con más carácter que la sinusoidal)
        return 2 * np.abs(2 * (frequency * time - np.floor(0.5 + frequency * time))) - 1
    
    elif waveform_type == 'noise':
        # Ruido blanco (percusivo, textura)
        return np.random.uniform(-1, 1, len(time))
    
    # Por defecto, usamos sinusoidal
    return np.sin(2 * np.pi * frequency * time)

def generate_wave(frequencies, durations, sample_rate=44100):
    """Genera una señal de audio con duraciones variables por nota."""
    audio = np.array([])
    
    for freq, duration in zip(frequencies, durations):
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        
        # Crear envolvente
        fade_samples = int(sample_rate * 0.1)
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        sustain = np.ones(len(t) - 2 * fade_samples)
        envelope = np.concatenate([fade_in, sustain, fade_out])
        
        # Generar y procesar la onda
        wave = np.sin(2 * np.pi * freq * t)
        wave = wave * envelope
        wave[:1] = 0
        wave[-1:] = 0
        
        audio = np.concatenate((audio, wave))
    
    return (audio * 32767).astype(np.int16)

def sonify_text(text, config):
    """Función principal que procesa el texto según la configuración."""
    # Usar ngrams de tamaño variable o fijo
    if config.get('variable_ngrams', False):
        ngrams = create_variable_ngrams(text, config.get('ngram_pattern', [3, 2, 4]))
    else:
        ngrams = create_ngram(text, config['ngram_size'])
    
    # El resto del código permanece igual
    frequencies = [
        calculate_frequency(
            ngram, 
            config['min_freq'], 
            config['max_freq'], 
            config['freq_method']
        ) for ngram in ngrams
    ]
    
    durations = [
        calculate_duration(
            ngram, 
            config['base_duration'], 
            config['duration_method']
        ) for ngram in ngrams
    ]
    
    return generate_wave(frequencies, durations, config['sample_rate'])

def generate_multi_voice_wave(voice_data, sample_rate=44100):
    """Genera múltiples voces de audio en paralelo y las mezcla."""
    # Determinar la duración total necesaria
    total_duration = max(sum(voice['durations']) for voice in voice_data)
    total_samples = int(sample_rate * total_duration)
    
    # Crear un array para la mezcla final
    mixed_audio = np.zeros(total_samples)
    
    # Procesar cada voz
    for voice in voice_data:
        frequencies = voice['frequencies']
        durations = voice['durations']
        volume = voice.get('volume', 1.0)  # Volumen relativo de la voz
        waveform_type = voice.get('waveform', 'sine')  # Tipo de forma de onda
        
        current_sample = 0
        
        for freq, duration in zip(frequencies, durations):
            # Número de muestras para esta nota
            samples = int(sample_rate * duration)
            
            # Crear el tiempo para esta nota
            t = np.linspace(0, duration, samples, endpoint=False)
            
            # Crear la envolvente
            fade_samples = int(sample_rate * 0.1)
            fade_in = np.linspace(0, 1, min(fade_samples, samples//2))
            fade_out = np.linspace(1, 0, min(fade_samples, samples//2))
            sustain_samples = samples - len(fade_in) - len(fade_out)
            sustain = np.ones(max(0, sustain_samples))
            envelope = np.concatenate([fade_in, sustain, fade_out])[:samples]
            
            # Generar onda con la forma de onda seleccionada
            wave = generate_waveform(freq, t, waveform_type) * envelope * volume
            
            # Añadir a la mezcla en la posición correcta
            end_sample = current_sample + samples
            if end_sample > total_samples:
                # Recortar si sobrepasa
                wave = wave[:total_samples - current_sample]
                end_sample = total_samples
                
            mixed_audio[current_sample:end_sample] += wave
            current_sample = end_sample
    
    # Normalizar para evitar clipping
    max_amp = np.max(np.abs(mixed_audio))
    if max_amp > 0:
        mixed_audio = mixed_audio / max_amp
        
    return (mixed_audio * 32767).astype(np.int16)

def sonify_text_multi_voice(text, config):
    """Procesa el texto generando múltiples voces."""
    # Dividir el texto para diferentes voces
    if config.get('multi_voice', False):
        voices = []
        
        # Voz 1: Bajo - usando etiquetas HTML y símbolos
        bass_text = ''.join([c for c in text if c in '<>/="{}[]()!@#$%^&*'])
        bass_ngrams = create_variable_ngrams(bass_text, config.get('bass_pattern', [2, 3]))
        
        bass_voice = {
            'frequencies': [
                calculate_frequency(
                    ngram, 
                    config.get('bass_min_freq', 30),
                    config.get('bass_max_freq', 150), 
                    config.get('bass_freq_method', 'hash')
                ) for ngram in bass_ngrams
            ],
            'durations': [
                calculate_duration(
                    ngram, 
                    config.get('bass_duration', 1.5),
                    config.get('bass_duration_method', 'fixed')
                ) for ngram in bass_ngrams
            ],
            'volume': config.get('bass_volume', 0.8),
            'waveform': config.get('bass_waveform', 'square')  # Forma de onda para el bajo
        }
        voices.append(bass_voice)
        
        # Voz 2: Melodía - usando texto y números
        melody_text = ''.join([c for c in text if c.isalnum() and c not in '<>/="{}[]()!@#$%^&*'])
        melody_ngrams = create_variable_ngrams(melody_text, config.get('melody_pattern', [3, 2, 4]))
        
        melody_voice = {
            'frequencies': [
                calculate_frequency(
                    ngram, 
                    config.get('melody_min_freq', 150),
                    config.get('melody_max_freq', 400), 
                    config.get('melody_freq_method', 'vowel_weight')
                ) for ngram in melody_ngrams
            ],
            'durations': [
                calculate_duration(
                    ngram, 
                    config.get('melody_duration', 0.8),
                    config.get('melody_duration_method', 'complexity')
                ) for ngram in melody_ngrams
            ],
            'volume': config.get('melody_volume', 1.0),
            'waveform': config.get('melody_waveform', 'sine')  # Forma de onda para la melodía
        }
        voices.append(melody_voice)
        
        # Opcionalmente, añadir una tercera voz para atmósfera
        if config.get('use_atmosphere', False):
            # Filtrar números y algunos caracteres especiales
            atmosphere_text = ''.join([c for c in text if c.isdigit() or c in '.,;:?!'])
            atmosphere_ngrams = create_variable_ngrams(atmosphere_text, config.get('atmosphere_pattern', [4, 2]))
            
            atmosphere_voice = {
                'frequencies': [
                    calculate_frequency(
                        ngram, 
                        config.get('atmosphere_min_freq', 200),
                        config.get('atmosphere_max_freq', 500), 
                        config.get('atmosphere_freq_method', 'ascii_sum')
                    ) for ngram in atmosphere_ngrams
                ],
                'durations': [
                    calculate_duration(
                        ngram, 
                        config.get('atmosphere_duration', 0.5),
                        config.get('atmosphere_duration_method', 'length')
                    ) for ngram in atmosphere_ngrams
                ],
                'volume': config.get('atmosphere_volume', 0.6),
                'waveform': config.get('atmosphere_waveform', 'sawtooth')
            }
            voices.append(atmosphere_voice)
        
        return generate_multi_voice_wave(voices, config['sample_rate'])
    
    else:
        # Código original para una sola voz
        return sonify_text(text, config)

configs = {
    'default': {
        'ngram_size': 3,
        'min_freq': 50,
        'max_freq': 200,
        'freq_method': 'hash',
        'base_duration': 1.0,
        'duration_method': 'fixed',
        'sample_rate': 44100,
        'variable_ngrams': False
    },
    'variable': {
        'min_freq': 50,
        'max_freq': 200,
        'freq_method': 'hash',
        'base_duration': 1.0,
        'duration_method': 'fixed',
        'sample_rate': 44100,
        'variable_ngrams': True,
        'ngram_pattern': [3, 2, 4]  # Patrón: trigram, bigram, tetragrama, repetir...
    },
    'jazz': {
        'min_freq': 40,
        'max_freq': 300,
        'freq_method': 'vowel_weight',
        'base_duration': 0.28,
        'duration_method': 'complexity',
        'sample_rate': 44100,
        'variable_ngrams': True,
        'ngram_pattern': [2, 3, 5, 1, 4]  # Patrón más complejo para variación rítmica
    },
    'polyphony': {
        'sample_rate': 44100,
        'multi_voice': True,
        # Bajo
        'bass_pattern': [2, 3],
        'bass_min_freq': 30,
        'bass_max_freq': 150,
        'bass_freq_method': 'hash',
        'bass_duration': 1.5,
        'bass_duration_method': 'fixed',
        'bass_volume': 0.8,
        'bass_waveform': 'square',  # Onda cuadrada para bajo (más potente)
        # Melodía
        'melody_pattern': [3, 2, 4],
        'melody_min_freq': 150,
        'melody_max_freq': 400,
        'melody_freq_method': 'vowel_weight',
        'melody_duration': 0.8,
        'melody_duration_method': 'complexity',
        'melody_volume': 1.0,
        'melody_waveform': 'sine'  # Onda sinusoidal para melodía (más suave)
    },
    'orchestra': {
        'sample_rate': 44100,
        'multi_voice': True,
        'use_atmosphere': True,
        # Bajo (estructura HTML con onda cuadrada)
        'bass_pattern': [2, 3],
        'bass_min_freq': 30,
        'bass_max_freq': 120,
        'bass_freq_method': 'hash',
        'bass_duration': 1.8,
        'bass_duration_method': 'fixed',
        'bass_volume': 0.7,
        'bass_waveform': 'square',
        # Melodía (texto con onda triangular)
        'melody_pattern': [3, 2, 4],
        'melody_min_freq': 150,
        'melody_max_freq': 350,
        'melody_freq_method': 'vowel_weight',
        'melody_duration': 0.7,
        'melody_duration_method': 'complexity',
        'melody_volume': 0.9,
        'melody_waveform': 'triangle',
        # Atmósfera (números con onda sierra)
        'atmosphere_pattern': [4, 2],
        'atmosphere_min_freq': 200,
        'atmosphere_max_freq': 500,
        'atmosphere_freq_method': 'ascii_sum',
        'atmosphere_duration': 0.5,
        'atmosphere_duration_method': 'length',
        'atmosphere_volume': 0.6,
        'atmosphere_waveform': 'sawtooth'
    },
    'lofi': {
        'sample_rate': 44100,
        'multi_voice': True,
        # Bajo con onda triangular suave
        'bass_pattern': [3, 2],
        'bass_min_freq': 40,
        'bass_max_freq': 120,
        'bass_freq_method': 'hash',
        'bass_duration': 1.2,
        'bass_duration_method': 'fixed',
        'bass_volume': 0.7,
        'bass_waveform': 'triangle',
        # Melodía con onda sinusoidal
        'melody_pattern': [2, 4, 3],
        'melody_min_freq': 120,
        'melody_max_freq': 320,
        'melody_freq_method': 'vowel_weight',
        'melody_duration': 0.9,
        'melody_duration_method': 'complexity',
        'melody_volume': 0.8,
        'melody_waveform': 'sine'
    }
}

# Leer el archivo y procesar
with open(sys.argv[1], "r") as file:
    html_content = file.read()

# Elegir la configuración (podría venir como tercer argumento)
config_name = sys.argv[3] if len(sys.argv) > 3 else 'default'
selected_config = configs.get(config_name, configs['default'])

# Generar el audio con la configuración seleccionada
if selected_config.get('multi_voice', False):
    audio_wave = sonify_text_multi_voice(html_content, selected_config)
else:
    audio_wave = sonify_text(html_content, selected_config)
write(sys.argv[2], selected_config['sample_rate'], audio_wave)
