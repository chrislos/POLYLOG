import os
from moviepy.editor import VideoFileClip

def extract_and_cut_video(video_path, start_ms_list, duration_s):
    try:
        # Video laden
        clip = VideoFileClip(video_path)
        
        print(f"Die Videolänge beträgt {clip.duration} Sekunden.")
        
        for start_ms in start_ms_list:
            # Startzeit von Millisekunden in Sekunden umrechnen
            start_time = start_ms / 1000.0
            
            # Prüfen, ob Startzeit + Dauer innerhalb der Videolänge liegt
            if start_time + duration_s > clip.duration:
                print(f"Startzeit {start_time}s + Dauer {duration_s}s überschreitet Videolänge {clip.duration}s")
                continue
            
            # Clip zuschneiden
            cut_clip = clip.subclip(start_time, start_time + duration_s)
            
            # Ausgabe-Pfade definieren (nur Millisekundenzahl als Dateiname)
            output_video_path = f'{start_ms}.mp4'
            output_audio_path = f'{start_ms}.wav'
            
            # Geschnittenes Video mit Audio speichern
            cut_clip.write_videofile(
                output_video_path,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                audio=True
            )
            
            # Optional: Audio extrahieren und separat speichern
            # Wenn Sie die Audiodatei separat benötigen, lassen Sie diesen Teil stehen.
            # Ansonsten können Sie ihn entfernen.
            cut_clip.audio.write_audiofile(output_audio_path)
            
            # Ressourcen freigeben
            cut_clip.close()
            
            print(f"Video und Audio wurden gespeichert als {output_video_path} und {output_audio_path}")
        
        # Hauptvideo schließen
        clip.close()
    except Exception as e:
        print(f"Fehler beim Verarbeiten von {video_path}: {e}")

def main():
    # Startzeiten in Millisekunden (innerhalb der Videolänge)
    start_ms_list = [60000, 120000, 180000, 240000]  # Passen Sie die Startzeiten nach Bedarf an
    
    duration_s = 20  # Dauer in Sekunden
    
    # Videodatei angeben
    video_file = 'poly.mp4'  # Stellen Sie sicher, dass dies die richtige Videodatei ist
    
    # Prüfen, ob die Videodatei existiert
    if not os.path.isfile(video_file):
        print(f"Die Videodatei {video_file} wurde nicht gefunden.")
        return
    
    extract_and_cut_video(video_file, start_ms_list, duration_s)

if __name__ == "__main__":
    main()