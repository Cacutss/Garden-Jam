import librosa
import numpy as np
from pathlib import Path
import os
import soundfile as sf

from typing import List #for documentation

FILE_PATH_DEBUG = Path('Test assets')/'beeps.wav'
TARGET_FPS = 60
NUM_BIN_RANGES = 10 #these are decided by the way the visualizer is designed
NUM_BINS = 1024 #these are then divided into ranges based on an exponential scale that represents how frequencies work.
DEBUG = False


"""
The purpose of this file (and class) is to take an audio file path, extract the audio data from it, and convert it into data that is usable in pygame.
This file can actually be used as a library by itself to pass the same kind of data to any other visualizer project :)

To initialize: 
Audio = AudioDataSet(path/to/your/file.wav, tempo = None)
If you do not initialize with a tempo value, librosa will try to compute it on it's own.

To get the number of frames to render:
num_frames = Audio.get_total_frames()

To get the data for a single frame:
ranges = Audio.get_visual_ranges(frame_index, direction= "center" (default) or "left" or "right")
Returns 0-255 values for 10 frequency bands:
31Hz, 62Hz, 125Hz, 250Hz, 500Hz, 1kHz, 2kHz, 4kHz, 8kHz, 16kHz

To get the tempo/BPM:
Audio.get_bpm()

by default each one of those lists will have 10 entries, where 0 index is for the lowest notes and 9 index is for the highest notes.

"""

