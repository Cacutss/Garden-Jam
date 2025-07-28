# JamFrog
An audio visualizer with a twist, gives you a customized per audio self-playing frogger!
created in pygame and ffmpeg for [boot.dev](https://boot.dev)'s 2025 Hackathon!
## Requirements
* **Python 3.12+**
* **[ffmpeg](https://ffmpeg.org/download.html)**
* **[uv](https://github.com/astral-sh/uv#installation)**
* **The audio file that you want to visualize - use a .wav file, if you don't the musical overnerds will smite you :)**
## Installation
Clone the repo or download it directly and unzip it
```
git clone https://github.com/Cacutss/JamFrog
```
If you don't have **uv** installed, you can install it [here](https://github.com/astral-sh/uv#installation).
### Initialize the project
```
uv init
```
### Now you have to install the dependencies, if you don't want to install dependencies on your whole system, you can do so in a virtual environment. To initialize a virtual environment
```
uv venv
```
### Now you should source into it
```
source .venv/bin/activate
```
### To install dependencies use this command
```
uv add librosa pygame numpy scipy pillow
```
Note: if you are on **Linux** you might need to install tkinter
```
sudo apt-get install python3-tk
```
### Now we need to install [ffmpeg](https://ffmpeg.org/download.html), to install use your preferred method [here](https://ffmpeg.org/download.html).
## Usage
### To run JamFrog you can execute the main.py file with
```
uv run main.py
```
### Flags
For now there's just one flag.  
```
uv run main.py --tempo (number)
```
accepts any positive integer and represents the tempo of the audio chosen. Why user input? because librosa is very innacurate on this part.
You can refer to https://www.beatsperminuteonline.com/ on how to calculate those, anyways this program will try it's best to guess the audio tempo even if you don't specify it
