import os
import librosa
import numpy as np
from pydub import AudioSegment

# Define the directory where the audio files are located
current_dir = os.getcwd()

# List of audio file extensions to look for
audio_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.aiff', '.aif', '.m4a']

# Get a list of audio files in the current directory
audio_files = [f for f in os.listdir(current_dir) if os.path.splitext(f)[1].lower() in audio_extensions]

# Ensure the 'extracts' directory exists
output_dir = 'extracts'
os.makedirs(output_dir, exist_ok=True)

# Process each audio file
for audio_file in audio_files:
    print(f"Processing file: {audio_file}")
    # Load the audio file with librosa
    y, sr = librosa.load(audio_file, sr=None)

    # Use librosa's onset detection to detect transients
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=True, units='time')

    # Convert onset frames to time positions (in seconds)
    onset_times = onset_frames

    # Load the audio file with pydub for easier slicing and exporting
    audio_segment = AudioSegment.from_file(audio_file)

    # Process each onset
    for idx, onset_time in enumerate(onset_times):
        # Current onset time in milliseconds
        onset_time_ms = onset_time * 1000

        # Initialize end time
        end_time_ms = None

        # Search for the next suitable transient at least 5 seconds ahead
        for next_onset_time in onset_times[idx+1:]:
            time_difference = next_onset_time - onset_time
            if time_difference >= 5.0:
                end_time_ms = next_onset_time * 1000
                break

        # If no suitable next transient found, set end time to onset_time + 5 seconds or end of audio
        if end_time_ms is None:
            end_time_ms = onset_time_ms + 5000  # 5 seconds in milliseconds
            if end_time_ms > len(audio_segment):
                end_time_ms = len(audio_segment)

        # Extract the audio segment
        sample_audio = audio_segment[onset_time_ms:end_time_ms]

        # Create a filename for the extracted sample
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        output_filename = f"{base_name}_sample_{idx+1:04d}.wav"
        output_path = os.path.join(output_dir, output_filename)

        # Export the sample
        sample_audio.export(output_path, format="wav")

        print(f"Extracted sample {output_filename}")

print("Processing complete. Extracted samples are saved in the 'extracts' folder.")