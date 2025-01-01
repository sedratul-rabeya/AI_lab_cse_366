import time
import pygame
import matplotlib.pyplot as plt
from environment import Environment
from agent import GeneticAlgorithm
import numpy as np

class ScheduleOptimizer:
    def __init__(self):
        self.NUM_SLOTS = 8
        self.NUM_STUDENTS = 5
        self.POPULATION_SIZE = 50
        self.MUTATION_RATE = 0.1
        self.NUM_GENERATIONS = 100
        self.DELAY = 1000
        
        self.env = Environment(self.NUM_SLOTS, self.NUM_STUDENTS)
        self.ga = GeneticAlgorithm(self.POPULATION_SIZE, self.MUTATION_RATE)
        
        # Logging setup
        self.fitness_history = []
        self.best_schedule = None
        self.best_fitness = 0.0

    def optimize(self):
        """Main optimization loop with enhanced features"""
        try:
            # Initialize population
            population = [self.env.generate_random_schedule() 
                         for _ in range(self.POPULATION_SIZE)]
            
            generation = 0
            running = True
            
            while running and generation < self.NUM_GENERATIONS:
                # Handle Pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                
                try:
                    # Dynamic mutation rate adjustment
                    self.ga.mutation_rate = max(0.01, 
                        self.MUTATION_RATE * (1 - generation/self.NUM_GENERATIONS))
                    
                    # Evaluate population
                    fitness_scores = []
                    for schedule in population:
                        fitness = self.ga.calculate_fitness(
                            schedule, 
                            self.env.student_preferences,
                            self.env.student_availability
                        )
                        fitness_scores.append(fitness)
                    
                    # Update best schedule
                    best_idx = np.argmax(fitness_scores)
                    current_best_fitness = fitness_scores[best_idx]
                    
                    if current_best_fitness > self.best_fitness:
                        self.best_fitness = current_best_fitness
                        self.best_schedule = population[best_idx]
                    
                    # Log fitness
                    self.fitness_history.append(current_best_fitness)
                    
                    # Visualize current best schedule
                    self.env.visualize_schedule(
                        population[best_idx],
                        generation,
                        current_best_fitness,
                        self.best_fitness
                    )
                    
                    # Create new generation
                    new_population = self.ga.evolve_population(
                        population,
                        fitness_scores,
                        self.env.classes
                    )
                    
                    population = new_population
                    generation += 1
                    
                    time.sleep(self.DELAY / 1000)
                    
                except Exception as e:
                    print(f"Error during generation {generation}: {str(e)}")
                    continue
                    
        except KeyboardInterrupt:
            print("\nOptimization interrupted by user")
        except Exception as e:
            print(f"Fatal error: {str(e)}")
        finally:
            self.plot_fitness_history()
            self.env.cleanup()

    def plot_fitness_history(self):
        """Plot fitness history"""
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(self.fitness_history)
            plt.title('Fitness History')
            plt.xlabel('Generation')
            plt.ylabel('Fitness')
            plt.grid(True)
            plt.savefig('fitness_history.png')
            plt.close()
        except Exception as e:
            print(f"Error plotting fitness history: {str(e)}")

if __name__ == "__main__":
    optimizer = ScheduleOptimizer()
    optimizer.optimize()