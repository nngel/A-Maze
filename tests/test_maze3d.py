#!/usr/bin/env python3
"""
Test script for the 3D A* maze visualization.

This script provides tests and manual verification steps to ensure:
1. The 3D scene loads correctly
2. Models are rendered properly
3. The Python A* logic still works with the new frontend
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from typing import Tuple, List, Optional

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from maze_generator import MazeGenerator
from astar import AStar
import maze3d

# Import Panda3D modules
try:
    from direct.showbase.ShowBase import ShowBase
    from panda3d.core import NodePath, PandaNode
    PANDA3D_AVAILABLE = True
except ImportError:
    PANDA3D_AVAILABLE = False


class MockShowBase:
    """Mock class for ShowBase to avoid opening windows during tests."""
    
    def __init__(self):
        self.render = MagicMock()
        self.loader = MagicMock()
        self.taskMgr = MagicMock()
        self.camera = MagicMock()
        self.win = MagicMock()
        self.accept = MagicMock()
        self.disableMouse = MagicMock()


@unittest.skipIf(not PANDA3D_AVAILABLE, "Panda3D is not available")
class TestMaze3D(unittest.TestCase):
    """Test the 3D maze visualization."""

    def setUp(self):
        """Set up the test environment."""
        # Create a small maze for testing
        self.width, self.height = 5, 5
        self.seed = 42  # Fixed seed for reproducible tests
        
        # Mock ShowBase class to avoid opening windows
        self.patcher = patch('maze3d.ShowBase', MockShowBase)
        self.mock_showbase = self.patcher.start()
        
    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()
    
    def test_maze_generation(self):
        """Test that the maze is generated correctly."""
        # Create the 3D maze
        m3d = maze3d.Maze3D(self.width, self.height, self.seed)
        
        # Test that maze dimensions are correct
        self.assertEqual(m3d.width, self.width)
        self.assertEqual(m3d.height, self.height)
        
        # Test that walls were generated
        self.assertGreater(len(m3d.walls), 0)
        
        # Test that start and end positions are set
        self.assertEqual(m3d.start_pos, (0, 0))
        self.assertEqual(m3d.end_pos, (self.width - 1, self.height - 1))
    
    def test_path_calculation(self):
        """Test that A* pathfinding still works correctly."""
        # Create the 3D maze
        m3d = maze3d.Maze3D(self.width, self.height, self.seed)
        
        # Verify that a path was found
        self.assertIsNotNone(m3d.path)
        
        # Check that path starts and ends at correct positions
        self.assertEqual(m3d.path[0], m3d.start_pos)
        self.assertEqual(m3d.path[-1], m3d.end_pos)
        
        # Check that path is continuous (no jumps)
        for i in range(len(m3d.path) - 1):
            x1, y1 = m3d.path[i]
            x2, y2 = m3d.path[i + 1]
            manhattan_dist = abs(x1 - x2) + abs(y1 - y2)
            self.assertEqual(manhattan_dist, 1, "Path should only move one cell at a time")
            
        # Check that no walls are crossed
        for i in range(len(m3d.path) - 1):
            wall = tuple(sorted([m3d.path[i], m3d.path[i + 1]]))
            self.assertNotIn(wall, m3d.walls, f"Path crosses wall between {m3d.path[i]} and {m3d.path[i + 1]}")
    
    def test_scene_setup(self):
        """Test that the 3D scene is set up correctly."""
        m3d = maze3d.Maze3D(self.width, self.height, self.seed)
        
        # Check that maze node was created
        self.assertTrue(hasattr(m3d, 'maze_node'))
        
        # Check that walls were created
        self.assertTrue(hasattr(m3d, 'wall_nodes'))
        
        # Check that player and goal were created
        self.assertTrue(hasattr(m3d, 'player'))
        self.assertTrue(hasattr(m3d, 'goal'))
        
        # Check that lights were created
        self.assertTrue(hasattr(m3d, 'plight'))


def manual_verification_checklist():
    """Print a checklist for manual verification."""
    print("\n=== Manual Verification Checklist ===")
    print("Run the following command to start the 3D maze:")
    print("    python maze3d.py --width 10 --height 10")
    print("\nCheck the following:")
    
    print("\n1. Scene Loading:")
    print("  - [ ] The application window opens with a title bar")
    print("  - [ ] A 3D maze is visible with walls, floor, and ceiling")
    print("  - [ ] The maze structure matches what you would expect from the regular visualization")
    
    print("\n2. Model Rendering:")
    print("  - [ ] Walls are visible and have textures")
    print("  - [ ] The floor is visible and has a texture")
    print("  - [ ] The player object (green sphere) is visible at the start position")
    print("  - [ ] The goal object (red sphere) is visible at the end position")
    
    print("\n3. Navigation and Controls:")
    print("  - [ ] WASD keys move the camera around")
    print("  - [ ] Q/E keys rotate the camera")
    print("  - [ ] R key resets the camera position")
    print("  - [ ] ESC key quits the application")
    
    print("\n4. A* Integration:")
    print("  - [ ] P key toggles path display (marked TO DO in the code)")
    print("  - [ ] The player can navigate from start to end following the correct path")
    print("  - [ ] Try generating different mazes with --seed parameter to verify path finding works")
    
    print("\nIf all checks pass, the 3D maze visualization is working correctly!\n")


if __name__ == "__main__":
    # Run automated tests
    unittest.main(exit=False)
    
    # Print manual verification checklist
    manual_verification_checklist()