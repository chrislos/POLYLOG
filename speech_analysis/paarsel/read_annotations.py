from pydub import AudioSegment
import tgt
import os

# Load the TextGrid files
tg = tgt.read_textgrid("long.TextGrid")
tgs = tgt.read_textgrid("adv.TextGrid")

# Get the tiers
words = tg.get_tier_by_name("union")
syllables = tgs.get_tier_by_name("DFauto (English)")

# Load the audio file
audio = AudioSegment.from_file("a.wav")

# Ensure the directories exist
words_dir = "words"
syllables_dir = "syllables"
os.makedirs(words_dir, exist_ok=True)
os.makedirs(syllables_dir, exist_ok=True)

print(syllables)


# # Function to export audio slices
# def export_audio_slices(intervals, directory, label="slice"):
#     for interval in intervals:
#         start_time = int(interval.start_time * 1000)  # convert to milliseconds
#         end_time = int(interval.end_time * 1000)      # convert to milliseconds
#         sliced_audio = audio[start_time:end_time]
#         # Export each sliced audio segment to the specified directory
#         sliced_audio.export(os.path.join(directory, f"{label}_{start_time}_{end_time}.wav"), format="wav")

# # Export words slices
# export_audio_slices(words, words_dir, "speech")

# # Export syllables slices (adjust as needed if you want to include non-pause intervals)
# export_audio_slices(syllables.intervals, syllables_dir, "syllable")