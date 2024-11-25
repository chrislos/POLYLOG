import os
import librosa
import soundfile as sf

# Pfad zur Audio-Datei
file_path = 'Writer_Unisono Ende.wav'

# Lade das Audiofile
audio, sr = librosa.load(file_path, sr=None)

# Erkenne die Transienten mittels der Onset-Detection-Funktion von librosa
onsets = librosa.onset.onset_detect(y=audio, sr=sr, units='samples')

# Füge das Ende des Audios hinzu, um auch den letzten Teil zu erfassen
onsets = list(onsets) + [len(audio)]

# Ordner für die Ausgabe erstellen
output_dir = 'soundset'
os.makedirs(output_dir, exist_ok=True)

# Schneide das Audio an den Transienten und speichere die Schnipsel
for i in range(len(onsets) - 1):
    start_sample = onsets[i]
    end_sample = onsets[i + 1]
    onset_samples = audio[start_sample:end_sample]
    start_ms = (start_sample / sr) * 1000  # Beginn des Schnipsels in ms
    filename = f'{int(start_ms):07d}.wav'  # Formatierung als 7-stellige Zahl
    sf.write(os.path.join(output_dir, filename), onset_samples, sr)

print(f'Audio snippets wurden im Ordner "{output_dir}" gespeichert.')