# run.py
import pygame
import sys
from agent import Agent
from environment import Environment

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
GRID_SIZE = 40
STATUS_WIDTH = 250
BACKGROUND_COLOR = (255, 255, 255)
BARRIER_COLOR = (0, 0, 0)       # Barrier color is black
TASK_COLOR = (255, 0, 0)        # Task color is red
TEXT_COLOR = (0, 0, 0)
BUTTON_COLOR = (0, 200, 0)
BUTTON_HOVER_COLOR = (0, 255, 0)
BUTTON_TEXT_COLOR = (255, 255, 255)
SWITCH_BUTTON_COLOR = (100, 100, 200)
SWITCH_BUTTON_HOVER_COLOR = (150, 150, 255)
MOVEMENT_DELAY = 200  # Milliseconds between movements

def main():
    pygame.init()

    # Set up display with an additional status panel
    screen = pygame.display.set_mode((WINDOW_WIDTH + STATUS_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pathfinding Algorithm Simulation")

    # Clock to control frame rate
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    # Initialize environment and agent
    environment = Environment(WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE, num_tasks=5, num_barriers=15)
    agent = Agent(environment, GRID_SIZE, "ucs")  # Start with UCS
    all_sprites = pygame.sprite.Group()
    all_sprites.add(agent)

    # Start button
    button_width, button_height = 100, 50
    button_x = WINDOW_WIDTH + (STATUS_WIDTH - button_width) // 2
    button_y = WINDOW_HEIGHT // 2 - button_height // 2
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    # Algorithm switch button
    switch_button_width, switch_button_height = 130, 30
    switch_button_x = WINDOW_WIDTH + (STATUS_WIDTH - switch_button_width) // 2
    switch_button_y = button_y + button_height + 20
    switch_button_rect = pygame.Rect(switch_button_x, switch_button_y, switch_button_width, switch_button_height)

    simulation_started = False
    last_move_time = pygame.time.get_ticks()

    # Main loop
    running = True
    while running:
        clock.tick(60)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not simulation_started and button_rect.collidepoint(event.pos):
                    simulation_started = True
                    if environment.task_locations:
                        agent.find_nearest_task()
                elif switch_button_rect.collidepoint(event.pos):
                    agent.switch_algorithm()
                    simulation_started = False
                    # Reset environment and agent
                    environment = Environment(WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE, num_tasks=5, num_barriers=15)
                    agent = Agent(environment, GRID_SIZE, agent.algorithm)
                    all_sprites = pygame.sprite.Group()
                    all_sprites.add(agent)

        screen.fill(BACKGROUND_COLOR)

        # Draw grid and barriers
        for x in range(environment.columns):
            for y in range(environment.rows):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)

        # Draw barriers
        for (bx, by) in environment.barrier_locations:
            barrier_rect = pygame.Rect(bx * GRID_SIZE, by * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, BARRIER_COLOR, barrier_rect)

        # Draw tasks with numbers
        for (tx, ty), task_number in environment.task_locations.items():
            task_rect = pygame.Rect(tx * GRID_SIZE, ty * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, TASK_COLOR, task_rect)
            task_num_surface = font.render(str(task_number), True, (255, 255, 255))
            task_num_rect = task_num_surface.get_rect(center=task_rect.center)
            screen.blit(task_num_surface, task_num_rect)

        # Draw agent
        all_sprites.draw(screen)

        # Display status panel
        status_x = WINDOW_WIDTH + 10
        algorithm_text = f"Algorithm: {'UCS' if agent.algorithm == 'ucs' else 'A*'}"
        task_status_text = f"Tasks Completed: {agent.task_completed}"
        path_cost_text = f"Total Path Cost: {agent.total_path_cost}"
        completed_tasks_text = f"Completed Tasks: {agent.completed_tasks}"

        algorithm_surface = font.render(algorithm_text, True, TEXT_COLOR)
        status_surface = font.render(task_status_text, True, TEXT_COLOR)
        path_cost_surface = font.render(path_cost_text, True, TEXT_COLOR)
        completed_tasks_surface = font.render(completed_tasks_text, True, TEXT_COLOR)

        screen.blit(algorithm_surface, (status_x, 20))
        screen.blit(status_surface, (status_x, 50))
        screen.blit(path_cost_surface, (status_x, 80))
        screen.blit(completed_tasks_surface, (status_x, 110))

        # Draw buttons
        if not simulation_started:
            # Start button
            mouse_pos = pygame.mouse.get_pos()
            button_color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, button_color, button_rect)
            button_text = font.render("Start", True, BUTTON_TEXT_COLOR)
            text_rect = button_text.get_rect(center=button_rect.center)
            screen.blit(button_text, text_rect)

        # Algorithm switch button
        switch_color = SWITCH_BUTTON_HOVER_COLOR if switch_button_rect.collidepoint(pygame.mouse.get_pos()) else SWITCH_BUTTON_COLOR
        pygame.draw.rect(screen, switch_color, switch_button_rect)
        switch_text = font.render("Switch Algorithm", True, BUTTON_TEXT_COLOR)
        switch_text_rect = switch_text.get_rect(center=switch_button_rect.center)
        screen.blit(switch_text, switch_text_rect)

        # Automatic movement with delay
        if simulation_started:
            current_time = pygame.time.get_ticks()
            if current_time - last_move_time > MOVEMENT_DELAY:
                if not agent.moving and environment.task_locations:
                    agent.find_nearest_task()
                elif agent.moving:
                    agent.move()
                last_move_time = current_time

        # Draw the status panel separator
        pygame.draw.line(screen, (0, 0, 0), (WINDOW_WIDTH, 0), (WINDOW_WIDTH, WINDOW_HEIGHT))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()