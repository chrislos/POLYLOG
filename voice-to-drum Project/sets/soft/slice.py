import os
import librosa
import soundfile as sf

# Ordner für die Ausgabe erstellen
output_dir = 'soundset'
os.makedirs(output_dir, exist_ok=True)

# Minimale und maximale Länge der Slices in Sekunden
min_len = 3
max_len = 5

# Gehe durch alle Dateien im aktuellen Verzeichnis
for file_name in os.listdir('.'):
    if file_name.endswith('.wav'):
        # Lade das Audiofile
        audio, sr = librosa.load(file_name, sr=None)

        # Erkenne die Transienten mittels der Onset-Detection-Funktion von librosa
        onsets = librosa.onset.onset_detect(y=audio, sr=sr, units='samples')

        # Füge das Ende des Audios hinzu
        onsets = list(onsets) + [len(audio)]

        # Initialisiere Startpunkt
        start_sample = onsets[0]

        # Gehe durch alle Onsets und erstelle die Slices
        for i in range(1, len(onsets)):
            end_sample = onsets[i]
            duration = (end_sample - start_sample) / sr

            # Prüfe, ob der Slice die minimale Länge erreicht oder überschreitet
            if duration >= min_len:
                # Slice das Audio und speichere es
                onset_samples = audio[start_sample:end_sample]
                start_ms = (start_sample / sr) * 1000  # Beginn des Schnipsels in ms
                filename = f'{int(start_ms):07d}.wav'  # Formatierung als 7-stellige Zahl
                sf.write(os.path.join(output_dir, filename), onset_samples, sr)
                start_sample = end_sample  # Setze den Startpunkt für den nächsten Slice
            # Wenn der Slice zu lang ist, teile ihn
            elif duration > max_len:
                max_samples = int(max_len * sr)
                while (end_sample - start_sample) > max_samples:
                    onset_samples = audio[start_sample:start_sample + max_samples]
                    start_ms = (start_sample / sr) * 1000
                    filename = f'{int(start_ms):07d}.wav'
                    sf.write(os.path.join(output_dir, filename), onset_samples, sr)
                    start_sample += max_samples

print(f'Audio snippets wurden im Ordner "{output_dir}" gespeichert.')