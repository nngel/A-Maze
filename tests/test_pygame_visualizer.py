#!/usr/bin/env python3
"""
Tests for the Pygame maze visualizer.

This test suite verifies that:
1. The maze generator and A* pathfinding work correctly with the pygame visualizer
2. The visualizer can run headlessly without crashing
3. The pygame visualization logic functions properly
"""

import unittest
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules to test
from maze_generator import MazeGenerator
from astar import AStar
import pygame

# Try to import the pygame visualizer
try:
    from pygame_visualizer import PygameMazeVisualizer
except ImportError:
    print("Warning: Pygame visualization module could not be imported.")
    PygameMazeVisualizer = None


class TestPygameMazeVisualizer(unittest.TestCase):
    """Test the Pygame maze visualizer."""

    def setUp(self):
        """Set up the test environment with mocked pygame components if needed."""
        # Initialize pygame in headless mode if possible
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        try:
            pygame.init()
        except:
            self.skipTest("Pygame couldn't initialize, skipping tests.")
    
    def tearDown(self):
        """Clean up after the tests."""
        pygame.quit()
    
    def test_maze_generation_and_pathfinding(self):
        """Test that maze generation and pathfinding still work correctly."""
        # Create a small maze for testing
        width, height = 10, 10
        maze_generator = MazeGenerator(width, height)
        walls = maze_generator.generate()
        
        # Check that walls were generated
        self.assertGreater(len(walls), 0, "No walls were generated")
        
        # Use A* to find a path
        astar = AStar(width, height, walls)
        start = (0, 0)
        end = (width - 1, height - 1)
        path = astar.find_path(start, end)
        
        # Verify that a path was found
        self.assertIsNotNone(path, "A* could not find a path")
        self.assertEqual(path[0], start, "Path doesn't start at the correct position")
        self.assertEqual(path[-1], end, "Path doesn't end at the correct position")
    
    @unittest.skipIf(PygameMazeVisualizer is None, "Pygame visualizer module not available")
    def test_visualizer_creation(self):
        """Test that the visualizer can be created without errors."""
        width, height = 10, 10
        try:
            visualizer = PygameMazeVisualizer(width, height)
            self.assertIsNotNone(visualizer, "Visualizer was not created")
        except Exception as e:
            self.fail(f"Visualizer creation raised exception: {e}")
    
    @unittest.skipIf(PygameMazeVisualizer is None, "Pygame visualizer module not available")
    def test_coordinate_conversion(self):
        """Test the cell-to-pixel and pixel-to-cell conversions."""
        width, height = 10, 10
        cell_size = 40
        margin = 50
        
        visualizer = PygameMazeVisualizer(width, height, cell_size, margin)
        
        # Test cell to pixel conversion
        cell = (3, 4)
        pixel = visualizer.cell_to_pixel(cell)
        expected_pixel = (3 * cell_size + margin, 4 * cell_size + margin)
        self.assertEqual(pixel, expected_pixel, "Cell to pixel conversion is incorrect")
        
        # Test pixel to cell conversion
        pixel = (3 * cell_size + margin + 10, 4 * cell_size + margin + 10)  # Inside cell (3, 4)
        cell = visualizer.pixel_to_cell(pixel)
        expected_cell = (3, 4)
        self.assertEqual(cell, expected_cell, "Pixel to cell conversion is incorrect")
        
        # Test pixel to cell conversion for out-of-bounds pixel
        pixel = (margin - 5, margin - 5)  # Outside the maze area
        cell = visualizer.pixel_to_cell(pixel)
        self.assertIsNone(cell, "Out-of-bounds pixel should convert to None")
    
    @unittest.skipIf(PygameMazeVisualizer is None, "Pygame visualizer module not available")
    def test_maze_regeneration(self):
        """Test regenerating the maze."""
        width, height = 10, 10
        
        visualizer = PygameMazeVisualizer(width, height)
        original_walls = set(visualizer.walls)
        
        # Regenerate the maze
        visualizer.regenerate_maze()
        new_walls = set(visualizer.walls)
        
        # Due to randomness, there's a small chance the mazes could be identical
        # For a 10x10 maze, this is extremely unlikely
        self.assertNotEqual(len(original_walls & new_walls), len(original_walls),
                            "Maze regeneration did not change the maze")
    
    @unittest.skipIf(PygameMazeVisualizer is None, "Pygame visualizer module not available")
    def test_path_calculation(self):
        """Test that path calculation works correctly in the visualizer."""
        width, height = 10, 10
        
        visualizer = PygameMazeVisualizer(width, height)
        
        # Test with default start and end positions
        path = visualizer.path
        self.assertIsNotNone(path, "Path should be calculated")
        self.assertEqual(path[0], (0, 0), "Path should start at (0, 0)")
        self.assertEqual(path[-1], (width-1, height-1), "Path should end at bottom-right")
        
        # Change start and end positions
        visualizer.start_pos = (1, 1)
        visualizer.end_pos = (width-2, height-2)
        
        # Recalculate path
        visualizer.path = visualizer.astar.find_path(visualizer.start_pos, visualizer.end_pos)
        
        # Test the new path
        self.assertIsNotNone(visualizer.path, "Path should be recalculated")
        self.assertEqual(visualizer.path[0], (1, 1), "Path should start at new start position")
        self.assertEqual(visualizer.path[-1], (width-2, height-2), "Path should end at new end position")
    
    @unittest.skipIf(PygameMazeVisualizer is None, "Pygame visualizer module not available")
    def test_draw_maze_headless(self):
        """Test that drawing the maze doesn't crash in headless mode."""
        width, height = 10, 10
        
        visualizer = PygameMazeVisualizer(width, height)
        try:
            visualizer.draw_maze()
            # If we got here without exceptions, the test passes
        except Exception as e:
            self.fail(f"Drawing maze raised exception: {e}")
    
    @unittest.skipIf(PygameMazeVisualizer is None, "Pygame visualizer module not available")
    def test_simulated_user_interaction(self):
        """Simulate user interactions to test the visualizer logic."""
        width, height = 10, 10
        
        visualizer = PygameMazeVisualizer(width, height)
        
        # Simulate selecting start position
        visualizer.selecting_start = True
        cell = (2, 3)
        old_path = visualizer.path
        
        # Mock a click event at this cell
        visualizer.start_pos = cell
        visualizer.selecting_start = False
        visualizer.path = visualizer.astar.find_path(visualizer.start_pos, visualizer.end_pos)
        
        self.assertEqual(visualizer.start_pos, cell, "Start position was not updated")
        self.assertNotEqual(visualizer.path, old_path, "Path was not recalculated")
    
    @unittest.skipIf(PygameMazeVisualizer is None, "Pygame visualizer module not available")
    def test_mock_animation(self):
        """Test animation logic without actually rendering."""
        width, height = 5, 5  # Small maze for faster testing
        
        visualizer = PygameMazeVisualizer(width, height)
        visualizer.animation_speed = 0  # No delay for testing
        
        # Mock pygame.time.delay to avoid actual delays
        original_delay = pygame.time.delay
        pygame.time.delay = lambda _: None
        
        try:
            # Run the animation logic
            original_explored = len(visualizer.explored_nodes)
            visualizer.animate_pathfinding()
            
            # Since we're not actually rendering, just check that the animation
            # logic executed without errors and updated state appropriately
            self.assertGreaterEqual(len(visualizer.explored_nodes), original_explored,
                                   "Animation did not update explored nodes")
        finally:
            # Restore original delay function
            pygame.time.delay = original_delay


if __name__ == '__main__':
    unittest.main()