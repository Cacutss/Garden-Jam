import subprocess
import os
import welcome_screen

def ensure_folder_not_empty(folder):
    """
    Raises a FileNotFoundError if the specified folder contains no files.
    """
    # List all files and directories in the folder
    contents = os.listdir(folder)
    # Filter out only files (ignoring subdirectories)
    files = [name for name in contents if os.path.isfile(os.path.join(folder, name))]
    if not files:
        raise FileNotFoundError(f"No files found in folder: {folder}")

def cleanup_folder(folder):
    """
    Deletes all files in the specified folder.    
    If the folder does not exist, it prints a warning.
    If a file cannot be deleted, it prints an error for that file.
    Subdirectories inside the folder are ignored.
    """
    try:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Unexpected error for {file_path}: {e}")
    except FileNotFoundError:
            print("temp_frames folder is missing")


def get_next_filename(base_name="output", extension="mp4", folder="output"):
    """
    Returns a filename that does not already exist, by adding a number if needed.
    For example: output.mp4, output_1.mp4, output_2.mp4, etc.
    """
    os.makedirs(folder, exist_ok=True)
    counter = 0
    while True:
        if counter == 0:
            filename = f"{base_name}.{extension}"
        else:
            filename = f"{base_name}_{counter}.{extension}"
        file_path = os.path.join(folder, filename)
        if not os.path.exists(file_path):
            return file_path
        counter += 1


def merge_export(audio_path):
    #audio_path = audio_path()
    #output_path = 
    output_path = get_next_filename()  # Find a name that does not already exist
    result = None
    try:
        # Check for required files—raise or stop if not present!
        ensure_folder_not_empty("./temp_frames/")
        
        # Runs the ffmpeg command as if you typed it in the terminal
        result = subprocess.run([
            "ffmpeg",                                        # The program that turns images and audio into a video.
            "-framerate", "30",                              # Sets the video frame rate to 30 FPS.
            "-i", "./temp_frames/JSAB_finalboss_%05d.png",   # Input pattern for images; %05d matches numbers with leading zeros    
            "-i", audio_path,                 # Path to your audio file (handle spaces with quotes or as a list element)
            "-c:v", "libx264",                               # Sets the video codec to libx264 (H.264)
            "-pix_fmt", "yuv420p",                           # Sets pixel format for compatibility
            "-c:a", "aac",                                   # Sets audio codec to AAC
            output_path                                      # The video file to create (ensured to be unique).
        ])
        if result.returncode == 0:
            print(f"Video created successfully: {output_path}")
            print("ffmpeg succeeded! Cleaning up images...")            
            cleanup_folder("./temp_frames")
        else:
            print("ffmpeg failed. Video was not created.")
            print("Images not deleted.")
    
    except FileNotFoundError as e:
            print(f"Pre-check failed: {e}")
    except Exception as e:
            # Handles exceptions like ffmpeg not being installed, etc.
            print(f"A Python error occurred: {e}")