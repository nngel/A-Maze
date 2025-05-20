from typing import List, Set, Tuple, Optional
import matplotlib.pyplot as plt
import numpy as np


class MazeVisualizer:
    def __init__(self, width: int, height: int, walls: Set[Tuple[Tuple[int, int], Tuple[int, int]]]):
        """Initialize the maze visualizer."""
        self.width = width
        self.height = height
        self.walls = walls
    
    def print_text_maze(self, path: Optional[List[Tuple[int, int]]] = None, explored: Optional[Set[Tuple[int, int]]] = None):
        """Print the maze in text format with optional path and explored nodes.
        
        Args:
            path: Optional list of coordinates representing the solution path
            explored: Optional set of coordinates representing explored nodes
        """
        # Initialize the maze representation with walls represented
        # Top boundary
        print("+" + "---+" * self.width)
        
        for y in range(self.height):
            # Row for cells and right walls
            row = "|"
            bottom_row = "+"
            
            for x in range(self.width):
                # Determine cell content
                cell = (x, y)
                
                # Handle path visualization
                if path and cell in path:
                    if cell == path[0]:
                        cell_str = " S "  # Start
                    elif cell == path[-1]:
                        cell_str = " E "  # End
                    else:
                        cell_str = " * "  # Path
                # Handle explored cells visualization
                elif explored and cell in explored:
                    cell_str = " · "  # Explored
                else:
                    cell_str = "   "  # Empty
                
                row += cell_str
                
                # Check if there's a wall to the right
                if x < self.width - 1:
                    if ((x, y), (x + 1, y)) in self.walls or ((x + 1, y), (x, y)) in self.walls:
                        row += "|"
                    else:
                        row += " "
                else:
                    row += "|"  # Right boundary
                    
                # Check if there's a wall below
                if y < self.height - 1:
                    if ((x, y), (x, y + 1)) in self.walls or ((x, y + 1), (x, y)) in self.walls:
                        bottom_row += "---+"
                    else:
                        bottom_row += "   +"
                else:
                    bottom_row += "---+"  # Bottom boundary
                    
            print(row)
            print(bottom_row)
    
    def plot_matplotlib_maze(self, path: Optional[List[Tuple[int, int]]] = None, explored: Optional[Set[Tuple[int, int]]] = None):
        """Plot the maze using matplotlib.
        
        Args:
            path: Optional list of coordinates representing the solution path
            explored: Optional set of coordinates representing explored nodes
        """
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Draw the cells
        for y in range(self.height):
            for x in range(self.width):
                # Draw the walls
                for (x1, y1), (x2, y2) in self.walls:
                    plt.plot([x1, x2], [y1, y2], 'k-', linewidth=2)
        
        # Draw explored nodes if provided
        if explored:
            ex, ey = zip(*explored) if explored else ([], [])
            plt.scatter(ex, ey, color='lightblue', s=100, alpha=0.5)
            
        # Draw the path if provided
        if path:
            # Draw start and end points
            plt.scatter([path[0][0]], [path[0][1]], color='green', s=200, marker='o')
            plt.scatter([path[-1][0]], [path[-1][1]], color='red', s=200, marker='o')
            
            # Draw path
            path_x, path_y = zip(*path)
            plt.plot(path_x, path_y, 'b-', linewidth=3)
        
        # Set up the plot
        plt.grid(False)
        plt.xlim(-0.5, self.width - 0.5)
        plt.ylim(self.height - 0.5, -0.5)  # Flip y-axis to match maze coordinates
        plt.title("Maze with A* Path")
        plt.axis('off')
        plt.tight_layout()
        
        plt.show()