class AudioDataSet():

    def __init__(self,filepath,tempo = None):
    
        if not Path(filepath).exists():
            raise FileNotFoundError(f"Audio file not found: {filepath}")

        self.is_stereo = True

        try:
            raw_audio, self.__sample_rate = sf.read(filepath)
        except Exception as e:
            raise ValueError(f"Could not read audio file: {e}")
        
        hop_length = int(self.__sample_rate / TARGET_FPS)
        #Normally this would be 44100 / 60 = 735 - but this supports 48000 and other sample rates too :)

        if len(raw_audio.shape) > 1:  # Stereo
            self.__left_channel = raw_audio[:, 0]
            self.__right_channel = raw_audio[:, 1]

            #see 
            self.__processed_center = []
            self.__processed_left = []
            self.__processed_right = []


            #passing hop_length to divide the channels into TARGET_FPS fps.
            self.__left_magnitude = np.abs(librosa.stft(self.__left_channel,hop_length = hop_length, n_fft=NUM_BINS))
            self.__right_magnitude = np.abs(librosa.stft(self.__right_channel,hop_length = hop_length, n_fft=NUM_BINS))

            #these are (frequency bins, number of frames) tuples. these are AUDIO frames which are NOT 60fps unless you specify hop_length.
            print(f"Left magnitude shape: {self.__left_magnitude.shape}") 
            print(f"Right magnitude shape: {self.__right_magnitude.shape}")
        else:
            # Mono - duplicate for both channels
            self.is_stereo = False
            self.__left_magnitude = self.__right_magnitude = np.abs(librosa.stft(raw_audio,hop_length = hop_length, n_fft=NUM_BINS))

        self.num_of_ranges = 10
        self.__frequencies_to_assign = librosa.fft_frequencies(sr=self.__sample_rate, n_fft=NUM_BINS)
        self.list_freq_ranges = [31, 62, 125, 250, 500, 1000, 2000, 4000, 8000, 16000] #Standard 10 band

        print("Precomputing all audio frames...")
        self.__processed_left = []
        self.__processed_right = []
        self.__processed_center = []
        
        total_frames = self.__left_magnitude.shape[1]


        #Tempo initialization
        self.tempo = tempo
        if self.tempo == None:
            print("No tempo detected, computing BPM... this crashes right now, on it :)")
            self.__raw_tempo = librosa.beat.beat_track(
            y=self.__left_channel, 
            sr=self.__sample_rate,
            hop_length=int(self.__sample_rate / TARGET_FPS)  # Match your existing hop_length
            )[0]
            self.tempo = float(self.__raw_tempo)
            print(f"BPM detected: {self.tempo:.1f}")
        
        if total_frames > 50000:
            print(f"Warning: Large file ({total_frames} frames). This may use significant memory.")
                 
        for frame_index in range(total_frames):
            # Process each frame
            left_frame = self._compute_visual_ranges(frame_index, "left")
            right_frame = self._compute_visual_ranges(frame_index, "right")
            
            # Compute center (max of left/right)
            center_frame = []
            for i in range (0, len(left_frame)):
                if left_frame[i] > right_frame[i]:
                    center_frame.append(left_frame[i])
                else:
                    center_frame.append(right_frame[i])
            
            self.__processed_left.append(left_frame)
            self.__processed_right.append(right_frame)
            self.__processed_center.append(center_frame)


    def get_audio_frame_data(self, frame_index, direction = "left"):
        #Get magnitude data for a specific audio frame (time slice)

        n = self.__left_magnitude
        if direction == "right":
            n = self.__right_magnitude

        if frame_index >= n.shape[1]:
            raise IndexError(f"ERROR: Frame {frame_index} out of range. Max frame: {n.shape[1] - 1}")
        
        return n[:, frame_index]
    
    def get_tempo(self) -> float:
        """Get the BPM of the audio file"""
        return float(self.tempo)
    
    def map_bins_to_ranges(self,frame_data):
        #Each bin has a numeric frequency value attached to it - which should be assigned to the smallest freq range that is equal or larger than that value.
        #self.__list_freq_ranges = [31, 62, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        #so 23hz is assigned to 31hz band, 628hz is assigned to 1000hz band, 5000 is assigned to 8000 and so on...
        range_values = [0.0] * self.num_of_ranges
        range_counts = [0] * self.num_of_ranges
        for bin_index in range(len(self.__frequencies_to_assign)):
            i = 0
            freq = self.__frequencies_to_assign[bin_index]
            magnitude = frame_data[bin_index]
            while i < self.num_of_ranges:
                if freq <= self.list_freq_ranges[i]: #Tries to assign to current frequency band
                    range_values[i] += magnitude
                    range_counts[i] += 1
                    break #Success, can move on to the next for loop iteration.
                else:
                    i += 1 #Fails, if there's a larger band - try there instead.

            # Average when needed
            for i in range(self.num_of_ranges):
                if range_counts[i] > 0:
                    #range_values[i] /= range_counts[i]
                    pass #leaving this in to debug easily

        return range_values 
    
    def get_total_frames(self) -> int:
        #Get total number of audio frames available
        return self.__left_magnitude.shape[1]
    
    def dump_all_raw_data(self):
        #For debugging only, don't use this unless you know what you're doing

        return self.__left_magnitude, self.__right_magnitude
    
    def get_dbfs_ranges(self, frame_index, direction ="left"):
        # Convert to dBFS (decibels relative to full scale)
        frame_data = self.get_audio_frame_data(frame_index, direction)
        raw_ranges = self.map_bins_to_ranges(frame_data)
        dbfs_ranges = []
        for val in raw_ranges:
            if val > 0: #if it's not silent

                dbfs = 20 * np.log10(val)
                #Formula to convert magnitude value to dbfs: dbfs = 20 * log10(1.0) = 20 * 0 = 0 dBFS, dbfs = 20 * log10(0.5) = 20 * (-0.301) = -6 dBFS..
                #Good thing i know a bit about audio engineering for this one, or i would have been cooked :p
                clamped_db_value = max(-60, min(0, dbfs)) #takes care of peaks
                dbfs_ranges.append(clamped_db_value)
            
            else:
                dbfs_ranges.append(-60) #silence
        
        return dbfs_ranges

        
    def _compute_visual_ranges(self, frame_index, direction="center"):
        # This is the "master function" that takes a frame index and a direction and returns the frame magnitude data in that direction
        # By default - it will return the max values of either L/R as a representation of centered audio.
        # it also scales the result to a 0-255 range (perfect for RGB values to use in pygame).
        if direction == "center":
            L = list(map(lambda dbfs: int(((dbfs + 60) / 60) * 255),self.get_dbfs_ranges(frame_index, "left")))
            R = list(map(lambda dbfs: int(((dbfs + 60) / 60) * 255),self.get_dbfs_ranges(frame_index, "right")))

            Center_list = []
            for i in range (0,len(L)):
                if L[i] > R[i]:
                    Center_list.append(L[i])
                else:
                    Center_list.append(R[i])
            return Center_list
        
        elif direction == "left" or direction == "right":
            return list(map(lambda dbfs: int(((dbfs + 60) / 60) * 255),self.get_dbfs_ranges(frame_index, direction)))
        
        raise Exception (f"ERROR: Invalid direction string: {direction}")
    
    def get_visual_ranges(self, frame_index: int, direction: str ="center") -> List[int]:
        #and this is the one that's posing as the master function but it acually just returns a value.
        #much better performance wise to generate everything at the init stage than to calculate it every time.
        if direction == "center":
            return self.__processed_center[frame_index]
        elif direction == "left":
            return self.__processed_left[frame_index]
        elif direction == "right":
            return self.__processed_right[frame_index]
        else:
            raise ValueError(f"ERROR: Invalid direction: {direction}")


        

if DEBUG:
    n = AudioDataSet(FILE_PATH_DEBUG)
    
    print(f"Num_Of_Frames: {n.get_total_frames()}")
    
    # Check the final visual ranges
    visual_ranges = n.get_visual_ranges(0, 'left')
    print(f"Visual ranges (0-255): {visual_ranges}")
    
    # Test a frame that should have audio (not frame 0)
    print(f"\n--- Testing frame with audio (frame 50) ---")
    frame_50_visual = n.get_visual_ranges(50, 'left')
    print(f"Frame 50 visual ranges (LEFT): {frame_50_visual}")
    frame_50_visual = n.get_visual_ranges(50, 'right')
    print(f"Frame 50 visual ranges (RIGHT): {frame_50_visual}")
    frame_50_visual = n.get_visual_ranges(50)
    print(f"Frame 50 visual ranges (CENTER): {frame_50_visual}")

    # Check which ranges are consistently zero
    frame_50 = n.get_visual_ranges(50, 'left')
    print("Frame 50 ranges:")
    bands = ['31Hz', '62Hz', '125Hz', '250Hz', '500Hz', '1kHz', '2kHz', '4kHz', '8kHz', '16kHz']
    for i, (band, value) in enumerate(zip(bands, frame_50)):
        status = "ACTIVE" if value > 0 else "SILENT"
        print(f"  {band:>5}: {value:>3} {status}")
