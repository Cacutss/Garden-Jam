import export_video
import window
from welcome_screen import show_instruction_screen

def main():
    # Show the Pygame welcome window (with "Upload" button)
    audio_path = show_instruction_screen()
    if not audio_path:
        print("No audio file selected.")
        return
    print("Audio file selected:", audio_path) 
    gamewindow = window.Window(audio_path)
    gamewindow.run()
    # create_window(audio_path)   # Launch visualization as needed


if __name__ == "__main__":
    main()
