import export_video
from welcome_screen import show_instruction_screen

def main():
    gamewindow = window.Window("Test assets/beeps.wav")
    gamewindow.run()
    # Show the Pygame welcome window (with "Upload" button)
    audio_path = show_instruction_screen()
    if not audio_path:
        print("No audio file selected.")
        return
    print("Audio file selected:", audio_path)
    # create_window(audio_path)   # Launch visualization as needed
    export_video.merge_export(audio_path)



if __name__ == "__main__":
    main()