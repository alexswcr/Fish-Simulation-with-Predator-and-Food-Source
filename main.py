from datetime import datetime
from multiprocessing import Process

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import numpy as np
import pandas as pd
import pygame
from matplotlib import pyplot as plt
from pygame import freetype

from BoidGrid import Grid
from FishBoid import FishBoid
from FoodPoint import FoodPoint
from PredatorBoid import PredatorBoid


# Create a random RGB value
def randomColour():
    return (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))


# Creates the pygame simulation window, can customise the window size, cell size, number of boids and locations of food
def simulate(sim_name, window, cell_size, fish_count, foodpoint_locations, evo_and_learn, stochastic):
    pygame.init()
    pygame.display.set_caption(str(sim_name))
    screen = pygame.display.set_mode(window)
    grid = Grid(window, cell_size)

    # Food points are created at the points specified above, the amount of food and size of the food point can be changed
    # In this case the foodpoint can feed 30 fish before disabling and have size 2x2 (cells)
    foodpoints = [FoodPoint(foodpoint[1], foodpoint[0], grid, 40, 2) for foodpoint in foodpoint_locations]

    # Creates a list of fish with random colours
    fishes = [FishBoid(window, randomColour(), grid, foodpoints, evo_and_learn, stochastic) for i in range(fish_count)]

    # Give grid object the fish list reference, allowing it to remove fish from grid that are dead
    grid.giveFishList(fishes)

    # Create the predator
    predator = PredatorBoid(window, grid)

    clock = pygame.time.Clock()

    Fish_eaten = 0
    Fish_starved = 0

    running = True
    Time = 0

    oldest_fish = None

    # Data collection for performance
    y = []

    # This is the gameplay loop, closes when the x button of the window is pressed
    while running:
        Time += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if not fishes:
            running = False

        # Top 10% eldest fish considered "elders", they will teach the juvenile fish
        elder_idx = len(fishes) // 10
        elders = fishes[:elder_idx]
        for elder in elders:
            elder.isElder = True

        # Youngest 20% of fish considered "juveniles", they will learn from the elders
        juvenile_idx = int((len(fishes) * 0.8))
        juveniles = fishes[juvenile_idx:]
        for juvenile in juveniles:
            juvenile.isJuvenile = True

        screen.fill((153, 238, 255))

        # Update the foodpoints, feeding fish in its radius, if it is inactive (no food left) turn red
        for foodpoint in foodpoints:
            foodpoint.detectFish()
            if foodpoint.active:
                colour = (0, 140, 0)
            else:
                colour = (140, 0, 0)
            length = cell_size * foodpoint.size * 4
            top_left_x = foodpoint.x - length / 2
            top_left_y = foodpoint.y - length / 2
            rectangle = pygame.Rect(top_left_y, top_left_x, length, length)
            pygame.draw.rect(screen, colour, rectangle)
            pygame.draw.circle(screen, (0, 0, 0), (int(foodpoint.y), int(foodpoint.x)), 3)

        # Update the fishes, if the fish runs out of hunger, it is removed
        for fish in fishes:
            fish.update()
            if fish.Hunger <= 0:
                grid.wipeFish(fish)
                fishes.remove(fish)
                print("Fish Starved")
                Fish_starved += 1
                generation = ((Time - fish.age // 60) // 2700)
                y.append((generation, fish.age // 60))
            pygame.draw.polygon(screen, fish.colour, fish.draw_shape())

        # Update the predator, returns the fish it has eaten, or none if it did not eat in that frame
        Eaten_fish = predator.update()
        if isinstance(Eaten_fish, FishBoid):
            if any(fish == Eaten_fish for fish in fishes):
                fishes.remove(Eaten_fish)
                print("Fish Eaten")
                Fish_eaten += 1
                generation = ((Time - Eaten_fish.age) // 2700)
                y.append((generation, Eaten_fish.age // 60))
        pygame.draw.polygon(screen, (108, 119, 128), predator.draw_shape())
        pygame.draw.polygon(screen, (0, 0, 0), predator.draw_shape(),width=1)

        # Visually show stats about the state of the simulation
        ft_font = freetype.Font(None, 25)
        ft_font.render_to(screen, (10, 10), 'Number of Fish: ' + str(len(fishes)), (250, 250, 250))
        ft_font.render_to(screen, (10, 60), 'Number of Fish Eaten: ' + str(Fish_eaten), (250, 250, 250))
        ft_font.render_to(screen, (10, 110), 'Number of Fish Starved: ' + str(Fish_starved), (250, 250, 250))

        # Finds the youngest and fish that has lived the longest
        if fishes:
            # This checks whether the current oldest fish is older than the previous eldest fish
            oldest_fish = fishes[0] if oldest_fish is None or fishes[0].age > oldest_fish.age else oldest_fish
            youngest_fish = fishes[-1]
            genes = [str(np.round(oldest_fish.S_co, 2)),
                     str(np.round(oldest_fish.A_co, 2)),
                     str(np.round(oldest_fish.C_co, 2)),
                     str(np.round(oldest_fish.f_strength, 2)),
                     str(np.round(oldest_fish.p_strength, 2)),
                     str(np.round(oldest_fish.Hungry_co, 2))]

        ft_font.render_to(screen, (10, 180), 'Oldest fish\'s genes: ' + str(genes), (250, 250, 250))
        ft_font.render_to(screen, (10, 220), 'Oldest fish\'s age: ' + str(oldest_fish.age // 60), (250, 250, 250))
        ft_font.render_to(screen, (10, 260), 'Oldest fish\'s generation: ~' + str((Time - oldest_fish.age) // 2700),
                          (250, 250, 250))
        ft_font.render_to(screen, (10, 300), 'Youngest fish\'s generation: ~' + str((Time - youngest_fish.age) // 2700),
                          (250, 250, 250))

        # All current juveniles have their isJuvenile field set to false, as they may not be juveniles in the next frame
        for juvenile in juveniles:
            juvenile.isJuvenile = False

        # Time is every 60 ticks, so if the game is run at 60 ticks per second, it should represents seconds
        # Please note that as more fish spawn, the game lags and time will not go up as smoothly
        ft_font.render_to(screen, (10, 340), 'Time: ' + str(Time // 60), (250, 250, 250))

        pygame.display.update()

        clock.tick(60)

    # Creates a new file containing the important statistics if the simulation, the file will be created at the directory
    # of main.py and will have the name of the corresponding simulation, along with the time it ended
    now = datetime.now()
    with open(str(sim_name + " " + now.strftime("%H.%M.%S") + ".txt"), "a") as file:
        file.write(str(sim_name + " statistics: "))
        file.write(str("\nFish Eaten: " + str(Fish_eaten)))
        file.write(str("\nFish Starved: " + str(Fish_starved)))
        file.write(str("\nTotal Fish: " + str((Fish_eaten + Fish_starved))))
        file.write(str("\nBest Genotype: " + str(genes)))
        file.write(str("\nThis simulation ended at: " + str(now)))
        file.write(str("\n\nWas there evolution and learning?: " + str(evo_and_learn)))
        file.write(str("\nWas there stochasticity added?: " + str(stochastic)))

    # Find average age for each generation
    print(y)
    final_y = pd.DataFrame(y)
    print(final_y)
    final_y = final_y.groupby([0]).mean()
    print(final_y)

    # Plot data on a line graph
    plt.plot(final_y)
    plt.show()

    pygame.quit()


def fish_change_val(*args):
    num = int(num_boids_var.get())
    fish_value_label['text'] = "Value: " + str(num)
def cell_change_val(*args):
    num = int(cell_var.get())

    cell_value_label['text'] = "Value: " + str(num)

def sim_change_val(*args):
    num = int(sim_num_var.get())
    sim_value_label['text'] = "Value: " + str(num)

def start_sim(*args):

    number_of_boids = int(num_boids_var.get())

    cell_size = int(cell_var.get())

    screen_width = int(screen_width_entry.get()) if screen_width_entry.get().isnumeric() else 1260
    screen_height = int(screen_height_entry.get()) if screen_height_entry.get().isnumeric() else 700
    screen_size = (screen_width,screen_height)

    foodpoint_locations = [(screen_size[0] // 6, screen_size[1] // 6), (screen_size[0] // 6, screen_size[1] * 5 // 6),
                           (screen_size[0] * 5 // 6, screen_size[1] // 6),
                           (screen_size[0] * 5 // 6, screen_size[1] * 5 // 6),
                           (screen_size[0] // 2, screen_size[1] // 2)]

    evolve_and_learn = True if evol_val.get() == "Yes" else False
    stochasticity =  True if stoch_val.get() == "Yes" else False

    num_simulations = int(sim_num_var.get())
    root.destroy()
    for i in range(num_simulations):
        Process(target=simulate,
                args=[str("Simulation_" + str(i)), screen_size, cell_size, number_of_boids, foodpoint_locations, evolve_and_learn,
                      stochasticity]).start()

if __name__ == '__main__':
    # Change the following values to affect the simulation, the variable names indicate their function

    # Simple GUI to enter values #
    root = tk.Tk()
    s=ttk.Style()
    s.theme_use('xpnative')

    root.title("Set the Parameters for the simulation")
    root.geometry('500x500')
    root.columnconfigure(0, weight=2)
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=1)

    #Adding frames to window
    top_frame = ttk.Frame(root)
    bottom_frame = ttk.Frame(root)
    button_frame = ttk.Frame(root)
    top_frame.pack(side="top")
    bottom_frame.pack(side="top",expand=1)
    button_frame.pack(side="top",expand=1)

    #Adding introductory text
    ttk.Label(top_frame,text="Please fill in the variables below, \nyou can also just click enter to \nuse the default values",
              font=tkFont.Font(family="Helvetica",size=15),justify="center").pack()

    #Used to see current value of slider
    num_boids_var = tk.IntVar()
    num_boids_var.set(50)
    num_boids_var.trace_add("write",fish_change_val)

    #Create a slider to choose number of starting Boids
    ttk.Label(bottom_frame, text="Number of starting fish/Boids:").grid(column=0, row=0, sticky=tk.W)
    number_of_boids_slider = ttk.Scale(bottom_frame, from_=1, to=100, variable=num_boids_var)
    fish_value_label = ttk.Label(bottom_frame, text="Value: 50")
    number_of_boids_slider.grid(column=1, row=0, sticky=tk.W)
    fish_value_label.grid(column=2, row=0, sticky=tk.W)


    cell_var = tk.IntVar()
    cell_var.set(15)
    cell_var.trace_add("write",cell_change_val)

    #Create a slider to choose cell size
    ttk.Label(bottom_frame, text="Size of grid cells in pixels: ").grid(column=0, row=1, sticky=tk.W)
    cell_size_slider = ttk.Scale(bottom_frame, from_=5, to=30,variable=cell_var)
    cell_size_slider.grid(column=1, row=1, sticky=tk.W)
    cell_value_label = ttk.Label(bottom_frame,text="Value: 15")
    cell_value_label.grid(column=2,row=1,sticky=tk.W)

    #Text box to choose screen width
    ttk.Label(bottom_frame, text="Screen Width (leave blank for default): ").grid(column=0,row=2,sticky=tk.W)
    screen_width_entry = ttk.Entry(bottom_frame,width=10)
    screen_width_entry.grid(column=1,row=2,sticky=tk.W)

    # Text box to choose screen height
    ttk.Label(bottom_frame, text="Screen Height (leave blank for default): ").grid(column=0, row=3, sticky=tk.W)
    screen_height_entry = ttk.Entry(bottom_frame, width=10)
    screen_height_entry.grid(column=1, row=3, sticky=tk.W)

    #Option menu for including evolution
    ttk.Label(bottom_frame, text="Use Evolution?: ").grid(column=0,row=4,sticky=tk.W)
    evol_val = tk.StringVar()
    evol_val.set("Yes")
    evol_option = tk.OptionMenu(bottom_frame,evol_val,"Yes","No")
    evol_option.grid(column=1,row=4,sticky=tk.W)

    # Option menu for including stochasticity
    ttk.Label(bottom_frame, text="Use Stochasticity? (causes janky movement): ").grid(column=0, row=5, sticky=tk.W)
    stoch_val = tk.StringVar()
    stoch_val.set("No")
    stoch_option = tk.OptionMenu(bottom_frame, stoch_val, "Yes", "No")
    stoch_option.grid(column=1, row=5, sticky=tk.W)

    ttk.Label(bottom_frame,text="Number of Simulations: ").grid(column=0,row=6,sticky=tk.W)

    sim_num_var = tk.IntVar()
    sim_num_var.set(1)
    sim_num_var.trace_add("write",sim_change_val)

    sim_num_slider = ttk.Scale(bottom_frame,from_=1,to=4,variable=sim_num_var)
    sim_num_slider.grid(column=1,row=6,sticky=tk.W)
    sim_value_label = ttk.Label(bottom_frame,text="Value: 1")
    sim_value_label.grid(column=2,row=6,sticky=tk.W)

    ttk.Button(button_frame,text="Start Simulation",command=start_sim).grid()


    root.mainloop()

