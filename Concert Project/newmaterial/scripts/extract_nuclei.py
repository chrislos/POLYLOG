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
data = 'Praat Info window'  # Options: 'TextGrid(s) only', 'Praat Info window', 'Save as text file', 'Table'
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