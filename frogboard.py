import random
import pygame

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

DIVIDER_THICKNESS = 2

LANE_COUNT = 15

"""
The purpose of this file (and classes) is to handle the frogger game board logic
it should return a bunch of pygame.RECT objects to be rendered as cars/player/whatever else that needs rendering.

to initialize: frogger_board = Frogger_Board()

to update every frame: frogger_board.update()

to get all the car rects (for rendering): frogger_board.get_all_car_rects()

to generate a new car: frogger_board.generate_car(range_index,direction = "center")
range value is the 0-9 index that measures the frequency range.

notice that there isn't any loudness measurement in here. you can just call .generate_car multiple times if there's a really loud sound :p
but don't go overboard! you need a reasonable gap between the cars for the frog to fit in!

"""


class Frogger_Car():

    def __init__(self, range_index, speed,x,y):
        min_length = 20
        
        self.speed = speed
        self.x = x
        self.y = y
        self.w = (int(range_index*5)) + min_length #converting the 0-255 value to a more reasonable value visually, this is fully arbitrary
        self.h = 10 #arbitrary, can change later.

        self.rect = pygame.Rect(self.x, self.y,self.w,self.h)

    def update(self):
        self.x += self.speed
        self.rect = pygame.Rect(self.x, self.y,self.w,self.h)

    def __get_rect(self):
        return self.rect

class Frogger_Lane():

    def __init__(self,direction,speed,y_position,height):
        self.x = 0
        self.y = y_position
        self.w = SCREEN_WIDTH
        self.h = height

        self.direction = direction
        self.speed = speed
        if self.direction == "left":
            self.speed = 0-self.speed


        self.cars = [] # init
        self.frog = [] # init - this list will at most have one frog....... for now :p


        if self.direction == "left": #car travels to the left
            self.car_start_x = SCREEN_WIDTH
        if self.direction == "right": #car travels to the right
            self.car_start_x = 0

    def generate_car(self,range_index):
        self.cars.append(Frogger_Car(range_index,self.speed,self.car_start_x,self.y))

    def get_car_rects(self):
        rect_list = []
        for entry in self.cars:
            rect_list.append(entry.__get_rect())
        return rect_list

    def update(self):
        for entry in self.cars:
            entry.update()
        for entry in self.frog:
            entry.update()
        for i in range (len(self.cars)-1,-1, -1): #looping in reverse because that's a safer approach when deleting list entries.
            if abs(self.cars[i].x) > SCREEN_WIDTH + 1000: #dumb but effective way to detect if a car is still on screen
                self.cars.pop(i)


class Frogger_Board():

    def __init__(self):
        self.__lane_count = LANE_COUNT
        self.lanes = []

        self.__initspeed = 7

        self.divider_thickness = 2
        self.__lanesize = self.calc_lane_height()

        self.__init_lanes()

    def update(self):
        for entry in self.lanes:
            entry.update()

    def get_all_car_rects(self):
        all_car_rects = []
        for entry in self.lanes:
            for car in entry.cars:
                all_car_rects.append(car.rect)
        return all_car_rects

    def calc_lane_height(self):
        sum_of_dividers = self.divider_thickness*(self.__lane_count-1)
        sum_of_lanes = SCREEN_HEIGHT - sum_of_dividers
        return sum_of_lanes/self.__lane_count

    def __init_lanes(self):
        for i in range (0,self.__lane_count):
            direction = "left"
            if i%2 == 1: #alternate left and right
                direction = "right"
            self.lanes.append(Frogger_Lane(direction,self.__initspeed,self.__get_lane_y_value(i),self.__lanesize)) 
            #for now it's one speed fits all. i can absolutely change this later.

    def __get_lane_y_value(self,index):
        i = 0
        height = 0
        while i < index:
            height += self.divider_thickness + self.__lanesize
            i += 1
        return height
    
    def generate_car(self,range_index,direction = "center"):

        if direction == "center": #recursive call to both left and right if it's on center - 2 cars will be generated if that's the case.
            self.generate_car(range_index,"left")
            self.generate_car(range_index,"right")
            return

        # pick a random lane with the correct direction and have that lane use it's own generate_car method
        lanes_with_right_direction = []
        for entry in self.lanes:
            if entry.direction == direction:
                lanes_with_right_direction.append(entry)
            
        lane_to_generate = random.choice(lanes_with_right_direction)
        lane_to_generate.generate_car(range_index)

    
        
    
    



    

