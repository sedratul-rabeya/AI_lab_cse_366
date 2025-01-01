## Project Structure

### Files

1. **agen.py**
   - Contains the implementation of the `Student` class and the `GeneticAlgorithm` class.
   - Key functionalities:
     - Assigning classes to students while checking availability.
     - Genetic algorithm operations such as fitness calculation, crossover, mutation, and evolution of population.

2. **environment.py**
   - Defines the `Environment` class responsible for managing students, time slots, and scheduling constraints.
   - Key functionalities:
     - Generating random schedules.
     - Visualizing schedules with conflict and priority indicators using Pygame.
     - Calculating conflicts and preference scores.

3. **run.py**
   - Contains the main entry point for running the optimization process.
   - Implements the `ScheduleOptimizer` class for orchestrating the environment and genetic algorithm.
   - Key functionalities:
     - Running the optimization loop for a fixed number of generations.
     - Visualizing the best schedule in each generation.
     - Logging and plotting fitness history.

## Dependencies

- Python 3.8+
- Pygame
- NumPy
- Matplotlib

Install the required libraries using pip:
```bash
pip install pygame numpy matplotlib
```

## Usage

1. Clone this repository and navigate to the project directory.
2. Run the main script:
   ```bash
   python run.py
   ```
3. The program will display the GUI for schedule optimization and start the process. Each generation's best schedule will be visualized, and conflicts and priorities will be highlighted.

### Key Features

- **Random Schedule Generation**: Initializes a population of schedules.
- **Genetic Algorithm**: Optimizes schedules using fitness evaluation, crossover, and mutation.
- **Dynamic Visualization**: Displays schedules and highlights conflicts and priorities in real-time.
- **Fitness History Plot**: Saves a plot of the fitness progression as `fitness_history.png`.

## Configuration

Modify parameters in `run.py` to adjust the optimization process:

- `NUM_SLOTS`: Number of time slots in the schedule.
- `NUM_STUDENTS`: Number of students to schedule.
- `POPULATION_SIZE`: Size of the population for the genetic algorithm.
- `MUTATION_RATE`: Probability of mutation in the genetic algorithm.
- `NUM_GENERATIONS`: Maximum number of generations to evolve.
- `DELAY`: Delay (in milliseconds) between generations for visualization.

## How It Works

1. **Initialize**: Generate random schedules based on student availability and preferences.
2. **Optimize**: Use the genetic algorithm to iteratively improve the schedules.
   - Fitness is calculated based on conflicts and preference alignment.
   - Crossover combines features of parent schedules.
   - Mutation introduces random variations.
3. **Visualize**: Display the current best schedule in each generation and log the fitness.
4. **Results**: The final optimized schedule is displayed, and a fitness history plot is saved.





