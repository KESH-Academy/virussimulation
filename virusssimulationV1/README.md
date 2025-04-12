# Virus Spread Simulation

A visual simulation of virus spread in a population, created using Python and Pygame.

## Features

- Visual representation of healthy (blue), infected (red), and dead (black) individuals
- Real-time statistics display
- Pause/Resume simulation with Space key
- Reset simulation with R key
- Configurable parameters (population size, infection radius, etc.)

## Requirements

- Python 3.x
- Pygame
- NumPy

## Installation

1. Make sure you have Python 3.x installed
2. Run `start.bat` - it will automatically install the required packages

## Controls

- Space: Pause/Resume simulation
- R: Reset simulation
- Close window: Exit simulation

## How It Works

- Each dot represents a person
- Blue dots are healthy
- Red dots are infected
- Black dots are dead
- Infected people can spread the virus to healthy people within their infection radius
- After a certain time, infected people either recover (turn blue) or die (turn black)
- Statistics are displayed in the top-left corner

## Parameters

You can modify these parameters in the code:
- Population size
- Infection radius
- Infection chance
- Death chance
- Recovery time
- Movement speed
- Simulation FPS 