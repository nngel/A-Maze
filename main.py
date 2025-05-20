#!/usr/bin/env python3
"""
A* Search Algorithm Maze Demo

This script demonstrates the A* search algorithm by:
1. Generating a random maze
2. Finding the shortest path from the start to the end point
3. Visualizing the maze and the path found
"""

import argparse
from maze_generator import MazeGenerator
from astar import AStar
from visualizer import MazeVisualizer
from typing import Optional


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="A* Search Algorithm Maze Demo")
    parser.add_argument("--width", type=int, default=10, help="Maze width (default: 10)")
    parser.add_argument("--height", type=int, default=10, help="Maze height (default: 10)")
    parser.add_argument("--text", action="store_true", help="Use text visualization instead of matplotlib")
    parser.add_argument("--pygame", action="store_true", help="Use interactive Pygame visualization")
    parser.add_argument("--show-explored", action="store_true", help="Show explored nodes in visualization")
    parser.add_argument("--cell-size", type=int, default=40, help="Cell size in pixels for Pygame visualization (default: 40)")
    parser.add_argument("--seed", type=int, default=None, help="Seed for maze generation (default: random)")
    args = parser.parse_args()

    if args.pygame:
        # Use the Pygame visualization
        try:
            from pygame_visualizer import run_pygame_visualizer
            print(f"Starting Pygame visualization with a {args.width}x{args.height} maze...")
            if args.seed is not None:
                print(f"Using seed: {args.seed}")
            run_pygame_visualizer(args.width, args.height, args.cell_size, seed=args.seed)
            # The Pygame visualization has its own maze generation and A* implementation
            return
        except ImportError:
            print("Pygame visualization couldn't be loaded. Make sure pygame is installed.")
            print("Falling back to default visualization.")
    
    # Generate a random maze
    print(f"Generating a {args.width}x{args.height} maze...")
    if args.seed is not None:
        print(f"Using seed: {args.seed}")
    maze_generator = MazeGenerator(args.width, args.height, seed=args.seed)
    walls = maze_generator.generate()
    
    # Define start and end points
    start = (0, 0)  # Top-left corner
    end = (args.width - 1, args.height - 1)  # Bottom-right corner
    
    # Find the shortest path using A*
    print(f"Finding the shortest path from {start} to {end}...")
    a_star = AStar(args.width, args.height, walls)
    path = a_star.find_path(start, end)
    
    # Show results
    if path:
        print(f"Path found! Length: {len(path) - 1} steps")
    else:
        print("No path found! This should not happen with our maze generation algorithm.")
        return
    
    # Visualize the maze and path
    visualizer = MazeVisualizer(args.width, args.height, walls)
    
    # Choose visualization method
    if args.text:
        print("\nMaze and solution path:")
        explored = a_star.get_explored_nodes() if args.show_explored else None
        visualizer.print_text_maze(path, explored)
    else:
        print("\nShowing maze and solution path in a matplotlib window...")
        explored = a_star.get_explored_nodes() if args.show_explored else None
        visualizer.plot_matplotlib_maze(path, explored)


if __name__ == "__main__":
    main()