import random
from typing import List, Tuple, Set


class MazeGenerator:
    def __init__(self, width: int, height: int):
        """Initialize a maze generator with given dimensions."""
        self.width = width
        self.height = height
        # Maze walls represented as a set of wall coordinates
        self.walls = set()
        # Visited cells during maze generation
        self.visited = set()
        
    def generate(self) -> Set[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Generate a random maze using depth-first search with backtracking.
        
        Returns:
            Set of wall tuples. Each wall is represented as a tuple of two cells.
            A wall between (0,0) and (1,0) would be ((0,0), (1,0)).
        """
        # Initialize all walls
        for x in range(self.width):
            for y in range(self.height):
                if x < self.width - 1:
                    self.walls.add(((x, y), (x + 1, y)))
                if y < self.height - 1:
                    self.walls.add(((x, y), (x, y + 1)))
        
        # Start from the top-left corner
        self._carve_paths((0, 0))
        
        return self.walls
    
    def _carve_paths(self, cell: Tuple[int, int]):
        """Carve paths through the maze using recursive DFS."""
        self.visited.add(cell)
        
        # Define possible directions to move (right, down, left, up)
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        random.shuffle(directions)
        
        # Try each direction
        for dx, dy in directions:
            next_cell = (cell[0] + dx, cell[1] + dy)
            
            # Check if the next cell is valid and not visited
            if (0 <= next_cell[0] < self.width and 
                0 <= next_cell[1] < self.height and 
                next_cell not in self.visited):
                
                # Remove the wall between the current and next cell
                wall = tuple(sorted([cell, next_cell]))
                if wall in self.walls:
                    self.walls.remove(wall)
                
                # Continue carving from the next cell
                self._carve_paths(next_cell)
    
    def is_wall_between(self, cell1: Tuple[int, int], cell2: Tuple[int, int]) -> bool:
        """Check if there's a wall between two adjacent cells."""
        if (abs(cell1[0] - cell2[0]) + abs(cell1[1] - cell2[1])) != 1:
            raise ValueError("Cells must be adjacent")
        
        wall = tuple(sorted([cell1, cell2]))
        return wall in self.walls