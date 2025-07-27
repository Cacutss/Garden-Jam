import random
import pygame
from constants import *

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

LANE_COUNT = 15 # MUST BE AN ODD NUMBER
if (LANE_COUNT % 2 != 1) or (LANE_COUNT < 1):
    raise ValueError ("LANE_COUNT must be a positive odd number!")

"""
The purpose of this file (and classes) is to handle the frogger game board logic
it should return a bunch of pygame.RECT objects to be rendered as cars/player/whatever else that needs rendering.

to initialize: frogger_board = Frogger_Board()

to update every frame: frogger_board.update()

to get all the car rects (for rendering): frogger_board.get_all_car_rects()

to get the frog rect: frogger_board.get_frog_rect()

to generate a new car: frogger_board.generate_car(range_index,direction = "center")
range value is the 0-9 index that measures the frequency range.

notice that there isn't any loudness measurement in here. we just call .generate_car multiple times if there's a really loud sound :p
but don't go overboard! you need a reasonable gap between the cars for the frog to fit in!

"""

class Froggy(): #self playing player

    def __init__(self,x,y,size,gap_between_lanes):
        self.x = x
        self.y = y
        self.w = self.h = size #identical w/h in a square

        self.x_weight = 0 #this is for prioritizing towards-center movement. 
        self.y_weight = 0

        self.rect = pygame.Rect(self.x,self.y,self.w,self.h)

        self.increment_move_x = gap_between_lanes #arbitrary, can be anything
        self.increment_move_y = gap_between_lanes #has to be this no matter what. this needs to be calculated in the board class like most calculations.

    def change_position(self,direction): #verbose, but readable - the way i like it :p
        if direction == "left":
            self.x -= self.increment_move_x
            self.x_weight -= 1
        if direction == "right":
            self.x += self.increment_move_x
            self.x_weight += 1
        if direction == "up":
            self.y -= self.increment_move_y
            self.y_weight -=1
        if direction == "down":
            self.y += self.increment_move_y
            self.y_weight +=1

    def weight_too_light_to_care(self):
        return (abs(self.x_weight) < 5) or (abs(self.y_weight) < 5) #no need to gravitate towards center yet.


    def update(self):
        self.rect = pygame.Rect(self.x,self.y,self.w,self.h)
    

class Frogger_Car():

    def __init__(self, range_index, speed,x,y):
        min_length = CAR_WIDTH_BASE
        
        self.speed = speed
        
        self.y = y
        self.w = (int(range_index*3)) + min_length #converting the 0-255 value to a more reasonable value visually, this is fully arbitrary
        self.h = CAR_HEIGHT #arbitrary, can change later.

        if x == "left":
            self.x = 0
        elif x == "right":
            self.x = SCREEN_WIDTH - self.w

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

        self.rect = pygame.Rect(self.x,self.y,self.w,self.h) #should never update.

        self.direction = direction
        self.speed = speed
        if self.direction == "left":
            self.speed = 0-self.speed


        self.cars = [] # init

        if self.direction == "left": #car travels to the left
            self.car_start_x = "right"
        if self.direction == "right": #car travels to the right
            self.car_start_x = "left"

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
        for i in range (len(self.cars)-1,0, -1): #looping in reverse because that's a safer approach when deleting list entries.
            if abs(self.cars[i].x) > SCREEN_WIDTH + 1000: #dumb but effective way to detect if a car is still on screen
                self.cars.pop(i)


