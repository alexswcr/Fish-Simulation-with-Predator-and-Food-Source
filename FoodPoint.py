from FishBoid import FishBoid


class FoodPoint():
    def __init__(self,x,y,grid,max_capacity,size):
        self.x = x
        self.y = y
        self.grid = grid
        self.max_capacity = max_capacity
        self.capacity = max_capacity
        self.active = True
        self.internalTime = 0

        #Number of ticks the foodpoint will be disabled after running out of food
        self.TimeOut = 2800
        self.size = size

    #Feeds neighbouring fish ONLY if the fish are 'hungry' (below their respective hunger threshold)
    def detectFish(self):
        neighbours = self.grid.get_neighbour(self,self.size)
        for fish in neighbours:
            if self.active and isinstance(fish,FishBoid) and (fish.Hunger < fish.Hungry_Level):
                self.capacity -= 1
                fish.Hunger = fish.maxHunger
                self.checkActive()
        self.checkActive()

    #Controls the activation/deactivation of the foodpoint
    def checkActive(self):
        if self.active and self.capacity <= 0:
            self.internalTime = 0
            self.active = False
        elif not self.active:
            self.internalTime += 1
        
            if self.internalTime >= self.TimeOut:
                self.active = True
                self.capacity = self.max_capacity




