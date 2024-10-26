from pydub import AudioSegment
import tgt

# Load your TextGrid file
tg = tgt.read_textgrid("long.TextGrid")
ipu_tier = tg.get_tier_by_name("union")
fb_p2 = ipu_tier.get_annotations_with_text(r"speech")

# Load your audio file
audio = AudioSegment.from_file("a.wav")

# Iterate over the intervals and slice the audio
for interval in fb_p2:
    start_time = int(interval.start_time * 1000)  # convert to milliseconds
    end_time = int(interval.end_time * 1000)      # convert to milliseconds
    sliced_audio = audio[start_time:end_time]
    # Export each sliced audio segment
    sliced_audio.export(f"speech_{start_time}_{end_time}.wav", format="wav")