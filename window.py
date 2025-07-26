import pygame
import numpy
import audio_extractor 
import os

WIN_WIDTH = 1920
WIN_HEIGHT = 1080

class Bar:
    def __init__(self,x:int,y:int,width:int):
        self.rect = pygame.Rect((x,y),(width,0))
        self.color = (255,255,255)

    def update(self,data):
        #max is half the screen so 255 / 255 * 540 = 540
        height = (data / 255) * (WIN_HEIGHT/2)
        self.rect.y = WIN_HEIGHT - height
        self.rect.height = height 

    def draw(self,screen):
        pygame.draw.rect(screen,self.color,self.rect)

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

def create_temp():
    try:
        rootpath = os.getcwd()
        temp = os.path.join(rootpath,"temp_frames")
        os.mkdir(temp)
    except Exception as e:
        pass

def create_window():
    audio_path = "Test assets/cat.mp3"
    audioExtractor = audio_extractor.AudioDataSet(audio_path)
    audioExtractor = audio_extractor.AudioDataSet("Test assets/cat.mp3")
    pygame.init()
    #you can change display flags, example : pygame.FULLSCREEN gives you fullscreen duh, there's also filters you can apply here.
    screen = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT),pygame.FULLSCREEN)
    pygame.display.set_caption("Visualizer")
    framecount = 0
    totalframes = audioExtractor.get_total_frames()
    bargroups = []
    print(totalframes)
    for i in range(0,10):
        #divides the screen in 10 to fit all 10 bar groups
        x = int(WIN_WIDTH *(i/10))
        #gives all the bargroups the same width
        width = int(WIN_WIDTH/10) 
        bargroups.append(BarGroup(amount=4,x = x,width=width,barwidth=int(width/4)))
    for frame in range(totalframes):
        data = audioExtractor.get_visual_ranges(frame_index=frame)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0,0,0))
        #updates everything
        for i in range(len(bargroups)):
            bargroups[i].update(data[i])
        #draws everything
        for i in range(len(bargroups)):
            bargroups[i].draw(screen)
        pygame.display.flip()
        #saves screen to folder
        pygame.image.save(screen,f"temp_frames/screen{framecount}.png")
        framecount += 1
        #framerate should be number of frames / audio duration in seconds?

    pygame.quit()

create_temp()    
create_window()
