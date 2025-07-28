import window
from tk_welcome_screen import show_instruction_screen_tk
import subprocess
import platform
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
    return None
        
def main():
    tempo = is_there_tempo()
    # Show the Pygame welcome window (with "Upload" button)
    audio_dataset = show_instruction_screen_tk()
    if not audio_dataset:
        print("No audio file selected.")
        return
    print("Audio file selected:", audio_dataset.filepath) 
    
    #Launch the standalone progress bar window
    progressbar_proc = subprocess.Popen([sys.executable, "progress_bar_tk.py"])

    gamewindow = window.Window(audio_dataset)
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
<<<<<<< HEAD
        if "Microsoft" in platform.uname().release:
            os.system(f"explorer.exe {output_path}")
=======
        uname_info = platform.uname().release.lower()
        if "microsoft" in uname_info or "wsl" in uname_info:
            print("Seems you're using wsl!'")
            print(f"Output folder is in {output_path}")
>>>>>>> 3ca0ec9 (graceful handling)
        else:
            subprocess.Popen(['xdg-open',output_path])

if __name__ == "__main__":
    main()
