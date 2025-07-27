import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk   # pip install pillow
import pygame

def play_click_sound(sound_path):
    pygame.mixer.init()
    sound = pygame.mixer.Sound(sound_path)
    sound.play()

def show_instruction_screen_tk():
    selected_audio = None
    # Setup main Tkinter window
    root = tk.Tk()
    root.title("Welcome to Frog Jam!")
    root.geometry("620x550")
    root.resizable(False, False)
    
    # Load and display background image
    bg_img = Image.open("./resources/images/background_welcome_screen.png")
    bg_img = bg_img.resize((620, 550))
    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    # Instructions
    instructions = [
        "Welcome to the Frog Jam!",
        "Click the button below to upload an audio file.",
        "Visualization will start after file selection."
    ]
    for idx, line in enumerate(instructions):
        label = tk.Label(
            root,
            text=line,
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#333333" if idx == 0 else "#333333"
        )
        label.place(x=35, y=30 + idx*40)

    # Button callback
    def on_upload():
        nonlocal selected_audio
        play_click_sound("./resources/sounds/click.wav")
        audio_path = filedialog.askopenfilename(
            title="Select an audio file",
            filetypes=[("Audio Files", "*.wav *.mp3 *.ogg *.flac"), ("All Files", "*.*")]
        )
        if audio_path:
            selected_audio = audio_path
            root.destroy()  # close window to proceed
            # Pass audio_path to main program as needed
          
    # Styled button
    button = tk.Button(
        root, text="Upload Audio File",
        font=("Arial", 15, "bold"),
        fg="black", bg="#FFD700", activebackground="#FFA500",  # gold/yellow with hover orange
        borderwidth=4, relief="raised",
        command=on_upload
    )
    button.place(x=340, y=450, width=250, height=60)

    root.mainloop()
    return selected_audio

if __name__ == "__main__":
    show_instruction_screen_tk()
    # Proceed to Pygame game window after
