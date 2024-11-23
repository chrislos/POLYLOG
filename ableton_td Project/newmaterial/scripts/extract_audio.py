import os
from moviepy.editor import VideoFileClip

def extract_audio_from_video():
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

            # Write the audio to a WAV file
            audio.write_audiofile(audio_file_path)

            # Close the audio to release resources
            audio.close()

            print(f"Extracted audio to {audio_file_path}")

        except Exception as e:
            print(f"Error processing {video_file}: {e}")

# Call the function
extract_audio_from_video()