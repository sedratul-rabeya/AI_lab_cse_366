# agent.py
import pygame
from collections import deque
import heapq

class Agent(pygame.sprite.Sprite):
    def __init__(self, environment, grid_size, algorithm="ucs"):
        super().__init__()
        self.image = pygame.Surface((grid_size, grid_size))
        self.image.fill((0, 0, 255))  # Agent color is blue
        self.rect = self.image.get_rect()
        self.grid_size = grid_size
        self.environment = environment
        self.position = [0, 0]  # Starting at the top-left corner of the grid
        self.rect.topleft = (0, 0)
        self.task_completed = 0
        self.completed_tasks = []
        self.path = []  # List of positions to follow
        self.moving = False  # Flag to indicate if the agent is moving
        self.algorithm = algorithm  # 'ucs' or 'astar'
        self.total_path_cost = 0

    def move(self):
        """Move the agent along the path."""
        if self.path:
            next_position = self.path.pop(0)
            self.position = list(next_position)
            self.rect.topleft = (self.position[0] * self.grid_size, self.position[1] * self.grid_size)
            self.check_task_completion()
            # Add movement cost (1 unit per move)
            self.total_path_cost += 1
        else:
            self.moving = False

    def manhattan_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def find_nearest_task(self):
        """Find the nearest task using the selected algorithm."""
        if not self.environment.task_locations:
            return

        if self.algorithm == "ucs":
            self.find_nearest_task_ucs()
        else:  # A* algorithm
            self.find_nearest_task_astar()

    def find_nearest_task_ucs(self):
        """Find nearest task using Uniform Cost Search."""
        start = tuple(self.position)
        # Priority queue stores: (cost, position, path)
        pq = [(0, start, [start])]
        visited = set()

        while pq:
            cost, current, path = heapq.heappop(pq)
            
            if current in visited:
                continue
                
            visited.add(current)

            # Check if current position is a task location
            if current in self.environment.task_locations:
                self.path = path[1:]  # Exclude the current position
                self.moving = True
                return

            # Explore neighbors
            for next_pos in self.get_neighbors(*current):
                if next_pos not in visited:
                    new_path = list(path)
                    new_path.append(next_pos)
                    # Cost is uniform (1) for each step
                    heapq.heappush(pq, (cost + 1, next_pos, new_path))

    def find_nearest_task_astar(self):
        """Find nearest task using A* Search."""
        start = tuple(self.position)
        # For each task, find path using A*
        best_path = None
        lowest_cost = float('inf')

        for task_pos in self.environment.task_locations:
            # Priority queue stores: (f_score, g_score, position, path)
            pq = [(self.manhattan_distance(start, task_pos), 0, start, [start])]
            visited = set()
            g_scores = {start: 0}  # Cost from start to current position

            while pq:
                f_score, g_score, current, path = heapq.heappop(pq)
                
                if current in visited:
                    continue
                    
                visited.add(current)

                if current == task_pos:
                    if g_score < lowest_cost:
                        lowest_cost = g_score
                        best_path = path
                    break

                for next_pos in self.get_neighbors(*current):
                    if next_pos not in visited:
                        new_g_score = g_score + 1
                        if next_pos not in g_scores or new_g_score < g_scores[next_pos]:
                            g_scores[next_pos] = new_g_score
                            new_path = list(path)
                            new_path.append(next_pos)
                            f_score = new_g_score + self.manhattan_distance(next_pos, task_pos)
                            heapq.heappush(pq, (f_score, new_g_score, next_pos, new_path))

        if best_path:
            self.path = best_path[1:]  # Exclude the current position
            self.moving = True

    def check_task_completion(self):
        """Check if the agent has reached a task location."""
        position_tuple = tuple(self.position)
        if position_tuple in self.environment.task_locations:
            task_number = self.environment.task_locations.pop(position_tuple)
            self.task_completed += 1
            self.completed_tasks.append(task_number)

    def get_neighbors(self, x, y):
        """Get walkable neighboring positions."""
        neighbors = []
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.environment.is_within_bounds(nx, ny) and not self.environment.is_barrier(nx, ny):
                neighbors.append((nx, ny))
        return neighbors

    def switch_algorithm(self):
        """Switch between UCS and A* algorithms."""
        self.algorithm = "astar" if self.algorithm == "ucs" else "ucs"
        self.total_path_cost = 0  # Reset path cost when switching algorithms