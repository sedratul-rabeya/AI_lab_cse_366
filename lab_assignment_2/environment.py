import random

class Environment:
    def __init__(self, width, height, grid_size, num_tasks=5, num_barriers=15):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.columns = width // grid_size
        self.rows = height // grid_size
        
        # Dictionary to store task locations and their numbers
        self.task_locations = {}
        # Set to store barrier locations
        self.barrier_locations = set()
        
        self._generate_environment(num_tasks, num_barriers)
    
    def _generate_environment(self, num_tasks, num_barriers):
        """Generate random tasks and barriers."""
        # Generate barriers
        for _ in range(num_barriers):
            while True:
                x = random.randint(0, self.columns - 1)
                y = random.randint(0, self.rows - 1)
                # Don't place barriers at (0,0) or if location already has a barrier
                if (x, y) != (0, 0) and (x, y) not in self.barrier_locations:
                    self.barrier_locations.add((x, y))
                    break
        
        # Generate tasks
        task_number = 1
        for _ in range(num_tasks):
            while True:
                x = random.randint(0, self.columns - 1)
                y = random.randint(0, self.rows - 1)
                # Don't place tasks at (0,0), on barriers, or where other tasks are
                if (x, y) != (0, 0) and (x, y) not in self.barrier_locations and (x, y) not in self.task_locations:
                    self.task_locations[(x, y)] = task_number
                    task_number += 1
                    break
    
    def is_within_bounds(self, x, y):
        """Check if the given coordinates are within the grid bounds."""
        return 0 <= x < self.columns and 0 <= y < self.rows
    
    def is_barrier(self, x, y):
        """Check if the given coordinates contain a barrier."""
        return (x, y) in self.barrier_locations