class Frogger_Board():

    def __init__(self):
        self.__lane_count = LANE_COUNT
        self.lanes = []

        self.__initspeed = CAR_SPEED

        self.divider_thickness = 2
        self.__lanesize = self.calc_lane_height()
        self.move_cooldown = 0
        
        self.__init_lanes()

        self.frog = self.__init_frog()

    def __init_lanes(self):
        for i in range (0,self.__lane_count):
            direction = "left"
            if i%2 == 1: #alternate left and right
                direction = "right"
            self.lanes.append(Frogger_Lane(direction,self.__initspeed,self.__get_lane_y_value(i),self.__lanesize)) 
            #for now it's one speed fits all. i can absolutely change this later.

    def __init_frog(self):
        x = (SCREEN_WIDTH/2) - (FROG_SIZE/2)
        correct_lane = self.lanes[int(LANE_COUNT/2)]
        y = correct_lane.y + (correct_lane.h/2) - (self.calc_lane_height()/2) #- (FROG_SIZE/2)
        size = FROG_SIZE
        gap_between_lanes = self.__lanesize + self.divider_thickness
        return Froggy(x,y,size,gap_between_lanes)
    
    def get_all_car_rects(self):
        all_car_rects = []
        for entry in self.lanes:
            for car in entry.cars:
                all_car_rects.append(car.rect)
        return all_car_rects
    
    def get_frog_rect(self):
        return self.frog.rect
    
    def update(self):
        for entry in self.lanes:
            entry.update()
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
        self.determine_next_frog_position()
        self.frog.update()
    
    def determine_next_frog_position(self):
        if self.frog_should_move():
            self.find_where_to_move_and_move_there()
    
    def frog_should_move(self):

        #emergency movement (car too close) goes here:
        if self.move_cooldown >= 32:
            return False
        elif self.move_cooldown != 0: #at this point, most of the cooldown is still in place - only move when you REALLY have to

            def identify_frog_lane():
                for i in range(0, len(self.lanes)):
                    if self.frog.rect.colliderect(self.lanes[i].rect):
                        return i
                raise Exception (f"frog went out of bounds, frog rect is {self.frog.rect}")
                    
            x_to_check = self.frog.x + (self.frog.w/2)
                    
            def check_if_car_is_too_close():
                nonlocal x_to_check
                lane = self.lanes[identify_frog_lane()]
                for car_rect in lane.cars:
                    distance_to_check = x_to_check - (car_rect.x + (car_rect.w/2))
                    if abs(distance_to_check) < (self.frog.w*3): #arbitrary distance check passes
                        if lane.direction == "left" and distance_to_check <= 0:
                            return True
                        if lane.direction == "right" and distance_to_check >= 0:
                            return True
                return False
            
            
            def check_if_too_close_to_edge():
                nonlocal x_to_check
                edge_margin = FROG_SIZE*10 
                if (x_to_check < edge_margin) or (x_to_check > SCREEN_WIDTH - edge_margin):
                    return True
                y_to_check = self.frog.x + (self.frog.h/2)
                if (y_to_check < edge_margin) or (y_to_check > SCREEN_HEIGHT - edge_margin):
                    return True
                
            return check_if_car_is_too_close() or check_if_too_close_to_edge()
            
        elif random.randint(1, 50) == 1: #wanders around even if it does not "want" to. just for randomness sake 
            return True
        
        elif random.randint(1, 10) and self.frog.weight_too_light_to_care: #wanders around when it "wants" to
            return True
    
        return False
        
        
            
    
    def find_where_to_move_and_move_there(self): #oh boy this is some code of all time

        edge_margin = FROG_SIZE*2 #this is not the same as the one in frog_should_move(self). that one is a "suggestion" to move. this one is mandatory.

        def move_checker(rect,direction):
            if direction == "left":
                rect.x -= self.frog.increment_move_x
            if direction == "right":
                rect.x += self.frog.increment_move_x
            if direction == "down":
                rect.y += self.frog.increment_move_y
            if direction == "up":
                rect.y -= self.frog.increment_move_y
            return rect
        
        def frog_can_move_there(direction):
            nonlocal edge_margin
            tester_rect = move_checker(self.frog.rect.copy(),direction)
            if direction == "up" or direction == "down":

                #arbitrary safety check to prevent any car crashes from adjacent lanes - TODO: check only one direction?
                margin = self.frog.increment_move_x + FROG_SIZE
                tester_rect.x -= margin 
                tester_rect.w += margin*2

            if tester_rect.x < (edge_margin) or tester_rect.x > SCREEN_WIDTH -(edge_margin): #corner detection. not exact and that's ok. we need some breathing room.
                return False
            if tester_rect.y < (edge_margin) or tester_rect.y > SCREEN_HEIGHT -(edge_margin):
                return False
            
            for car in self.get_all_car_rects():
                if car.colliderect(tester_rect):
                    return False
            return True
        
        def determine_priority_direction():
            nonlocal edge_margin
            possible_dirs = ["up", "down", "left", "right"]

            if self.frog.y - self.frog.increment_move_y < edge_margin: #check if frog close to edge
                possible_dirs.remove("up")
            if self.frog.y + self.frog.h + self.frog.increment_move_y > SCREEN_HEIGHT - edge_margin:
                possible_dirs.remove("down")
            if self.frog.x - self.frog.increment_move_x < edge_margin:
                possible_dirs.remove("left")
            if self.frog.x + self.frog.w + self.frog.increment_move_x > SCREEN_WIDTH - edge_margin:
                possible_dirs.remove("right")
                    
            dir_list = []
            if self.frog.y_weight <= 0: #arbitrary, prioritizing up over down
                if "up" in possible_dirs:
                    dir_list.append("up")
                if "down" in possible_dirs:
                    dir_list.append("down") 
            else:
                if "down" in possible_dirs:
                    dir_list.append("down") 
                if "up" in possible_dirs:
                    dir_list.append("up")
            
            #not sure if i need this at all, emergency situations need vertical movement
            rest_of_list = []
            if "left" in possible_dirs and "left" not in dir_list:
                rest_of_list.append("left")
            if "right" in possible_dirs and "right" not in dir_list:
                rest_of_list.append("right")


            random.shuffle(rest_of_list)
            dir_list.extend (rest_of_list)
            

            if self.frog.weight_too_light_to_care():
                random.shuffle(dir_list)
                
            return dir_list
        
        for dir in determine_priority_direction():
            if frog_can_move_there(dir):
                self.frog.change_position(dir)
                self.move_cooldown = 35 #TODO: needs to be a constant
                return
        
        print("WARNING: Car crash detected - maybe tweak some car generation parameters to give the frog more room to move?")
        #nowhere to move? at least run away from the car....
        if (self.frog.y_weight % 2) == 0:
            self.frog.change_position("left")
            return
        self.frog.change_position("right")
        return


    def calc_lane_height(self):
        sum_of_dividers = self.divider_thickness*(self.__lane_count-1)
        sum_of_lanes = SCREEN_HEIGHT - sum_of_dividers
        return sum_of_lanes/self.__lane_count

    def __get_lane_y_value(self,index):
        i = 0
        height = 0
        while i < index:
            height += self.divider_thickness + self.__lanesize
            i += 1
        return height
    
    def generate_car(self,range_index,direction = "center"):

        actual_direction = direction
        if direction == "center": #just pick at random. 
            if random.randint(0,1) == 1:
                actual_direction = "left"
            else:
                actual_direction = "right"

        # pick a random lane with the actual direction and have that lane use it's own generate_car method
        lanes_with_right_direction = []
        for entry in self.lanes:
            if entry.direction == actual_direction:
                lanes_with_right_direction.append(entry)

        #below is a silly way to map range index to lane choice.
        #lane counts are hardcoded i know (hi lane), but it's 3am and refactoring it at this point would require too valuable time to co-ordinate.
        #if it gets enough attention i'll refactor it for all sane lane counts, i promise :)

        if range_index >= 10 or range_index < 0:
            raise ValueError (f"range_index out of range: {range_index}")
        elif range_index < 3:
            range = [5,6]
        elif range_index < 6:
            range = [2,3,4]
        elif range_index < 10:
            range = [0,1]
        
        lanes_to_choose_from = []
        for entry in range:
            lanes_to_choose_from.append(lanes_with_right_direction[entry])
            
        lane_to_generate = random.choice(lanes_to_choose_from)
        lane_to_generate.generate_car(range_index)



DEBUG = False

if DEBUG:
    n = Frogger_Board()
    n.frog.x = 872
    n.frog.y = 504
    for i in range (5000000):
        print (f"frame {i}: frog rect = {n.frog.rect}")
        n.update()
