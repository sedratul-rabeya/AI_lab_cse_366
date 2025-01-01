import pygame
import numpy as np
from typing import List, Dict, Tuple

class Environment:
    def __init__(self, num_slots: int = 8, num_students: int = 5):
        self.num_slots = num_slots
        self.num_students = num_students
        self.classes = {
            'P1': {'duration': 2, 'priority': 5},
            'P2': {'duration': 1, 'priority': 4},
            'P3': {'duration': 1, 'priority': 3},
            'P4': {'duration': 1, 'priority': 2},
            'P5': {'duration': 2, 'priority': 1}
        }
        
        # Initialize Pygame with improved settings
        pygame.init()
        self.width = 1270
        self.height = 550
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Class Schedule Optimization")
        
        # Enhanced color scheme
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (66, 133, 244)
        self.LIGHT_GRAY = (245, 245, 245)
        self.DARK_GRAY = (108, 117, 125)
        self.HEADER_BG = (52, 73, 94)
        self.CONFLICT_COLOR = (255, 99, 71)  # Red for conflicts
        
        # Initialize student data
        self.student_preferences = {i: round(np.random.uniform(0.5, 1.5), 2) for i in range(num_students)}
        self.student_availability = self._generate_availability()
        
        # Grid properties
        self.grid_width = min(900, self.width - 300)
        self.cell_width = self.grid_width // num_slots
        self.cell_height = 60
        self.grid_start_x = 200
        self.grid_start_y = 100
        
        # Font setup
        self.title_font = pygame.font.SysFont('Arial', 28, bold=True)
        self.header_font = pygame.font.SysFont('Arial', 18, bold=True)
        self.cell_font = pygame.font.SysFont('Arial', 16)
        self.info_font = pygame.font.SysFont('Arial', 18)
        self.preference_font = pygame.font.SysFont('Arial', 16)
        
        # Logging setup
        self.fitness_history = []

    def _generate_availability(self) -> Dict[int, List[bool]]:
        """Generate random availability for each student"""
        availability = {}
        for i in range(self.num_students):
            # Make most time slots available with some random unavailable slots
            avail = [True] * self.num_slots
            unavailable_count = np.random.randint(1, 3)
            unavailable_slots = np.random.choice(self.num_slots, unavailable_count, replace=False)
            for slot in unavailable_slots:
                avail[slot] = False
            availability[i] = avail
        return availability

    def draw_rounded_rect(self, surface, rect, color, radius=10):
        """Draw a rounded rectangle"""
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    def generate_random_schedule(self) -> List[List[str]]:
        """Generate a random initial schedule considering availability"""
        schedule = [['' for _ in range(self.num_slots)] for _ in range(self.num_students)]
        classes_to_assign = list(self.classes.keys()) * 2  # Multiple instances
        
        for i in range(self.num_students):
            j = 0
            while j < self.num_slots and classes_to_assign:
                if self.student_availability[i][j]:  # Check availability
                    class_name = np.random.choice(classes_to_assign)
                    duration = self.classes[class_name]['duration']
                    
                    # Check if there's enough space and slots are available
                    can_assign = True
                    if j + duration > self.num_slots:
                        can_assign = False
                    else:
                        for k in range(duration):
                            if not self.student_availability[i][j + k]:
                                can_assign = False
                                break
                    
                    if can_assign:
                        classes_to_assign.remove(class_name)
                        schedule[i][j] = f"{class_name} {duration}h"
                        if duration == 2 and j + 1 < self.num_slots:
                            schedule[i][j + 1] = schedule[i][j]
                        j += duration
                    else:
                        j += 1
                else:
                    j += 1
                    
        return schedule

    def _count_conflicts(self, schedule: List[List[str]] = None) -> int:
        """Count the number of scheduling conflicts"""
        if schedule is None:
            return 0
            
        conflicts = 0
        for i in range(self.num_students):
            for j in range(self.num_slots):
                if schedule[i][j] and not self.student_availability[i][j]:
                    conflicts += 1
        return conflicts

    def _calculate_preference_score(self, schedule: List[List[str]] = None) -> float:
        """Calculate the preference alignment score"""
        if schedule is None:
            return 0.0
            
        score = 0.0
        for i in range(self.num_students):
            student_pref = self.student_preferences[i]
            for j in range(self.num_slots):
                if schedule[i][j]:
                    score += student_pref
        return score

    def visualize_schedule(self, schedule: List[List[str]], generation: int, 
                          current_fitness: float, max_fitness: float):
        """Visualize the schedule with improved layout"""
        self.screen.fill(self.WHITE)
        
        # Draw title
        title = self.title_font.render("Class Schedule Optimization", True, self.BLACK)
        title_rect = title.get_rect(centerx=self.grid_start_x + self.grid_width//2, y=30)
        self.screen.blit(title, title_rect)
        
        # Draw slot headers
        for i in range(self.num_slots):
            x = self.grid_start_x + i * self.cell_width
            header_rect = pygame.Rect(x, self.grid_start_y - 35, self.cell_width - 4, 30)
            self.draw_rounded_rect(self.screen, header_rect, self.HEADER_BG)
            
            text = self.header_font.render(f"Slot {i+1}", True, self.WHITE)
            text_rect = text.get_rect(center=header_rect.center)
            self.screen.blit(text, text_rect)
        
        # Draw info panel
        info_panel_x = self.grid_start_x + self.grid_width + 20
        info_panel_y = self.grid_start_y
        info_panel = pygame.Rect(info_panel_x, info_panel_y, 200, 100)
        self.draw_rounded_rect(self.screen, info_panel, self.LIGHT_GRAY)
        
        info_texts = [
            f"Generation: {generation}",
            f"Current Fitness: {current_fitness:.1f}",
            f"Best Fitness: {max_fitness:.1f}"
        ]
        
        for i, text in enumerate(info_texts):
            info_surface = self.info_font.render(text, True, self.BLACK)
            self.screen.blit(info_surface, (info_panel_x + 10, info_panel_y + 10 + i * 30))
        
        # Draw grid
        for i in range(self.num_students):
            # Draw preference
            pref_text = self.preference_font.render(
                f"Preference: {self.student_preferences[i]:.2f}",
                True, self.DARK_GRAY
            )
            pref_rect = pref_text.get_rect(
                right=self.grid_start_x - 10,
                centery=self.grid_start_y + i * self.cell_height + self.cell_height//2
            )
            self.screen.blit(pref_text, pref_rect)
            
            # Draw cells
            for j in range(self.num_slots):
                x = self.grid_start_x + j * self.cell_width
                y = self.grid_start_y + i * self.cell_height
                
                cell_rect = pygame.Rect(x, y, self.cell_width - 4, self.cell_height - 4)
                
                # Determine cell color and style
                cell_color = self.LIGHT_GRAY
                text_color = self.BLACK
                
                # Check conflicts and availability
                if schedule[i][j]:
                    if not self.student_availability[i][j]:
                        cell_color = self.CONFLICT_COLOR
                    elif schedule[i][j].startswith(('P1', 'P2')):
                        cell_color = self.BLUE
                        text_color = self.WHITE
                
                # Draw cell with shadow effect
                shadow_rect = cell_rect.copy()
                shadow_rect.topleft = (cell_rect.x + 2, cell_rect.y + 2)
                self.draw_rounded_rect(self.screen, shadow_rect, self.DARK_GRAY)
                self.draw_rounded_rect(self.screen, cell_rect, cell_color)
                
                # Draw cell content
                if schedule[i][j]:
                    text = self.cell_font.render(schedule[i][j], True, text_color)
                    text_rect = text.get_rect(center=cell_rect.center)
                    self.screen.blit(text, text_rect)
        
        # Draw legend
        legend_y = self.grid_start_y + (self.num_students + 0.5) * self.cell_height
        legend_texts = [
            "P1-P5: Class Programs",
            "1h/2h: Duration",
            "Blue: High Priority",
            "Red: indicate conflicts Class Scheduling"

        ]
        
        for i, text in enumerate(legend_texts):
            legend_surface = self.cell_font.render(text, True, self.DARK_GRAY)
            self.screen.blit(legend_surface, (self.grid_start_x, legend_y + i * 25))

        pygame.display.flip()

    def cleanup(self):
        """Cleanup Pygame resources"""
        pygame.quit()