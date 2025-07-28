import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk         # For loading background image
import pygame                          # For playing click sound
import threading                       # So UI doesn't freeze on load
import tkinter.ttk as ttk              # For the progress bar

def play_click_sound(sound_path):
    # Play a sound when the upload button is clicked
    pygame.mixer.init()
    sound = pygame.mixer.Sound(sound_path)
    sound.play()

def show_instruction_screen_tk():
    selected_audio = None
    dataset = None
    root = tk.Tk()                                  # Main Tkinter window
    root.title("Welcome to Frog Jam!")
    
    # Window size
    window_width = 620
    window_height = 550

    # Get the monitor size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate position for centering
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    # Set the geometry and position of the window
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.resizable(False, False)

    # Load and display background image
    bg_img = Image.open("./resources/images/background_welcome_screen.png")
    bg_img = bg_img.resize((620, 550))
    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Show instruction labels at the top
    instructions = [
        "Welcome to the FrogJam!",
        "Click the button below to upload an audio file.",
        "Visualization will start after precomputing.",
        "Please review the result upon completion."
        
    ]
    for idx, line in enumerate(instructions):
        label = tk.Label(
            root,
            text=line,
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#333333"
        )
        label.place(relx=0.5, y=20 + idx*28, anchor="n")  # Center horizontally    
   
   # Create a progress bar (initially hidden)
    progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    progress.place(x=110, y=380)
    progress.place_forget()


    def on_upload():
        nonlocal selected_audio, dataset
        play_click_sound("./resources/sounds/click.wav")
        
        # Open file dialog for audio selection
        audio_path = filedialog.askopenfilename(
            title="Select an audio file",
            filetypes=[("Audio Files", "*.wav *.mp3 *.flac"), ("All Files", "*.*")]
        )        
        
        if audio_path:
            selected_audio = audio_path
            progress.place(x=110, y=380) # Show the progress bar
            progress["value"] = 0

            # Update the progress bar from another thread safely
            def update_progress_bar(current, total):
                root.after_idle(lambda: progress.config(value=current, maximum=total))

            def do_loading():
                import audio_extractor
                # Build AudioDataSet and update progress bar as each frame is processed
                nonlocal dataset
                dataset = audio_extractor.AudioDataSet(
                    audio_path,
                    progress_callback=update_progress_bar
                )
                root.after_idle(root.destroy)     # Close window when done

            threading.Thread(target=do_loading, daemon=True).start()  # Avoid blocking UI. Without a thread, the UI would freeze until do_loading finishes.

    # Upload button
    button = tk.Button(
        root, text="Upload Audio File",
        font=("Arial", 15, "bold"),
        fg="black", bg="#FFD700", activebackground="#FFA500",
        borderwidth=4, relief="raised",
        command=on_upload
    )
    button.place(x=340, y=450, width=250, height=60)

    root.mainloop()         # Show the window and wait for actions
    return dataset          # Return the processed AudioDataSet after window closes

if __name__ == "__main__":
    dataset = show_instruction_screen_tk()
    if dataset:
        print(f"Loaded audio with {dataset.get_total_frames()} frames!")
    else:
        print("No audio selected.")
