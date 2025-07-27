import window
from pathlib import Path
from welcome_screen import show_instruction_screen

FILE_PATH = Path('Test assets')/'frog visualizer demo.wav'

def debug():
    # Show the Pygame welcome window (with "Upload" button)
    gamewindow = window.Window(FILE_PATH)
    gamewindow.run()
    # create_window(audio_path)   # Launch visualization as needed

debug()