# Fish-Simulation-with-Predator-and-Food-Source
This project contains python code to create a simulation involving Boid agents, a predator agent, food points and an arena. The goal of this project is to simulate how fish evolve schooling tactics over time (the sections below go into more detail as to how this is achieved). The predator and food point are used to influence the Boid fishes behaviour in a way that correlated to real fish. This project was submitted as part of my coursework for Acquired Intelligence and Adaptive Behaviour (Year 2 Semester 2).

## How to Run the Simulation
Alongside having Python 3.11, there are a few required libraries that need to be installed before running *main.py*.

Required Libraries:
- tkinter
- numpy
- pandas
- pygame
- matplotlib

Once the required libraries are installed, please run the *main.py* file.

## Using the Simuation
When the file is run, the first window that will open is the Parameter Menu. This is used to change some of the parameters of the simulation e.g. Number of starting fish, screen/arena size etc. Once you have chosen your parameters, press the start simulation button to close the menu and begin the simulation.

It is also possible to run the simulation with the default settings by not changing anything on the menu and simply pressing the start simulation button.

## How the Simulation Works
It is important to first understand how Boid agents typically function. They were initially introduced by Reynolds in the 80s as a way to model schooling animals (primarily birds). The three key components that dictated the agents were three forces: Separation, Cohesion and Alignment. These forces are calculated based on the position and velocity of neighbouring fish. The strength of these forces are determined by three respective coefficients. Typically, each agent in the simulation would have identical coefficient values, leading to all agents behaving identically.

Each agent in this simulation does not share these coefficient values. Instead, each agent has a genotype that define these values (in addition to some other values). These genotypes are then coerced using a Genetic Algorithm and social learning to hopefully reach an optimal solution.

The optimal solution would be an agent that has:
- Natural flocking behaviour
- Does not starve
- Able to avoid the predatr

As mentioned above, a Genetic Algorithm is used. More specifically, a tournament-style GA with sexual reproduction. The Boid parents both pass down their genetic to the offspring, with the goal being the agents who live longer (a sign of good fitness) reproduce more and pass down more of their genetics. Additionally, the youngest 20% of fish will slowly copy the genotype if the eldest 10% of fish are near them. This is meant to simulate social learning, where the young fish watch and copy the actions of older fish.

There is significantly more going on under the hood, such as how the fish detect neighbours and how the fish actually eat and reproduce. To find out more about how everything is implemented, I encourage you to look through the code and read the extensive commenting of each function. Additionally, I have included my report which can give a deeper insight as to why I chose to implement certain aspects of the simulation (including citations for biological plausibility).
