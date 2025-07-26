import export_video
from welcome_screen import show_instruction_screen
#from window import create_window


def main():
    # Show the Pygame welcome window (with "Upload" button)
    audio_path = show_instruction_screen()
    #print(f"TESTSTSTS: {audio_path}")
    if not audio_path:
        print("No audio file selected.")
        return
    print("Audio file selected:", audio_path)
    # create_window(audio_path)   # Launch visualization as needed
    export_video.merge_export(audio_path)

if __name__ == "__main__":
    main()