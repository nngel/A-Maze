#!/usr/bin/env python3
"""
Pygame-based visualization for the A* maze demo.
This module provides an interactive visualization of maze generation and pathfinding using Pygame.
"""

import pygame
import sys
from typing import List, Set, Tuple, Optional, Dict, Any
import time
from maze_generator import MazeGenerator
from astar import AStar

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
MAGENTA = (255, 0, 255)  # New color for explored nodes
LIGHT_BLUE = (173, 216, 230)
GRAY = (200, 200, 200)
DARK_BLUE = (0, 0, 139)
ORANGE = (255, 165, 0)


class PygameMazeVisualizer:
    def __init__(self, width: int, height: int, cell_size: int = 40, margin: int = 50, seed: Optional[int] = None):
        """Initialize the Pygame maze visualizer.
        
        Args:
            width: Width of the maze in cells
            height: Height of the maze in cells
            cell_size: Size of each cell in pixels
            margin: Margin around the maze in pixels
            seed: Optional seed for maze generation
        """
        # Initialize maze parameters
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.margin = margin
        self.seed = seed
        
        # Control panel width on the left side
        self.control_panel_width = 250  # Increased width for control panel
        
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("A* Maze Visualization")
        
        # Calculate screen dimensions with extra width for controls
        self.screen_width = self.control_panel_width + width * cell_size + 2 * margin
        self.screen_height = height * cell_size + 2 * margin
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Set up font
        self.font = pygame.font.SysFont('Arial', 16)
        
        # Initialize maze components
        self.maze_generator = MazeGenerator(width, height, seed=self.seed)
        self.walls = self.maze_generator.generate()
        self.astar = AStar(width, height, self.walls)
        
        # Set initial start and end positions
        self.start_pos = (0, 0)
        self.end_pos = (width - 1, height - 1)
        
        # Initialize path and explored nodes
        self.path = None
        self.explored_nodes = set()
        
        # Animation parameters
        self.animation_speed = 30  # ms per frame
        self.show_exploration = True
        self.animation_in_progress = False
        
        # User interaction state
        self.selecting_start = False
        self.selecting_end = False
        
        # Seed input variables
        self.entering_seed = False
        self.seed_input = "" if self.seed is None else str(self.seed)
        self.seed_cursor_visible = True
        self.cursor_blink_time = 0
        
        # Find the initial path
        self.path = self.astar.find_path(self.start_pos, self.end_pos)
        self.explored_nodes = self.astar.get_explored_nodes()
        
    def cell_to_pixel(self, cell: Tuple[int, int]) -> Tuple[int, int]:
        """Convert cell coordinates to pixel coordinates."""
        x, y = cell
        # Offset x by the control panel width
        pixel_x = self.control_panel_width + x * self.cell_size + self.margin
        pixel_y = y * self.cell_size + self.margin
        return (pixel_x, pixel_y)
    
    def pixel_to_cell(self, pixel: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert pixel coordinates to cell coordinates."""
        x, y = pixel
        
        # Adjust for control panel
        maze_x = x - self.control_panel_width
        
        # Check if the pixel is in the maze area
        if (self.control_panel_width + self.margin <= x < self.screen_width - self.margin and
            self.margin <= y < self.screen_height - self.margin):
            cell_x = (maze_x - self.margin) // self.cell_size
            cell_y = (y - self.margin) // self.cell_size
            
            # Validate cell coordinates
            if 0 <= cell_x < self.width and 0 <= cell_y < self.height:
                return (cell_x, cell_y)
        
        return None
    
    def draw_path(self):
        """Draw the path correctly following passages between cells."""
        if not self.path:
            return
        
        # Draw path cells (except start/end)
        for i in range(1, len(self.path) - 1):
            cell = self.path[i]
            pixel_x, pixel_y = self.cell_to_pixel(cell)
            
            # Fill the cell with yellow
            pygame.draw.rect(self.screen, YELLOW,
                          (pixel_x + 5, pixel_y + 5, self.cell_size - 10, self.cell_size - 10))
    
    def draw_maze(self):
        """Draw the maze with walls, cells, and path."""
        # Fill the background
        self.screen.fill(WHITE)
        
        # Draw control panel background
        pygame.draw.rect(self.screen, LIGHT_BLUE, 
                        (0, 0, self.control_panel_width, self.screen_height))
        
        # Draw the maze grid - all white cells
        maze_width = self.width * self.cell_size
        maze_height = self.height * self.cell_size
        maze_rect = pygame.Rect(
            self.control_panel_width + self.margin, 
            self.margin, 
            maze_width, 
            maze_height
        )
        pygame.draw.rect(self.screen, WHITE, maze_rect)
        
        # Draw explored nodes if enabled - draw ALL explored nodes (including those under the path)
        if self.show_exploration:
            for cell in self.explored_nodes:
                pixel_x, pixel_y = self.cell_to_pixel(cell)
                pygame.draw.rect(self.screen, MAGENTA,
                               (pixel_x + 3, pixel_y + 3, 
                                self.cell_size - 6, self.cell_size - 6))
        
        # Draw the path on top of explored nodes
        if self.path:
            self.draw_path()
        
        # Draw start and end points (always on top)
        start_pixel_x, start_pixel_y = self.cell_to_pixel(self.start_pos)
        end_pixel_x, end_pixel_y = self.cell_to_pixel(self.end_pos)
        
        pygame.draw.rect(self.screen, GREEN,
                        (start_pixel_x + 5, start_pixel_y + 5, 
                         self.cell_size - 10, self.cell_size - 10))
        pygame.draw.rect(self.screen, RED,
                        (end_pixel_x + 5, end_pixel_y + 5, 
                         self.cell_size - 10, self.cell_size - 10))
        
        # WALL DRAWING APPROACH - draw a complete grid, then erase walls where there are passages
        wall_thickness = 3
        
        # First, draw the grid lines to represent all potential walls
        for x in range(self.width + 1):
            # Draw vertical grid lines
            start_x = self.control_panel_width + self.margin + x * self.cell_size
            start_y = self.margin
            end_y = self.margin + self.height * self.cell_size
            pygame.draw.line(self.screen, BLACK, (start_x, start_y), (start_x, end_y), wall_thickness)
        
        for y in range(self.height + 1):
            # Draw horizontal grid lines
            start_x = self.control_panel_width + self.margin
            start_y = self.margin + y * self.cell_size
            end_x = self.control_panel_width + self.margin + self.width * self.cell_size
            pygame.draw.line(self.screen, BLACK, (start_x, start_y), (end_x, start_y), wall_thickness)
        
        # Now remove walls where there's a passage (not in self.walls)
        for x in range(self.width):
            for y in range(self.height):
                # Check right passage
                if x < self.width - 1:
                    wall = tuple(sorted([(x, y), (x + 1, y)]))
                    if wall not in self.walls:
                        # Draw a white line to "erase" the wall
                        start_x = self.control_panel_width + self.margin + (x + 1) * self.cell_size
                        start_y = self.margin + y * self.cell_size + 2
                        end_y = self.margin + (y + 1) * self.cell_size - 2
                        pygame.draw.line(self.screen, WHITE, (start_x, start_y), (start_x, end_y), wall_thickness + 2)
                
                # Check bottom passage
                if y < self.height - 1:
                    wall = tuple(sorted([(x, y), (x, y + 1)]))
                    if wall not in self.walls:
                        # Draw a white line to "erase" the wall
                        start_x = self.control_panel_width + self.margin + x * self.cell_size + 2
                        start_y = self.margin + (y + 1) * self.cell_size
                        end_x = self.control_panel_width + self.margin + (x + 1) * self.cell_size - 2
                        pygame.draw.line(self.screen, WHITE, (start_x, start_y), (end_x, start_y), wall_thickness + 2)
        
        # Draw controls information on the left panel with better spacing and organization
        title_font = pygame.font.SysFont('Arial', 20, bold=True)
        title = title_font.render("A* Maze Visualization", True, BLACK)
        self.screen.blit(title, (20, 15))
        
        controls = [
            ("Controls:", True),  # Section header
            ("R: Regenerate maze", False),
            ("S: Set start position (click)", False),
            ("E: Set end position (click)", False),
            ("A: Toggle animation", False),
            ("Space: Find path", False),
            ("D: Set seed for debugging", False),
            ("Q: Quit", False)
        ]
        
        # If seed input is active, we need a different layout to prevent overlapping
        if self.entering_seed:
            # Simplified control panel when entering seed to avoid overlaps
            max_y_pos = 50
            for i, (text, is_header) in enumerate(controls[:4]):  # Draw only first 4 controls
                if is_header:
                    font = pygame.font.SysFont('Arial', 18, bold=True)
                    max_y_pos += 10
                else:
                    font = self.font
                    
                text_surface = font.render(text, True, BLACK)
                self.screen.blit(text_surface, (20, max_y_pos))
                max_y_pos += 25
            
            # Draw a semi-transparent overlay for the seed input area
            seed_input_rect = pygame.Rect(10, max_y_pos, self.control_panel_width - 20, 150)
            overlay = pygame.Surface((seed_input_rect.width, seed_input_rect.height), pygame.SRCALPHA)
            overlay.fill((200, 225, 255, 240))  # Light blue with some transparency
            self.screen.blit(overlay, seed_input_rect)
            
            # Draw border around seed input area
            pygame.draw.rect(self.screen, BLACK, seed_input_rect, 2)
            
            # Draw the seed input header
            seed_header = pygame.font.SysFont('Arial', 18, bold=True).render("Enter Seed Value:", True, BLACK)
            self.screen.blit(seed_header, (20, max_y_pos + 15))
            
            # Draw instructions
            instructions = [
                "Type a number to set a specific seed",
                "Press Enter to confirm",
                "Press Esc to cancel"
            ]
            
            for i, text in enumerate(instructions):
                self.screen.blit(self.font.render(text, True, BLACK), (20, max_y_pos + 45 + i * 20))
            
            # Draw the input field with a white background
            input_y = max_y_pos + 45 + len(instructions) * 20 + 10
            pygame.draw.rect(self.screen, WHITE, (20, input_y, 210, 30))
            pygame.draw.rect(self.screen, BLACK, (20, input_y, 210, 30), 1)
            
            # Show the cursor blinking effect
            if pygame.time.get_ticks() - self.cursor_blink_time > 500:
                self.seed_cursor_visible = not self.seed_cursor_visible
                self.cursor_blink_time = pygame.time.get_ticks()
                
            input_text = self.seed_input
            if self.seed_cursor_visible:
                input_text += "|"
                
            self.screen.blit(self.font.render(input_text, True, BLACK), (25, input_y + 7))
            
            # Continue drawing the remaining controls below the seed input area
            y_pos = max_y_pos + 170
            for i, (text, is_header) in enumerate(controls[4:]):  # Draw remaining controls
                if is_header:
                    font = pygame.font.SysFont('Arial', 18, bold=True)
                    y_pos += 10
                else:
                    font = self.font
                    
                text_surface = font.render(text, True, BLACK)
                self.screen.blit(text_surface, (20, y_pos))
                y_pos += 25
                
        else:
            # Normal control panel when not entering seed
            y_pos = 50
            for text, is_header in controls:
                if is_header:
                    # Headers are bold and have more space above them
                    font = pygame.font.SysFont('Arial', 18, bold=True)
                    y_pos += 10
                else:
                    font = self.font
                    
                text_surface = font.render(text, True, BLACK)
                self.screen.blit(text_surface, (20, y_pos))
                y_pos += 25  # More spacing between controls
            
            # Draw seed information in a cleaner format
            seed_y = y_pos + 20
            seed_header = pygame.font.SysFont('Arial', 18, bold=True).render("Debugging Info:", True, BLACK)
            self.screen.blit(seed_header, (20, seed_y))
            
            seed_text = f"Current Seed: {self.seed if self.seed is not None else 'Random'}"
            self.screen.blit(self.font.render(seed_text, True, BLACK), (20, seed_y + 25))
        
        # Draw legend with clearer separation from other elements - always at the bottom
        legend_y = self.screen_height - 160
        legend_header = pygame.font.SysFont('Arial', 18, bold=True).render("Legend:", True, BLACK)
        self.screen.blit(legend_header, (20, legend_y))
        
        # Draw legend items with more spacing
        legends = [
            (GREEN, "Start position"),
            (RED, "End position"),
            (YELLOW, "Path"),
            (MAGENTA, "Explored nodes")
        ]
        
        for i, (color, text) in enumerate(legends):
            y_offset = legend_y + 30 + i * 25
            pygame.draw.rect(self.screen, color, (20, y_offset, 20, 20))
            self.screen.blit(self.font.render(text, True, BLACK), (50, y_offset + 2))
    
    def update_seed_and_regenerate(self):
        """Update the seed from the input and regenerate the maze."""
        if self.seed_input.strip() == "":
            self.seed = None
        else:
            try:
                self.seed = int(self.seed_input)
            except ValueError:
                # Handle invalid input
                self.seed_input = "" if self.seed is None else str(self.seed)
                return
            
        self.regenerate_maze()
        self.entering_seed = False
    
    def regenerate_maze(self):
        """Regenerate the maze and recalculate the path."""
        self.maze_generator = MazeGenerator(self.width, self.height, seed=self.seed)
        self.walls = self.maze_generator.generate()
        self.astar = AStar(self.width, self.height, self.walls)
        self.path = self.astar.find_path(self.start_pos, self.end_pos)
        self.explored_nodes = self.astar.get_explored_nodes()
    
    def animate_pathfinding(self):
        """Animate the A* pathfinding process."""
        self.animation_in_progress = True
        self.explored_nodes = set()
        
        # Create a new A* instance for animation
        astar = AStar(self.width, self.height, self.walls)
        
        # Get the step by step process of the algorithm
        path = astar.find_path(self.start_pos, self.end_pos)
        self.path = path
        
        # For animation, we'll use the explored nodes from A*
        explored_sequence = list(astar.get_explored_nodes())
        
        # Sort the explored nodes by distance from start (approximate)
        explored_sequence.sort(key=lambda pos: abs(pos[0] - self.start_pos[0]) + abs(pos[1] - self.start_pos[1]))
        
        # Animate the exploration
        self.explored_nodes = set()
        for node in explored_sequence:
            self.explored_nodes.add(node)
            self.draw_maze()
            pygame.display.flip()
            pygame.time.delay(self.animation_speed)
            
            # Check for quit events during animation
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
        
        # Set the final result
        self.explored_nodes = set(explored_sequence)
        self.animation_in_progress = False
    
    def run(self):
        """Run the main visualization loop."""
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if self.entering_seed:
                        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            self.update_seed_and_regenerate()
                        elif event.key == pygame.K_ESCAPE:
                            self.entering_seed = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.seed_input = self.seed_input[:-1]
                        else:
                            # Only allow numbers to be entered
                            if event.unicode.isdigit():
                                self.seed_input += event.unicode
                    else:
                        if event.key == pygame.K_q:
                            running = False
                        elif event.key == pygame.K_r:
                            self.regenerate_maze()
                        elif event.key == pygame.K_s and not self.entering_seed:
                            # Enable start position selection
                            self.selecting_start = True
                            self.selecting_end = False
                        elif event.key == pygame.K_e and not self.entering_seed:
                            # Enable end position selection
                            self.selecting_end = True
                            self.selecting_start = False
                        elif event.key == pygame.K_a:
                            # Toggle showing exploration
                            self.show_exploration = not self.show_exploration
                        elif event.key == pygame.K_d:
                            # Enable seed input
                            self.entering_seed = True
                            self.seed_cursor_visible = True
                            self.cursor_blink_time = pygame.time.get_ticks()
                        elif event.key == pygame.K_SPACE:
                            # Find path immediately or animate
                            if not self.animation_in_progress and not self.entering_seed:
                                self.animate_pathfinding()
                
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.entering_seed:
                    # Get the cell that was clicked
                    mouse_pos = pygame.mouse.get_pos()
                    cell = self.pixel_to_cell(mouse_pos)
                    
                    if cell:
                        if self.selecting_start:
                            self.start_pos = cell
                            self.selecting_start = False
                            # Recalculate path
                            self.path = self.astar.find_path(self.start_pos, self.end_pos)
                            self.explored_nodes = self.astar.get_explored_nodes()
                            
                        elif self.selecting_end:
                            self.end_pos = cell
                            self.selecting_end = False
                            # Recalculate path
                            self.path = self.astar.find_path(self.start_pos, self.end_pos)
                            self.explored_nodes = self.astar.get_explored_nodes()
            
            # Draw the maze and update the display
            self.draw_maze()
            
            # Show selection mode indicator
            if self.selecting_start:
                text = self.font.render("Click to set start position", True, GREEN)
                self.screen.blit(text, (self.control_panel_width + (self.screen_width - self.control_panel_width) // 2 - 100, 10))
            elif self.selecting_end:
                text = self.font.render("Click to set end position", True, RED)
                self.screen.blit(text, (self.control_panel_width + (self.screen_width - self.control_panel_width) // 2 - 100, 10))
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()


def run_pygame_visualizer(width: int, height: int, cell_size: int = 40, seed: Optional[int] = None):
    """Run the Pygame maze visualizer as a standalone application.
    
    Args:
        width: Width of the maze in cells
        height: Height of the maze in cells
        cell_size: Size of each cell in pixels
        seed: Optional seed for random maze generation
    """
    visualizer = PygameMazeVisualizer(width, height, cell_size, seed=seed)
    visualizer.run()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Pygame A* Maze Visualization")
    parser.add_argument("--width", type=int, default=15, help="Maze width (default: 15)")
    parser.add_argument("--height", type=int, default=15, help="Maze height (default: 15)")
    parser.add_argument("--cell-size", type=int, default=40, help="Cell size in pixels (default: 40)")
    parser.add_argument("--seed", type=int, default=None, help="Seed for maze generation (default: random)")
    args = parser.parse_args()
    
    run_pygame_visualizer(args.width, args.height, args.cell_size, args.seed)