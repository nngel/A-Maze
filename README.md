# A-Maze: A\* Pathfinding Visualization

A Python-based maze generator and A\* pathfinding algorithm visualization project.

## Features

- Random maze generation using Depth-First Search
- A\* pathfinding algorithm implementation
- Multiple visualization options:
  - Text-based console visualization
  - Matplotlib-based static visualization
  - Interactive Pygame visualization with real-time editing

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/A-Maze.git
cd A-Maze
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the main program:

```bash
python main.py
```

### Command Line Options

- `--width N`: Set maze width (default: 10)
- `--height N`: Set maze height (default: 10)
- `--text`: Use text-based visualization instead of matplotlib
- `--pygame`: Use interactive Pygame visualization
- `--show-explored`: Show explored nodes in visualization
- `--cell-size N`: Set cell size in pixels for Pygame visualization (default: 40)

### Examples

Generate a 15x15 maze with text visualization:

```bash
python main.py --width 15 --height 15 --text
```

Run the interactive Pygame visualization:

```bash
python main.py --pygame
```

### Pygame Controls

- `R`: Regenerate maze
- `S`: Set start position (click on a cell)
- `E`: Set end position (click on a cell)
- `A`: Toggle animation/exploration visualization
- `Space`: Animate pathfinding
- `Q`: Quit

## Testing

Run all tests:

```bash
python -m unittest discover tests
```

Run specific tests:

```bash
python -m tests.test_maze
python -m tests.test_pygame_visualizer
```

## Project Structure

- `astar.py`: A\* pathfinding algorithm implementation
- `maze_generator.py`: Maze generation algorithm
- `visualizer.py`: Text and matplotlib visualization
- `pygame_visualizer.py`: Interactive Pygame visualization
- `main.py`: Main program integrating all components
- `tests/`: Test modules

## License

MIT License
