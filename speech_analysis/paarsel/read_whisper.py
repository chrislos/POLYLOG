import os
import whisper
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

# Lade das komplette Audiofile mit PyDub
audio = AudioSegment.from_wav(audio_file)

# Überprüfe, ob das Verzeichnis "phonemes" existiert, und erstelle es, wenn nicht
if not os.path.exists('phonemes'):
    os.makedirs('phonemes')

# Extrahiere das erste Phonem und dessen Startzeit für jedes Wort
results = []
for segment in result['segments']:
    for word_info in segment['words']:
        word = word_info['word'].strip()  # Stelle sicher, dass kein führender/abschließender Leerzeichen vorhanden ist
        start_time = int(word_info['start'] * 1000 - 300)  # Konvertiere Sekunden in Millisekunden
        first_phoneme = get_first_phoneme(word)
        if first_phoneme:
            results.append((first_phoneme, start_time))
            # Schneide das Audio an der Startzeit und speichere 15 Sekunden lang
            end_time = start_time + 15000  # 15 Sekunden in Millisekunden
            slice = audio[start_time:end_time]
            # Formatieren des Dateinamens als siebenstelliger Millisekunden-Code gefolgt vom Phonemnamen
            filename = f"{start_time:07d}_{first_phoneme}.wav"
            slice.export(f"phonemes/{filename}", format="wav")

# Ausgabe der Ergebnisse
for phoneme, time in results:
    print(f"Erstes Phonem: {phoneme}, Startzeit: {time}ms")