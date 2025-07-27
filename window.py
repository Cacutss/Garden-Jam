import pygame
import numpy
import frogboard
import subprocess
import audio_extractor
import threading
import queue
import export_video
from constants import *

AUDIO_FILE="./Test assets/DeepDive.ogg"

class Bar:
    def __init__(self,x:int,y:int,width:int):
        self.rect = pygame.Rect((x,y),(width,0))
        self.color = BAR_COLOR + (BAR_TRANSPARENCY,)

    def update(self,data):
        #max is half the screen so 255 / 255 * 540 = 540
        height = (data / 255) * (WIN_HEIGHT/2)
        self.rect.y = WIN_HEIGHT - height
        self.rect.height = height 

    def draw(self,screen):
        temp_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        # Draw the bar with transparency
        pygame.draw.rect(temp_surface, self.color, (0, 0, self.rect.width, self.rect.height))
        # Blit to main screen at the right position
        screen.blit(temp_surface, self.rect)

class BarGroup:
    def __init__(self,amount:int,x:int,width:int,barwidth:int):
        #x is the position of the upper left corner in the x axis
        self.x = x
        #width is the width of the entire group of bars, basically screen size divided by number of bargroups
        self.width = width
        #width of each bar
        self.barwidth = barwidth
        #list of all bars
        self.bars = []
        for i in range(amount):
            self.bars.append(Bar(x=self.x + (self.barwidth*i),y=WIN_HEIGHT,width=self.barwidth - 10))

    def update(self,data):
        for i in range(len(self.bars)):
            self.bars[i].update(data)

    def draw(self,screen):
        for i in range(len(self.bars)):
            self.bars[i].draw(screen)

def draw_rect(rect,screen,color):
    pygame.draw.rect(surface=screen,color=color,rect=rect)

class Window():
    def __init__(self,audio_path):
        self.screen = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT),pygame.SRCALPHA,pygame.HIDDEN)
        self.audio_path = audio_path
        self.audio_data = audio_extractor.AudioDataSet(audio_path)
        self.bargroups = []  
        self.car_cooldown = [0,0,0,0,0,0,0,0,0,0]
        self.frogboard = frogboard.Frogger_Board()

    def update(self,data):
        self.frogboard.update()
        for i in range(len(data)):
            if self.car_cooldown[i] == 0:
                if data[i] > 250:
                    self.frogboard.generate_car(i)
                    self.car_cooldown[i] = 30
            else:
                self.car_cooldown[i] -= 1
        for i in range(len(self.bargroups)):
            self.bargroups[i].update(data[i])

    def draw(self):
        for i in range(len(self.bargroups)):
            self.bargroups[i].draw(self.screen)
        cars = self.frogboard.get_all_car_rects()
        frog = self.frogboard.get_frog_rect()
        for car in cars:
            draw_rect(car,self.screen,CAR_COLOR_LEFT)
        draw_rect(frog,self.screen,FROG_COLOR)

    def run(self):
        pygame.init()
        #you can change display flags, example : pygame.FULLSCREEN gives you fullscreen duh, there's also filters you can apply here.
        pygame.display.set_caption("Visualizer")
        #framecount is the count used to name frames in temp_frames folder
        framecount = 1
        #totalframes is the number we iterate on to create each frame
        totalframes = self.audio_data.get_total_frames()
        frame_queue = queue.Queue(maxsize=50)
        saving_thread = threading.Thread(target=save_frame_temp,args=(frame_queue,export_video.get_next_filename()))
        saving_thread.start()
        for i in range(0,10):
            #divides the screen in 10 to fit all 10 bar groups
            x = int(WIN_WIDTH *(i/10))
            #gives all the bargroups the same width
            width = int(WIN_WIDTH/10)
            #gives all the bars their unique spacing
            self.bargroups.append(BarGroup(amount=4,x = x,width=width,barwidth=int(width/4)))
        for frame in range(totalframes):
            print(f"{frame}/{totalframes}")
            self.screen.fill((0,0,0))
            data = self.audio_data.get_visual_ranges(frame_index=frame)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    frame_queue.put(None)
                    return 0
            #updates everything
            self.update(data)
            #draws everything
            self.draw()
            pygame.display.update()
            #saves screen to folder
            frame_queue.put(self.screen.copy())
            framecount += 1
        pygame.quit()
        frame_queue.put(None)
        frame_queue.join()
        saving_thread.join()

def save_frame_temp(queue,output_path):
    print("starting saving thread")
    ffmpeg_cmd = [
            'ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-pix_fmt', 'bgra',  # Pygame often gives BGRA byte order with alpha
            '-s', f"{WIN_WIDTH}x{WIN_HEIGHT}",
            '-r', "60",
            '-i', 'pipe:',
            "-i", AUDIO_FILE,          # Path to your audio file (handle spaces with quotes or as a list element)
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            output_path
    ]

    ffmpeg_process = None
    try:
        ffmpeg_process = subprocess.Popen(ffmpeg_cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        while True:
            #queue.get() gets a frame or waits if there is no frame, queue is basically a list that when you use put() you put into the queue
            frame = queue.get()
            #we send none once it's finished
            if frame is None:
                queue.task_done()
                break

            raw_data = pygame.image.tostring(frame,'BGRA')

            ffmpeg_process.stdin.write(raw_data)
            
            queue.task_done()
        ffmpeg_process.stdin.close()
        ffmpeg_process.wait()
        print(f"saving finished: ffmpeg process exited with {ffmpeg_process.returncode}")

        if ffmpeg_process.returncode != 0:
            print("Ffmpeg error output:")
            print(ffmpeg_process.stderr.read().decode())
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please ensure ffmpeg is installed and in your PATH")
    except Exception as e:
        print(f"Error in saving thread:{e}")
    finally:
        if ffmpeg_process and ffmpeg_process.poll() is None: # If process is still running
            ffmpeg_process.terminate()
            ffmpeg_process.wait(timeout=5) # Wait a bit
        if ffmpeg_process and ffmpeg_process.poll() is None: # If still running
            ffmpeg_process.kill() 
        print("Saving thread finished.")

