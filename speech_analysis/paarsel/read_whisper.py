import os
import whisper
import librosa
import numpy as np
from pydub import AudioSegment
import matplotlib.pyplot as plt

# Lade das Whisper-Modell und transkribiere die Audiodatei
model = whisper.load_model("small")
audio_file = "test.wav"  # Ersetze durch den Pfad zu deiner Audiodatei
result = model.transcribe(audio_file, language="en", word_timestamps=True)

# Lade das Audiofile mit librosa
y, sr = librosa.load(audio_file, sr=None)

# Lade das Audiofile mit PyDub
audio_segment = AudioSegment.from_file(audio_file)

# Stelle sicher, dass das Ausgabeverzeichnis existiert
output_dir = 'words'
os.makedirs(output_dir, exist_ok=True)

# Funktion zur verstärkten Transientenerkennung
def detect_stronger_onset(y_segment, sr, threshold=0.02, min_duration=0.02):
    # Berechne die Kurzzeitenergie
    hop_length = 256
    frame_length = 512
    energy = np.array([
        np.sum(np.abs(y_segment[i:i+frame_length]**2))
        for i in range(0, len(y_segment) - frame_length + 1, hop_length)
    ])
    # Normalisiere die Energie
    energy = energy / np.max(energy)
    # Finde die Indizes, bei denen die Energie den Schwellwert überschreitet
    indices = np.where(energy > threshold)[0]
    if len(indices) > 0:
        # Finde den ersten Index, an dem die Energie für eine minimale Dauer über dem Schwellwert bleibt
        for idx in indices:
            duration = 0
            while idx + duration < len(energy) and energy[idx + duration] > threshold:
                duration += 1
            if duration * hop_length / sr >= min_duration:
                onset_sample = idx * hop_length
                return onset_sample
    return None

# Verarbeite jedes Wort
results = []

for segment in result['segments']:
    for word_info in segment['words']:
        word = word_info['word'].strip()
        start_time_sec = word_info['start']
        start_sample = int(start_time_sec * sr)

        # Erweitere das Analysefenster, um verzögerten Stimmeinsatz zu berücksichtigen
        analysis_duration_sec = 3.0  # Analysiere bis zu 3 Sekunden nach der Startzeit
        end_sample = start_sample + int(analysis_duration_sec * sr)
        end_sample = min(end_sample, len(y))  # Begrenze auf die Audiodauer

        # Extrahiere das Segment für die Analyse
        y_segment = y[start_sample:end_sample]

        # Verstärkte Transientenerkennung
        onset_sample = detect_stronger_onset(
            y_segment,
            sr,
            threshold=0.02,      # Schwellwert für Empfindlichkeit (je niedriger, desto empfindlicher)
            min_duration=0.01    # Minimale Dauer, die über dem Schwellwert bleiben muss
        )

        if onset_sample is not None:
            true_start_sample = start_sample + onset_sample
            true_start_time_ms = (true_start_sample / sr) * 1000  # Konvertiere in Millisekunden
        else:
            # Fallback auf die ursprüngliche Startzeit von Whisper
            true_start_time_ms = start_time_sec * 1000

        # Stelle sicher, dass der Startpunkt innerhalb der Audiodauer liegt
        audio_duration_ms = len(audio_segment)
        if true_start_time_ms >= audio_duration_ms:
            continue  # Überspringe dieses Wort

        # Schneide das Audio ab der präzisen Startzeit, Länge 15 Sekunden
        slice_end_time_ms = true_start_time_ms + 15000  # 15 Sekunden in Millisekunden
        if slice_end_time_ms > audio_duration_ms:
            # Fülle mit Stille auf, wenn nötig
            missing_duration_ms = slice_end_time_ms - audio_duration_ms
            slice_audio = audio_segment[true_start_time_ms:]
            silence_segment = AudioSegment.silent(duration=missing_duration_ms)
            slice_audio += silence_segment
        else:
            slice_audio = audio_segment[true_start_time_ms:slice_end_time_ms]

        # Benutze den Anfangsbuchstaben des Wortes im Dateinamen
        starting_letter = word[0].upper() if word else 'UNKNOWN'

        # Formatieren des Dateinamens
        filename = f"{int(true_start_time_ms):07d}_{starting_letter}.wav"
        output_path = os.path.join(output_dir, filename)
        slice_audio.export(output_path, format="wav")

        results.append((starting_letter, true_start_time_ms))

# Ausgabe der Ergebnisse
for letter, time in results:
    print(f"Anfangsbuchstabe: {letter}, Startzeit: {time:.3f} ms")