import export_video
import window

def main(): 
    gamewindow = window.Window("Test assets/cat.mp3")
    gamewindow.run()
    export_video.merge_export()



if __name__ == "__main__":
    main()  # Only runs main() if this script is run directly
