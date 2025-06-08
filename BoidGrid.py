import numpy as np

class Grid:
    def __init__(self,window,cell_size):

        #Create matrix of empty lists, representing the screen space as a grid
        self.cell_size = cell_size
        self.columns = int(window[1] // cell_size)
        self.rows = int(window[0] // cell_size)
        self.grid = [[[] for i in range(self.columns)] for i in range(self.rows)]
        self.FishList = None

    def giveFishList(self,fishlist):
        self.FishList = fishlist

    # Returns the cell position of a particular x,y point
    def cell_coords(self,x,y):

        column = int(x/self.cell_size)
        row = int(y/self.cell_size)
        column = np.clip(column,0,self.columns-1)
        row = np.clip(row,0,self.rows-1)
        return row,column

    #Remove the fish from its current grid cell
    def removeFish(self,fish,x=None,y=None):
        if x is None or y is None:
            x, y = fish.x, fish.y
        row, col = self.cell_coords(x, y)
        if fish in self.grid[row][col]:
            self.grid[row][col].remove(fish)

    #This function removes all occurences of a fish in the grid
    def wipeFish(self,fish):
        counter = 0
        pos_list = []
        for row in range(self.rows):
            for col in range(self.columns):
                if fish in self.grid[row][col]:
                    self.grid[row][col].remove(fish)
                    counter += 1
                    pos_list.append([row,col])


    #Adds fish to its current cell
    def addFish(self,fish):
        row,column = self.cell_coords(fish.x,fish.y)
        self.grid[row][column].append(fish)

    def updateFish(self,fish,x,y):
        self.addFish(fish)
        self.removeFish(fish,x,y)


    #Gets fish in nearby cells
    def get_neighbour(self,fish,vision_range):
        row,column = self.cell_coords(fish.x,fish.y)
        neighbours = []
        for i in range(-vision_range,vision_range+1):
            for j in range(-vision_range,vision_range+1):
                r = row + i
                c = column + j
                if 0 < r < self.rows and 0 < c < self.columns:
                    neighbours.extend(self.grid[r][c])
                else:
                    pass
        return neighbours

    #Counts the number of neighbouring fish, if it finds 3, returns true meaning the fish is in a flock
    def count_flock(self,fish):
        neighbour_count = 0
        flock_num = 3
        row, column = self.cell_coords(fish.x, fish.y)
        for i in range(-2,3):
            for j in range(-2,3):
                r = row + i
                c = column + j
                if 0 < r < self.rows and 0 < c < self.columns:
                    neighbour_count += len(self.grid[r][c])
                if neighbour_count > flock_num:
                    return True
        return False

    #Find closest fish to reproduce with
    def getPartner(self, fish):
        partners = []
        row, column = self.cell_coords(fish.x, fish.y)
        for i in range(-3, 4):
            for j in range(-3, 4):
                r = row + i
                c = column + j
                if 0 < r < self.rows and 0 < c < self.columns:
                    partners.extend(self.grid[r][c])
                if partners:
                    return partners[0]
        return None