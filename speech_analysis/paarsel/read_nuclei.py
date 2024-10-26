from pydub import AudioSegment
import tgt
import os

# Load the TextGrid file
tgs = tgt.read_textgrid("adv.TextGrid")
print(tgs.get_tier_names())

tg = tgt.read_textgrid("v.TextGrid")
print(tg.get_tier_names())

word_tier = tg.get_tier_by_name("union")
print(word_tier)


# Get the "Nuclei" tier
nuclei_tier = tgs.get_tier_by_name("Nuclei")
# print(nuclei_tier)

# Load the audio file
audio = AudioSegment.from_file("a.wav")

# Ensure the directory exists
output_directory = "nuclei_audio"
os.makedirs(output_directory, exist_ok=True)

# Iterate over the points and slice the audio
for i, point in enumerate(nuclei_tier, 1):
    start_time = int(point.time * 1000)  # convert to milliseconds
    end_time = min(len(audio), start_time + 15000)  # 15 seconds after the point
    sliced_audio = audio[start_time:end_time]
    # Export each sliced audio segment to the specified directory
    sliced_audio.export(os.path.join(output_directory, f"nuclei_{i}.wav"), format="wav")


