import sys
import os
import unittest

# Add parent directory to the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from maze_generator import MazeGenerator
from astar import AStar


class TestMazeAndAStar(unittest.TestCase):
    def test_maze_solvability(self):
        """Test that generated mazes are always solvable."""
        # Test with different maze sizes
        for width, height in [(5, 5), (10, 10), (15, 15)]:
            with self.subTest(f"Testing {width}x{height} maze"):
                # Generate maze
                maze_generator = MazeGenerator(width, height)
                walls = maze_generator.generate()
                
                # Setup A* algorithm
                a_star = AStar(width, height, walls)
                
                # Check path exists from top-left to bottom-right
                start = (0, 0)
                end = (width - 1, height - 1)
                path = a_star.find_path(start, end)
                
                # Assert path exists
                self.assertIsNotNone(path, f"Generated {width}x{height} maze should be solvable")
                
                # Assert path starts at start and ends at end
                self.assertEqual(path[0], start, "Path should start at the start point")
                self.assertEqual(path[-1], end, "Path should end at the end point")

    def test_astar_finds_shortest_path(self):
        """Test that A* finds the shortest path in a small maze with known solution."""
        # Create a simple maze with a known shortest path
        width, height = 5, 5
        
        # Create a completely empty maze (no walls except boundaries)
        maze_generator = MazeGenerator(width, height)
        maze_generator.walls = set()  # Clear any walls
        
        # Add specific walls to create a simple maze with known solution
        # Force the path to go around an obstacle
        walls = {
            ((0, 1), (1, 1)),
            ((1, 1), (2, 1)),
            ((2, 1), (3, 1)),
            ((3, 1), (3, 2)),
            ((3, 2), (3, 3)),
            ((1, 3), (2, 3)),
            ((2, 3), (3, 3)),
        }
        
        # Setup A* algorithm
        a_star = AStar(width, height, walls)
        
        # Find path
        start = (0, 0)
        end = (4, 4)
        path = a_star.find_path(start, end)
        
        # The shortest path in this maze should be exactly 8 steps long
        # (0,0) -> (1,0) -> (2,0) -> (3,0) -> (4,0) -> (4,1) -> (4,2) -> (4,3) -> (4,4)
        expected_path_length = 9  # 9 points, 8 steps
        
        # Assert path exists and has correct length
        self.assertIsNotNone(path, "A* should find a path in the test maze")
        self.assertEqual(len(path), expected_path_length, 
                         f"Path should have length {expected_path_length} but got {len(path)}")

    def test_path_validity(self):
        """Test that the A* path is valid (no invalid moves or wall crossings)."""
        # Generate a random maze
        width, height = 10, 10
        maze_generator = MazeGenerator(width, height)
        walls = maze_generator.generate()
        
        # Find path
        a_star = AStar(width, height, walls)
        start = (0, 0)
        end = (width - 1, height - 1)
        path = a_star.find_path(start, end)
        
        # Check that path exists
        self.assertIsNotNone(path, "A* should find a path in the maze")
        
        # Check each step in the path
        for i in range(len(path) - 1):
            current_pos = path[i]
            next_pos = path[i + 1]
            
            # Check that moves are valid (only one cell at a time, horizontally or vertically)
            dx = abs(current_pos[0] - next_pos[0])
            dy = abs(current_pos[1] - next_pos[1])
            self.assertTrue(
                (dx == 1 and dy == 0) or (dx == 0 and dy == 1), 
                f"Invalid move from {current_pos} to {next_pos}"
            )
            
            # Check that no walls are crossed
            wall = tuple(sorted([current_pos, next_pos]))
            self.assertNotIn(wall, walls, f"Path crosses wall between {current_pos} and {next_pos}")


if __name__ == "__main__":
    unittest.main()