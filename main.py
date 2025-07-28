import window
from tk_welcome_screen import show_instruction_screen_tk
import subprocess
import pathlib as path
import os
import sys

def is_there_tempo():
    args = sys.argv[1:]
    tempo = False
    returnval = ""
    for arg in args:
        if arg == "--tempo":
            tempo = True
        if arg.isdigit():
            returnval = int(arg)
        if tempo == True and isinstance(returnval,int):
            return returnval
        
def main():
    tempo = is_there_tempo()
    # Show the Pygame welcome window (with "Upload" button)
    audio_path = show_instruction_screen_tk()
    if not audio_path:
        print("No audio file selected.")
        return
    print("Audio file selected:", audio_path) 
    
    #Launch the standalone progress bar window
    progressbar_proc = subprocess.Popen(["python3", "progress_bar_tk.py"])

    gamewindow = window.Window(audio_path)
    gamewindow.run()
    # create_window(audio_path)   # Launch visualization as needed

    #After good processing, terminate the progress bar window (if it's still open)
    try:
        progressbar_proc.terminate()
    except Exception:
        pass
    output_path = path.Path(os.getcwd(),"output")
    if os.name == "nt":
        os.startfile(path)
    else:
        subprocess.Popen(['xdg-open',output_path])

if __name__ == "__main__":
    main()
