import wx
import sys

def main():
    app = wx.App(False)             # Initialize the wx application (no redirect of stdout/stderr)
    dialog = wx.FileDialog(
        None,                       # No parent window
        "Select an audio file",     # Dialog title
        wildcard="Audio Files (*.wav;*.mp3;*.ogg;*.flac)|*.wav;*.mp3;*.ogg;*.flac|All Files (*.*)|*.*",  # File type filters
        style=wx.FD_OPEN            # Dialog will be file-open type
    )
    result = dialog.ShowModal()     # Show the dialog and wait for user to pick/cancel
    if result == wx.ID_OK:
        print(dialog.GetPath())     # Output the selected file path to stdout (read by your main script)
    dialog.Destroy()                # Clean up dialog window
    sys.exit(0)                     


if __name__ == "__main__":
    main()