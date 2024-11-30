import os

# Get the current working directory (the folder containing the script)
current_folder = os.getcwd()

# List all .wav files in the folder
wav_files = [file for file in os.listdir(current_folder) if file.endswith('.wav')]

# Sort the .wav files alphabetically to ensure consistent ordering
wav_files.sort()

# Select every second file to delete
delete_files = wav_files[1::2]

# Delete the selected files
for file in delete_files:
    file_path = os.path.join(current_folder, file)
    try:
        os.remove(file_path)
        print(f"Deleted: {file}")
    except Exception as e:
        print(f"Error deleting {file}: {e}")

print("Deletion process completed.")
