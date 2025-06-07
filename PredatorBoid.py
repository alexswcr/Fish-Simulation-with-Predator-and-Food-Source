import math

import numpy as np


class PredatorBoid():
    def __init__(self, window, grid):
        self.window = (window[1],window[0])
        self.grid = grid


        self.x, self.y = 100,100
        self.Vx = 1.6
        self.Vy = 1.6

        self.isElder = False # When a fish checks for elders, the neighbour list may contain a predator

        self.size = 10
        self.target = None # Fish it wants to catch
        self.grid.addFish(self)


    #Find the closest fish in a 12x12 cell radius, as well as the distance to this fish
    def get_closest_fish(self):
        all_visible_fish = self.grid.get_neighbour(self,vision_range=12)
        closest_fish = None
        min_distance = float(10000)
        for fish in all_visible_fish:
            if fish is not self:

                distance = math.dist((self.x,self.y),(fish.x,fish.y))
                if distance < min_distance:
                    min_distance = distance
                    closest_fish = fish


        return closest_fish,min_distance

    #Chase the closest fish and eat it if predator is close enough
    def chase_target(self):
        target, distance = self.get_closest_fish()
        self.target = target
        reach = 20
        #If there is a fish nearby
        if target:
            #If the predator is within reach of a fish (20px) then the fish is eaten
            if distance < reach:
                self.grid.wipeFish(target)
                self.target = None
                return target

            direction_x = target.x - self.x
            direction_y = target.y - self.y

            #Find how far fish is
            direction_mag = math.dist((target.x,target.y),(self.x,self.y))

            if direction_mag > 0:
                direction_x /= direction_mag
                direction_y /= direction_mag
            self.Vx += 0.5 * direction_x
            self.Vy += 0.5 * direction_y
        return False

    # Normalise and limit the speed of the predator
    def speed_limit(self):
        v_max = 1.82
        v_min = 1.2
        vel_norm = np.sqrt(self.Vx ** 2 + self.Vy ** 2)
        if vel_norm > v_max:
            self.Vx = (self.Vx / vel_norm) * v_max
            self.Vy = (self.Vy / vel_norm) * v_max
        elif vel_norm < v_min and vel_norm != 0:
            self.Vx = (self.Vx / vel_norm) * v_min
            self.Vy = (self.Vy / vel_norm) * v_min

    #Avoid edges by reflecting the current vector and adding very minor noise
    def avoid_edges(self):
        margin = 10
        if self.x < margin or self.x > self.window[0] - margin:
            self.Vx = -self.Vx + 0.01
        if self.y < margin or self.y > self.window[1] - margin:
            self.Vy = -self.Vy + 0.01

    #Updates the predator's state each frame
    def update(self):
        eaten_fish = self.chase_target()
        if eaten_fish and eaten_fish is not self:
            return eaten_fish

        self.avoid_edges()
        self.speed_limit()
        self.grid.removeFish(self)
        self.x += self.Vx
        self.y += self.Vy

        #Prevent predator from leaving bounds
        padding = 9
        self.x = np.clip(self.x, padding, self.window[0] - padding)
        self.y = np.clip(self.y, padding, self.window[1] - padding)
        self.grid.addFish(self)

    #Draw arrow of the predator
    def draw_shape(self):
        length = self.size
        kite = [[-length, 0], [0, length], [length, 0], [0, length * 2]]
        direction = np.arctan2(self.Vy, self.Vx)
        # Rotation matrix
        r_matrix = np.array([[np.cos(direction), -np.sin(direction)], [np.sin(direction), np.cos(direction)]])

        # Rotate kite and move to fish's position
        rotate_shape = np.dot(kite, r_matrix) + (self.y, self.x)
        return [(int(point[0]), int(point[1])) for point in rotate_shape]



