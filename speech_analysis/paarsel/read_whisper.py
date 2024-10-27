import os
import whisper
import librosa
import numpy as np
import nltk
from nltk.corpus import cmudict
from pydub import AudioSegment

# Pfad zum CMU Pronouncing Dictionary festlegen
nltk.data.path.append('/Users/christian/Dropbox/_Atelier_E/POLYLOG/PRODUCTION/sound/git/POLYLOG/speech_analysis/paarsel/nltk_data')

# Lade das CMU Pronouncing Dictionary direkt
cmu_dict = cmudict.dict()

def get_first_phoneme(word):
    """Extrahiere das erste Phonem für ein gegebenes Wort aus dem CMU Pronouncing Dictionary."""
    word = word.lower().strip(".,!?-")
    phonemes = cmu_dict.get(word, [])
    return phonemes[0][0] if phonemes else None

# Lade das Whisper-Modell und transkribiere die Audiodatei
model = whisper.load_model("small")
audio_file = "test_2.wav"
result = model.transcribe(audio_file, language="en", word_timestamps=True)

# Lade das Audiofile mit librosa
y, sr = librosa.load(audio_file, sr=None)

# Überprüfe, ob das Verzeichnis "phonemes" existiert, und erstelle es, wenn nicht
if not os.path.exists('phonemes'):
    os.makedirs('phonemes')

# Extrahiere das erste Phonem und dessen Startzeit für jedes Wort
results = []

for segment in result['segments']:
    for word_info in segment['words']:
        word = word_info['word'].strip()
        start_time_sec = word_info['start']
        end_time_sec = word_info['end']
        start_sample = int(start_time_sec * sr)
        end_sample = int(end_time_sec * sr)
        
        # **Korrigierter Codeabschnitt**
        # Extrahiere den Audiobereich für das aktuelle Wort
        y_segment = y[start_sample:end_sample]
        
        # Führe eine Transientenanalyse durch
        onset_env = librosa.onset.onset_strength(y=y_segment, sr=sr)
        onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='samples', backtrack=True)
        
        if len(onset_frames) > 0:
            # Finde den genauen Startpunkt relativ zum gesamten Audio
            true_start_sample = start_sample + onset_frames[0]
            true_start_time = true_start_sample / sr
        else:
            true_start_time = start_time_sec  # Fallback auf die ursprüngliche Startzeit
        
        first_phoneme = get_first_phoneme(word)
        if first_phoneme:
            results.append((first_phoneme, true_start_time * 1000))  # Konvertiere in Millisekunden
            # Schneide das Audio mit PyDub
            audio_segment = AudioSegment.from_wav(audio_file)
            slice = audio_segment[true_start_time * 1000:true_start_time * 1000 + 15000]  # 15 Sekunden
            filename = f"{int(true_start_time * 1000):07d}_{first_phoneme}.wav"
            slice.export(f"phonemes/{filename}", format="wav")

# Ausgabe der Ergebnisse
for phoneme, time in results:
    print(f"Erstes Phonem: {phoneme}, Startzeit: {time:.3f}ms")