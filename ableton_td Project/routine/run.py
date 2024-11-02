import os
from moviepy.editor import VideoFileClip

soundfilename = ""

def extract_audio_from_video():
    global soundfilename
    # Get the directory where the script is running
    directory = os.path.dirname(os.path.realpath(__file__))

    # List all files in the directory
    files = os.listdir(directory)

    # Filter out files that are videos based on their extension
    video_files = [file for file in files if file.endswith(('.mp4', '.mov', '.avi', '.mkv'))]

    # Loop through the found video files
    for video_file in video_files:
        try:
            # Create a VideoFileClip object
            video_path = os.path.join(directory, video_file)
            video_clip = VideoFileClip(video_path)

            # Extract audio from the video
            audio = video_clip.audio

            # Define the output audio file path
            audio_file_path = os.path.splitext(video_path)[0] + '.wav'
            soundfilename = os.path.splitext(video_path)[0]

            # Write the audio to a WAV file
            audio.write_audiofile(audio_file_path)

            # Close the audio to release resources
            audio.close()

            print(f"Extracted audio to {audio_file_path}")

        except Exception as e:
            print(f"Error processing {video_file}: {e}")

# Call the function
extract_audio_from_video()





## Extract Nuclei

import parselmouth

# Path to your Praat script
script_path = 'scripts/SyllableNucleiv3.praat'  # Ensure this path is correct

# Arguments to the script
file_spec = '../*.wav'  # File pattern to process (adjust as needed)
pre_processing = 'None'  # Options: 'None', 'Band pass (300..3300 Hz)', 'Reduce noise'
silence_threshold_db = -25
minimum_dip_near_peak_db = 2
minimum_pause_duration_s = 0.3
detect_filled_pauses = 'yes'  # Options: 'yes', 'no'
language = 'English'  # Options: 'English', 'Dutch'
filled_pause_threshold = 1.00
data = 'TextGrid(s) only'  # Options: 'TextGrid(s) only', 'Praat Info window', 'Save as text file', 'Table'
data_collection_type = 'OverWriteData'  # Options: 'OverWriteData', 'AppendData'
keep_objects = 'yes'  # Options: 'yes', 'no'

# Prepare the arguments as a list in the exact order defined in the Praat script's form
arguments = [
    file_spec,
    pre_processing,
    str(silence_threshold_db),
    str(minimum_dip_near_peak_db),
    str(minimum_pause_duration_s),
    detect_filled_pauses,
    language,
    str(filled_pause_threshold),
    data,
    data_collection_type,
    keep_objects
]

# Run the Praat script using Parselmouth, passing only the arguments without any Sound object
try:
    result = parselmouth.praat.run_file(
        script_path,
        *arguments,
        capture_output=True  # Optional: Capture the output from the Info window
    )

    # Print the output from the Praat script
    print(result)
except parselmouth.PraatError as e:
    print(f"An error occurred while running the Praat script:\n{e}")




## Render Nuclei



from pydub import AudioSegment
import tgt
import os

# Load the TextGrid files
adv_tg = tgt.read_textgrid(soundfilename+".auto.TextGrid")

# Get the "Nuclei" tier from adv.TextGrid
nuclei_tier = adv_tg.get_tier_by_name("Nuclei")


# Load the audio file
audio = AudioSegment.from_file(soundfilename+".wav")

# Directory setup for Nuclei
nuclei_output_dir = "nucleis"
os.makedirs(nuclei_output_dir, exist_ok=True)



# Function to format filename as 7-digit number
def format_filename(time_ms):
    return f"{time_ms:07d}.wav"

# Process Nuclei points for fixed 15 seconds duration
for i, point in enumerate(nuclei_tier, 1):
    start_time = int(point.time * 1000)  # convert to milliseconds
    end_time = min(len(audio), start_time + 15000)  # 15 seconds after the point
    sliced_audio = audio[start_time:end_time]
    filename = format_filename(start_time)
    sliced_audio.export(os.path.join(nuclei_output_dir, filename), format="wav")



## Render Whisper



import os
import whisper
import librosa
import numpy as np
from pydub import AudioSegment
import torch

# Setze das Gerät auf CPU
device = torch.device("cpu")
print(f"Verwende Gerät: {device}")

# Lade das Whisper-Modell auf die CPU
model = whisper.load_model("small", device=device)
audio_file = soundfilename+".wav"  # Ersetze durch deinen Dateipfad


# Transkribiere die Audiodatei mit dem Modell auf dem ausgewählten Gerät
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
    if np.max(energy) > 0:
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

        # Erweitere das Analysefenster
        analysis_duration_sec = 3.0  # Analysiere bis zu 3 Sekunden nach der Startzeit
        end_sample = start_sample + int(analysis_duration_sec * sr)
        end_sample = min(end_sample, len(y))  # Begrenze auf die Audiodauer

        # Extrahiere das Segment für die Analyse
        y_segment = y[start_sample:end_sample]

        # Verstärkte Transientenerkennung
        onset_sample = detect_stronger_onset(
            y_segment,
            sr,
            threshold=0.02,      # Schwellwert für Empfindlichkeit
            min_duration=0.01    # Minimale Dauer über dem Schwellwert
        )

        if onset_sample is not None:
            true_start_sample = start_sample + onset_sample
            true_start_time_ms = (true_start_sample / sr) * 1000  # In Millisekunden
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