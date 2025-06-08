import math

import numpy as np

from PredatorBoid import PredatorBoid


class FishBoid():
    def __init__(self, window, colour, grid, foodpoints, evo_and_learn, stochastic,reproduce_time):
        self.colour = colour
        self.age = 0
        # Random starting position and starting velocity
        self.x, self.y = np.random.uniform(0.1, 0.9) * window[1], np.random.uniform(0, 0.9) * window[0]

        self.Vx = np.random.uniform(-3, 3)
        self.Vy = np.random.uniform(-3, 3)

        # A bug has caused the x, y-axis of the fish to be reversed, therefore this makes sure the fish are at the right
        # positions
        self.window = (window[1], window[0])

        self.foodpoints = foodpoints
        # Enables/disables these features based on initialising arguments
        self.evo_and_learn = evo_and_learn
        self.stochastic = stochastic
        # This is the genotype of the fish, it affects:
        # 1. Separation force
        # 2. Alignment force
        # 3. Cohesion force
        # 4. food pull force
        # 5. predator push force
        # 6. Hunger threshold
        # Each gene has a different range of values, as certain extreme values can cause the boids to break, therefore
        # limiting the range of values independently prevents this
        # This is used as the basis for Table 1 in the report
        self.S_co = np.random.uniform(0.25, 3)  # Gene 1
        self.A_co = np.random.uniform(0.001, 3)  # Gene 2
        self.C_co = np.random.uniform(0.001, 1)  # Gene 3
        self.f_strength = np.random.uniform(0.01, 5)  # Gene 4
        self.p_strength = np.random.uniform(0.01, 5)  # Gene 5
        self.Hungry_co = np.random.uniform(0.05, 0.95)  # Gene 6

        self.grid = grid


        # Each fish starts with a random number of hunger, this is primarily to prevent fish all starving at once
        self.Hunger = np.random.randint(1500, 1900)

        self.maxHunger = 1900

        # Finds the exact threshold value
        self.Hungry_Level = np.round(self.maxHunger * self.Hungry_co)

        # Number of ticks before a fish can reproduce, random initial value is to prevent all fish breeding at once
        self.reproduceTime = reproduce_time
        self.reproduce_timer = np.random.randint(0, 300)

        # The initially created fish are neither elders nor juveniles, these are changed to True in the simulate fucntion
        self.isJuvenile = False
        self.isElder = False

    def avoidEdge(self):
        margin = 20
        # The graph of 1/x^2 diverges to infinity as x gets closer to 0, therefore,
        # the closer a fish is to the wall, the stronger the aversive force, smoothly pushing it away
        if self.x != 0 and self.x != self.window[0]:
            force_x = 200 * (1 / (self.x ** 2) - 1 / ((self.x - self.window[0]) ** 2))  # + np.random.uniform(-0.1,0.1)
            self.Vx += np.clip(force_x, -10, 10)
        if self.y != 0 and self.y != self.window[1]:
            force_y = 200 * (1 / (self.y ** 2) - 1 / ((self.y - self.window[1]) ** 2))  # + np.random.uniform(-0.1,0.1)
            self.Vy += np.clip(force_y, -10, 10)

        # If the fish hits the boundary, to prevent it from leaving, sharply turn it 180 degrees
        if self.x < margin or self.x > self.window[0] - margin:
            self.Vx = -self.Vx
        if self.y < margin or self.y > self.window[1] - margin:
            self.Vy = -self.Vy

    # Finds the x and y vector from the predator to the fish and adds it to current velocity
    def avoidPredator(self, predator):
        dx = self.x - predator.x
        dy = self.y - predator.y

        self.Vx += self.p_strength * dx
        self.Vy += self.p_strength * dy

    # Checks whether a fish is hungry, if so, adds a force pulling the fish towards the nearest food point
    def goToFood(self):
        anyActiveFood = any([foodpoint.active for foodpoint in self.foodpoints])
        if self.Hunger < self.Hungry_Level and anyActiveFood:
            # Get foodpoint with the lowest Euclidean distance from the fish
            foodpoints = [fp for fp in self.foodpoints if fp.active]
            foodlist = [math.dist((self.y, self.x), (foodpoint.y, foodpoint.x)) for foodpoint in foodpoints]

            closest_food = foodpoints[np.argmin(foodlist)]
            dx = closest_food.x - self.x
            dy = closest_food.y - self.y
            if self.stochastic:
                dx += np.random.normal(0, 5)
                dy += np.random.normal(0, 5)

            distance = math.sqrt(dx ** 2 + dy ** 2)

            self.Vx += self.f_strength * dx / distance
            self.Vy += self.f_strength * dy / distance

    # Checks whether the fish is near to any other fish, if so, then reproduce with the first neighbouring fish
    # It employs a tournament genetic algorithm, that crosses over the parents genes (with bias towards the eldest)
    # Mutation is added as a simple gaussian noise to each value, given the range of values for each gene differs
    # the amount of noise also differs
    def reproduce(self):
        partner = self.grid.getPartner(self)
        if isinstance(partner, FishBoid) and partner is not self:
            baby_x = (self.x + partner.x) / 2
            baby_y = (self.y + partner.y) / 2
            baby_colour = np.clip(np.uint8(np.mean((self.colour, partner.colour), 0)) + np.random.randint(-20, 20, 3),
                                  0, 255)
            baby_fish = FishBoid((self.window[1], self.window[0]), baby_colour, self.grid, self.foodpoints,
                                 self.evo_and_learn, self.stochastic,self.reproduceTime)

            baby_fish.x = baby_x
            baby_fish.y = baby_y
            if self.evo_and_learn:
                new_genotype = self.TournamentGA(partner)



                baby_fish.S_co = new_genotype[0]
                baby_fish.A_co = new_genotype[1]
                baby_fish.C_co = new_genotype[2]
                baby_fish.f_strength = new_genotype[3]
                baby_fish.p_strength = new_genotype[4]
                baby_fish.Hungry_co = new_genotype[5]

            self.grid.FishList.append(baby_fish)
        else:
            self.reproduce_timer = 0

    # Updates the state of the fish at each tick
    def update(self):
        # Remove the fish from the grid
        old_x,old_y = self.x,self.y
        # Reduce hunger
        self.Hunger -= 1
        # Find neighbours
        neighbours = self.grid.get_neighbour(self, 2)
        close_neighbours = self.grid.get_neighbour(self, 1)

        # If the fish is deemed juvenile, learn from fish deemed elder in fishlist
        if self.isJuvenile and self.evo_and_learn:
            elders = [neighbour for neighbour in neighbours if neighbour.isElder]
            for elder in elders:
                self.learn(elder)

        # If a neighbour is the predator, avoid the predator
        predator_spotted = [fish for fish in neighbours if isinstance(fish, PredatorBoid)]

        if predator_spotted:
            self.avoidPredator(predator_spotted[0])

        # If the fish reproduce timer has reach the limit, the fish reproduces
        if self.reproduce_timer >= self.reproduceTime:
            self.reproduce_timer = 0
            self.reproduce()
        else:
            self.reproduce_timer += 1

        # If the fish is hungry, go to food
        self.goToFood()
        # If the fish is near a wall, avoid it
        self.avoidEdge()
        # Combines the separation,cohesion and alignment forces
        self.Combining_Steers(neighbours, close_neighbours)

        if self.stochastic:
            self.Vx += np.random.normal(0, 0.5)
            self.Vy += np.random.normal(0, 0.5)

        # Normalizes the speed and caps it at the speed limit
        self.speed_limit()

        # Transform position to vector
        self.x += self.Vx
        self.y += self.Vy

        # Stop it from leaving the screen
        padding = 20
        self.x = np.clip(self.x, padding, self.window[0] - padding)
        self.y = np.clip(self.y, padding, self.window[1] - padding)

        self.grid.updateFish(self,old_x,old_y)

        self.age += 1

    # Boid's separation cohesion and alignment are based on: Autonomous Boids
    # By Christopher Hartman∗ and Bedˇrich Benes

    # THe paper defines separation as the repulsion of neighbouring fish
    def Separation(self, neighbours):
        if not neighbours:
            return 0, 0
        else:
            separation_force_x = 0
            separation_force_y = 0
            for fish in neighbours:
                if isinstance(fish, FishBoid):
                    # Weighing the separation value by the normalised distance from self to neighbour
                    # so fish closer together have a stronger separation force
                    dx = self.x - fish.x
                    dy = self.y - fish.y
                    distance_sq = np.sqrt(dx ** 2 + dy ** 2)
                    if distance_sq > 0:
                        separation_force_x += dx / distance_sq
                        separation_force_y += dy / distance_sq
            return separation_force_x, separation_force_y

    # The paper defines cohesion as the force pushing fish to the centre of all its neighbours
    def Cohesion(self, neighbours):
        if not neighbours:
            return 0, 0
        else:
            centre = [0, 0]
            total_weight = 0.00000001  # prevent division by 0 in case there is a non-fish neighbour
            for fish in neighbours:
                if isinstance(fish, FishBoid):
                    centre[0] += fish.x
                    centre[1] += fish.y
                    total_weight += 1
            centre = tuple(axis / total_weight for axis in centre)
            return (centre[0] - self.x) * 0.1, (centre[1] - self.y) * 0.1

    # The paper defines alignment as the force to align all fish to the same heading
    def Alignment(self, neighbours):
        if not neighbours:
            return 0, 0
        else:
            total_weight = 0.00000001
            alignment_force_x = 0
            alignment_force_y = 0
            for fish in neighbours:
                if isinstance(fish, FishBoid):
                    weight = 1
                    alignment_force_x += fish.Vx
                    alignment_force_y += fish.Vy
                    total_weight += weight

            return alignment_force_x / total_weight, alignment_force_y / total_weight

    # Sum the boid forces with respect to the weightings defined by the genotype
    def Combining_Steers(self, neighbours, close_neighbours):

        cohesion = self.Cohesion(neighbours)
        separation = self.Separation(close_neighbours)
        alignment = self.Alignment(neighbours)

        self.Vx += (self.C_co * cohesion[0] + self.S_co * separation[0] + self.A_co * alignment[0])
        self.Vy += (self.C_co * cohesion[1] + self.S_co * separation[1] + self.A_co * alignment[1])

    # Normalise and limit speed of fish, giving a minor speed boost to fish in a flock
    def speed_limit(self):
        v_max = 2 if self.grid.count_flock(self) else 1.6
        v_min = 0.05

        vel_norm = np.sqrt(self.Vx ** 2 + self.Vy ** 2)

        if vel_norm > v_max:
            self.Vx = (self.Vx / vel_norm) * v_max
            self.Vy = (self.Vy / vel_norm) * v_max
        elif vel_norm < v_min:
            self.Vx = (self.Vx / vel_norm) * v_min
            self.Vy = (self.Vy / vel_norm) * v_min

    # Create the shape of the fish, rotating it to match the direction of the fishes movement
    def draw_shape(self):
        # Length of the fish
        length = 3
        # Direction of movement
        direction = np.arctan2(self.Vy, self.Vx)

        # Create basic kite
        kite = [[length, length],
                [0, length * 2.5],
                [-length, length],
                [-length, length * 0.2],
                [-length * 0.3, -length],
                [-length * 1.2, -length * 2.5],
                [0, -length * 2],
                [length * 1.2, -length * 2.5],
                [length * 0.3, -length],
                [length, length * 0.2]
                ]

        # Rotation matrix
        r_matrix = np.array([[np.cos(direction), -np.sin(direction)], [np.sin(direction), np.cos(direction)]])

        # Rotate kite and move to fish's position
        rotate_shape = np.dot(kite, r_matrix) + (self.y, self.x)
        return [(int(point[0]), int(point[1])) for point in rotate_shape]

    # Tournament GA that combines both parents genes to create a new genotype, in addition to some mutation
    def TournamentGA(self, partner):
        self_genotype = [self.S_co, self.A_co, self.C_co, self.f_strength, self.p_strength, self.Hungry_co]
        partner_genotype = [partner.S_co, partner.A_co, partner.C_co, partner.f_strength, partner.p_strength,
                            partner.Hungry_co]
        baby_genotype = self.inherit(partner, self_genotype, partner_genotype)
        self.mutate(baby_genotype)

        baby_genotype[0] = np.clip(baby_genotype[0], 0.25, 3)
        baby_genotype[1] = np.clip(baby_genotype[1], 0.0001, 3)
        baby_genotype[2] = np.clip(baby_genotype[2], 0.0001, 1)
        baby_genotype[3] = np.clip(baby_genotype[3], 0.0001, 5)
        baby_genotype[4] = np.clip(baby_genotype[4], 0.0001, 5)
        baby_genotype[5] = np.clip(baby_genotype[5], 0.0001, 0.95)

        return baby_genotype

    # Returns the genotype combining both parent's genotype, there is a bias towards the older parent
    def inherit(self, partner, self_geno, partner_geno):
        # The fitness is based on age, the fish that has lived the longest is the fittest
        self_index = self.age
        partner_index = partner.age
        baby_geno = []
        # The baby should inherit around 75% of the older fishes genes and 25% of the younger fish
        if self_index > partner_index:
            for i in range(len(self_geno)):
                chance = np.random.random()
                if i > 0.25:
                    baby_geno.append(self_geno[i])
                else:
                    baby_geno.append(partner_geno[i])
        else:
            for i in range(len(self_geno)):
                chance = np.random.random()
                if i > 0.25:
                    baby_geno.append(partner_geno[i])
                else:
                    baby_geno.append(self_geno[i])
        return baby_geno

    def mutate(self, baby_geno):
        # Creep mutation: add a small amount of noise to each gene, with gaussian distribution
        # As the range of values for each gene differs, the amount mutated also differs
        baby_geno[0] += np.random.normal(0, 0.1)
        baby_geno[1] += np.random.normal(0, 0.1)
        baby_geno[2] += np.random.normal(0, 0.03)
        baby_geno[3] += np.random.normal(0, 0.15)
        baby_geno[4] += np.random.normal(0, 0.15)
        baby_geno[5] += np.random.normal(0, 0.06)

    # Social learning, juvenile fish slowly align their genotype to nearby elders at a slow rate
    def learn(self, elder):
        learning_rate = 0.0003
        self.S_co += learning_rate * (elder.S_co - self.S_co)
        self.A_co += learning_rate * (elder.A_co - self.A_co)
        self.C_co += learning_rate * (elder.C_co - self.C_co)
        self.f_strength += learning_rate * (elder.f_strength - self.f_strength)
        self.p_strength += learning_rate * (elder.p_strength - self.p_strength)
        self.Hungry_co += learning_rate * (elder.Hungry_co - self.Hungry_co)
