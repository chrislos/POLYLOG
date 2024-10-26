import parselmouth
from parselmouth.praat import call

# Pfad zum Audio-File
audio_path = 'a.wav'
output_textgrid_path = 'output_textgrid.TextGrid'

# Laden des Audio-Files
sound = parselmouth.Sound(audio_path)

speech = call(sound, "To TextGrid")