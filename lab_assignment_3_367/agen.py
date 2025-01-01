from typing import List, Dict, Tuple
import numpy as np

class Student:
    def __init__(self, id: int, availability: List[bool], preference: float):
        """Initialize student with availability and preferences"""
        self.id = id
        self.availability = availability
        self.preference = preference
        self.schedule = [''] * len(availability)

    def assign_class(self, time_slot: int, class_name: str, duration: int) -> bool:
        """
        Assign a class to student's schedule with availability check
        Args:
            time_slot: Starting time slot for the class
            class_name: Name of the class (e.g., 'P1')
            duration: Duration of the class (1 or 2 hours)
        Returns:
            bool: True if assignment successful, False otherwise
        """
        if time_slot + duration > len(self.availability):
            return False
            
        # Check availability and existing assignments
        for i in range(duration):
            if (not self.availability[time_slot + i] or 
                self.schedule[time_slot + i] or 
                time_slot + i >= len(self.availability)):
                return False
                
        # Assign class
        class_string = f"{class_name} {duration}h"
        for i in range(duration):
            self.schedule[time_slot + i] = class_string
            
        return True

    def clear_schedule(self):
        """Clear the student's schedule"""
        self.schedule = [''] * len(self.availability)

    def get_conflicts(self) -> List[int]:
        """Get list of time slots with conflicts"""
        conflicts = []
        for i, slot in enumerate(self.schedule):
            if slot and not self.availability[i]:
                conflicts.append(i)
        return conflicts

class GeneticAlgorithm:
    def __init__(self, population_size: int, mutation_rate: float):
        """Initialize GA with parameters"""
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.best_fitness_history = []
        self.current_generation = 0

    def calculate_fitness(self, schedule: List[List[str]], 
                         student_preferences: Dict[int, float],
                         student_availability: Dict[int, List[bool]]) -> float:
        """
        Calculate fitness score for a schedule
        Args:
            schedule: 2D list of class assignments
            student_preferences: Dict mapping student ID to preference value
            student_availability: Dict mapping student ID to list of available slots
        Returns:
            Fitness score
        """
        if not schedule or not student_preferences or not student_availability:
            return 0.0
            
        fitness = 0.0
        
        for i in range(len(schedule)):
            if i not in student_preferences or i not in student_availability:
                continue
                
            student_pref = student_preferences[i]
            availability = student_availability[i]
            
            # Check conflicts and availability
            for j, slot in enumerate(schedule[i]):
                if slot:
                    # Check availability conflicts
                    if j >= len(availability) or not availability[j]:
                        fitness -= 1.0  # Penalty for unavailable slot
                    
                    # Check preference alignment
                    if j > 0 and schedule[i][j] == schedule[i][j-1]:
                        continue  # Skip second hour of 2-hour class
                    fitness += student_pref  # Reward for preferred slot
            
            # Check class distribution and priority
            class_count = {}
            for j, slot in enumerate(schedule[i]):
                if slot:
                    class_name = slot.split()[0]
                    class_count[class_name] = class_count.get(class_name, 0) + 1
                    
                    # Penalize duplicate classes
                    if class_count[class_name] > 1:
                        fitness -= 2.0
                        
                    # Reward high-priority classes scheduled earlier
                    try:
                        priority = int(class_name[1])  # Get priority from class name (P1-P5)
                        fitness += (5 - priority) * (len(schedule[i]) - j) / len(schedule[i])
                    except (IndexError, ValueError):
                        continue
        
        return max(0.0, fitness)

    def tournament_select(self, population: List[List[List[str]]], 
                         fitness_scores: List[float], 
                         tournament_size: int = 3) -> List[List[str]]:
        """
        Select parent using tournament selection
        Args:
            population: List of schedules
            fitness_scores: List of fitness scores
            tournament_size: Number of candidates in tournament
        Returns:
            Selected parent schedule
        """
        if not population or not fitness_scores:
            return []
            
        tournament_size = min(tournament_size, len(population))
        tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmax(tournament_fitness)]
        return population[winner_idx]

    def crossover(self, parent1: List[List[str]], parent2: List[List[str]], 
                 class_durations: Dict[str, Dict[str, int]]) -> List[List[str]]:
        """
        Perform crossover between two parents
        Args:
            parent1, parent2: Parent schedules
            class_durations: Dict containing class duration information
        Returns:
            Child schedule
        """
        if not parent1 or not parent2 or len(parent1) != len(parent2):
            return parent1
            
        child = []
        crossover_point = np.random.randint(0, len(parent1[0]))
        
        for i in range(len(parent1)):
            row = []
            current_class = None
            remaining_duration = 0
            
            for j in range(len(parent1[0])):
                if remaining_duration > 0:
                    row.append(current_class)
                    remaining_duration -= 1
                    continue
                    
                if j < crossover_point:
                    cell = parent1[i][j]
                else:
                    cell = parent2[i][j]
                    
                row.append(cell)
                
                if cell:
                    try:
                        class_name = cell.split()[0]
                        duration = int(cell.split()[1][0])
                        if duration == 2 and j < len(parent1[0]) - 1:
                            current_class = cell
                            remaining_duration = 1
                    except (IndexError, ValueError):
                        continue
                        
            child.append(row)
            
        return child

    def mutate(self, schedule: List[List[str]]) -> List[List[str]]:
        """
        Perform mutation on a schedule
        Args:
            schedule: Schedule to mutate
        Returns:
            Mutated schedule
        """
        if not schedule:
            return schedule
            
        mutated = [row[:] for row in schedule]
        num_rows = len(schedule)
        num_cols = len(schedule[0])
        
        for i in range(num_rows):
            for j in range(num_cols):
                if np.random.random() < self.mutation_rate:
                    # Find another position to swap with
                    i2 = np.random.randint(0, num_rows)
                    j2 = np.random.randint(0, num_cols)
                    
                    # Skip if trying to modify second hour of 2-hour class
                    if j > 0 and mutated[i][j] == mutated[i][j-1]:
                        continue
                    if j2 > 0 and mutated[i2][j2] == mutated[i2][j2-1]:
                        continue
                    
                    # Check if it's a 2-hour class
                    is_two_hour = False
                    if j + 1 < num_cols and mutated[i][j] == mutated[i][j+1]:
                        is_two_hour = True
                    
                    # Perform swap
                    mutated[i][j], mutated[i2][j2] = mutated[i2][j2], mutated[i][j]
                    
                    # Handle second hour of 2-hour classes
                    if is_two_hour and j + 1 < num_cols and j2 + 1 < num_cols:
                        mutated[i][j+1], mutated[i2][j2+1] = mutated[i2][j2+1], mutated[i][j+1]
        
        return mutated

    def evolve_population(self, population: List[List[List[str]]], 
                         fitness_scores: List[float],
                         class_durations: Dict[str, Dict[str, int]]) -> List[List[List[str]]]:
        """
        Create next generation of schedules
        Args:
            population: Current population
            fitness_scores: List of fitness scores
            class_durations: Dict containing class duration information
        Returns:
            New population
        """
        if not population or not fitness_scores:
            return population
            
        new_population = []
        
        # Elitism - keep best schedule
        best_idx = np.argmax(fitness_scores)
        new_population.append(population[best_idx])
        
        # Create rest of new population
        while len(new_population) < self.population_size:
            # Tournament selection
            parent1 = self.tournament_select(population, fitness_scores)
            parent2 = self.tournament_select(population, fitness_scores)
            
            # Crossover
            child = self.crossover(parent1, parent2, class_durations)
            
            # Mutation
            child = self.mutate(child)
            
            new_population.append(child)
        
        self.current_generation += 1
        return new_population