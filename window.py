import pygame
import os
import numpy
import frogboard
import subprocess
import audio_extractor
import threading
import queue
import export_video
from constants import *


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

class RGB_Cycle:

    def __init__(self,color): #rgb are ints that represent color, calc is whether that value should increase or not.
        r,g,b = color
        self.color = [r,g,b]
        self.step = 1
        self.phase = 0  # 0-5 for the 6 transitions - R, Y, G, C, B, P
        

    def cycle(self): #increases/decreases color values based on the correct transition
        if self.color == [255,0,0]: self.phase = 0
        if self.color == [255,255,0]: self.phase = 1
        if self.color == [0,255,0]: self.phase = 2
        if self.color == [0,255,255]: self.phase = 3
        if self.color == [0,0,255]: self.phase = 4
        if self.color == [255,0,255]: self.phase = 5

        if self.phase == 0: self.color[1] += 1
        if self.phase == 1: self.color[0] -= 1
        if self.phase == 2: self.color[2] += 1
        if self.phase == 3: self.color[1] -= 1
        if self.phase == 4: self.color[0] += 1
        if self.phase == 5: self.color[2] -= 1


    def get_color(self):
        return self.color[0],self.color[1],self.color[2]


class Bar:
    def __init__(self,x:int,y:int,width:int):
        self.rect = pygame.Rect((x,y),(width,0))
        self.color = BAR_COLOR + (BAR_TRANSPARENCY,)

    def update(self,data):
        #max is half the screen so 255 / 255 * 540 = 540
        height = (data / 255) * BAR_MAX_HEIGHT
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

class CarRender:
    def __init__(self,rect,color):
        self.rect = rect

def draw_rect(rect,screen,color):
    pygame.draw.rect(surface=screen,color=color,rect=rect)

class Window():
    def __init__(self,audio_data):
        self.screen = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT),pygame.SRCALPHA)
        self.audio_data = audio_data
        self.bargroups = []  
        self.car_cooldown = [0,0,0,0,0,0,0,0,0,0]
        self.frogboard = frogboard.Frogger_Board()
        self.rgb = RGB_Cycle(CAR_COLOR)

    def determine_car_generation(self,frame_index):
        left = self.audio_data.get_visual_ranges(frame_index=frame_index,direction="left")
        center = self.audio_data.get_visual_ranges(frame_index=frame_index,direction="center")
        right = self.audio_data.get_visual_ranges(frame_index=frame_index,direction="right")
        determined_directions = []

        def determine_direction(l,r,c):
            if l - 100 > r:
                return "left"
            if r - 100 > l:
                return "right"
            return "center"
        
        for i in range (len(left)):
            determined_directions.append(determine_direction(left[i],center[i],right[i]))

        for i in range (len(left)):
            if self.car_cooldown[i] == 0:
                if self.audio_data.get_visual_ranges(frame_index=frame_index,direction=determined_directions[i])[i] > 250:
                    self.frogboard.generate_car(i,determined_directions[i])
                    self.car_cooldown[i] = 50
            else:
                self.car_cooldown[i] -= 1

    def update(self,data,frame):
        self.frogboard.update()
        self.rgb.cycle()
        self.determine_car_generation(frame)
        for i in range(len(self.bargroups)):
            self.bargroups[i].update(data[i])

    def draw_car(self,car,screen,color):
        draw_rect(car,screen,color)

    def draw(self):
        for i in range(len(self.bargroups)):
            self.bargroups[i].draw(self.screen)
        cars = self.frogboard.get_all_car_rects()
        frog = self.frogboard.get_frog_rect()
        for car in cars:
            self.draw_car(car,self.screen,self.rgb.get_color())
        draw_rect(frog,self.screen,FROG_COLOR)

    def run(self):
        pygame.init()
        pygame.display.set_caption("Visualizer")

        #you can change display flags, example : pygame.FULLSCREEN gives you fullscreen duh, there's also filters you can apply here.
       
        #framecount is the count used to name frames in temp_frames folder
        #totalframes is the number we iterate on to create each frame

        totalframes = self.audio_data.get_total_frames()
        frame_queue = queue.Queue(maxsize=10)
        saving_thread = threading.Thread(target=save_frame_temp,args=(frame_queue,get_next_filename(),self.audio_data.filepath))
        saving_thread.start()

        for i in range(0,10):
            #divides the screen in 10 to fit all 10 bar groups
            x = int(WIN_WIDTH *(i/10))
            #gives all the bargroups the same width
            width = int(WIN_WIDTH/10)
            #gives all the bars their unique spacing
            self.bargroups.append(BarGroup(amount=4,x = x,width=width,barwidth=int(width/4)))
        for frame in range(totalframes):
            percent = int((frame + 1) / totalframes * 100)
            with open("progress.txt", "w") as f:
                f.write(str(percent))
            print(f"{frame}/{totalframes}")
            self.screen.fill((0,0,0))
            data = self.audio_data.get_visual_ranges(frame_index=frame,direction="center")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    frame_queue.put(None)
                    frame_queue.join()
                    saving_thread.join()
                    return 0
            #updates everything
            self.update(data,frame)
            #draws everything
            self.draw()           
            
            pygame.display.update()
            
            frame_queue.put(self.screen.copy())
            
        pygame.quit()
        frame_queue.put(None)
        frame_queue.join()
        saving_thread.join()

def save_frame_temp(queue,output_path,audio_path):
    print("starting saving thread")
    ffmpeg_cmd = [
            'ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-pix_fmt', 'bgra',  # Pygame often gives BGRA byte order with alpha
            '-s', f"{WIN_WIDTH}x{WIN_HEIGHT}",
            '-r', "60",
            '-i', 'pipe:',
            "-i", audio_path,          # Path to your audio file (handle spaces with quotes or as a list element)
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-crf', '23',
            '-c:a', 'aac',
            output_path
    ]
    count = 1
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
           
            try:
                ffmpeg_process.stdin.write(raw_data)
            except Exception as e:
                print("I AM AN EXCEPTION, WRITE FAILED")
                print(f"Error writing frame to ffmpeg at frame {count}: {e}")
                # Print ffmpeg's status and stderr right here!
                try:
                    ffmpeg_process.stdin.close()
                except Exception:
                    pass
                ffmpeg_process.wait()
                print(f"ffmpeg returncode: {ffmpeg_process.returncode}")
                print("Ffmpeg error output:")
                print(ffmpeg_process.stderr.read().decode())
                break

            queue.task_done()
            count+=1
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
        
