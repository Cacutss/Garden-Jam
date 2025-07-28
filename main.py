import window
from tk_welcome_screen import show_instruction_screen_tk
import subprocess
import os

def main():
    # Show the Pygame welcome window (with "Upload" button)
    audio_path = show_instruction_screen_tk()
    if not audio_path:
        print("No audio file selected.")
        return
    print("Audio file selected:", audio_path) 
    
    #Launch the standalone progress bar window
    progressbar_proc = subprocess.Popen(["python3", "progress_bar_tk.py"])


    gamewindow = window.Window(audio_path)
    filepath = gamewindow.run()
    # create_window(audio_path)   # Launch visualization as needed

    #After good processing, terminate the progress bar window (if it's still open)
    try:
        progressbar_proc.terminate()
    except Exception:
        pass
    if os.name == "nt":
        os.startfile(filepath)
    else:
        subprocess.Popen(['xdg-open','output'])

if __name__ == "__main__":
    main()
