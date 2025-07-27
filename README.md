# JamFrog
An audio visualizer with a twist, gives you a customized per audio self-playing frogger!
created in pygame and ffmpeg for [boot.dev](https://boot.dev)'s 2025 Hackathon!
## Requirements
* **Python 3.12+**
* **[ffmpeg](https://ffmpeg.org/download.html)**
* **[uv](https://github.com/astral-sh/uv#installation)**
## Installation
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
uv add librosa pygame ffmpeg-python numpy scipy pillow
```
### Now we need to install [ffmpeg](https://ffmpeg.org/download.html), to install use your preferred method [here](https://ffmpeg.org/download.html).
## Usage
### To run JamFrog you can execute the main.py file with
```
uv run main.py
```
