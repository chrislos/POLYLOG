from pydub import AudioSegment
import tgt
import os

# Load the TextGrid files
adv_tg = tgt.read_textgrid("adv.TextGrid")
v_tg = tgt.read_textgrid("v.TextGrid")

# Get the "Nuclei" tier from adv.TextGrid
nuclei_tier = adv_tg.get_tier_by_name("Nuclei")

# Get the "union" tier from v.TextGrid
union_tier = v_tg.get_tier_by_name("union")

# Load the audio file
audio = AudioSegment.from_file("a.wav")

# Directory setup for Nuclei
nuclei_output_dir = "nuclei_audio"
os.makedirs(nuclei_output_dir, exist_ok=True)

# Directory setup for speech and non-speech
speech_output_dir = "speech"
non_speech_output_dir = "non-speech"
os.makedirs(speech_output_dir, exist_ok=True)
os.makedirs(non_speech_output_dir, exist_ok=True)

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

# Process Union intervals
for interval in union_tier:
    start_time = int(interval.start_time * 1000)
    end_time = int(interval.end_time * 1000)
    sliced_audio = audio[start_time:end_time]
    folder = speech_output_dir if interval.text == "speech" else non_speech_output_dir
    sliced_audio.export(os.path.join(folder, format_filename(start_time)), format="wav")