import tkinter as tk
import tkinter.ttk as ttk
import os

PROGRESS_FILE = "progress.txt"  # Shared file used to update progress

root = tk.Tk()
root.title("Rendering Audio&Video")        # Set the window title
root.attributes('-topmost', True)          # Keep this window always on top

# Desired window size
window_width = 420
window_height = 80

# Get the screen size
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate position for centering
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)

# Set the geometry and position of the window
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

bar = ttk.Progressbar(root, length=400, mode='determinate')  # Create a horizontal progress bar
bar.pack(padx=10, pady=10)
bar["maximum"] = 100                       # Set max value to 100 (for percent completion)

# This function checks the progress file and updates the bar
def poll_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            value = f.read().strip()
            if value.isdigit():
                bar["value"] = int(value)  # Update bar with current progress
    root.after(50, poll_progress)          # Check again after 50 ms (smooth updates)

poll_progress()                            # Start polling for progress updates
root.mainloop()                            # Start the Tkinter event loop (shows the window)
