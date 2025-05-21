#!/usr/bin/env python3
"""
3D A* Maze Visualization using Panda3D

This module provides a 3D visualization of the maze generation and pathfinding 
using Panda3D engine.
"""

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame
from panda3d.core import (
    NodePath, PandaNode, TextNode, 
    CollisionTraverser, CollisionNode, CollisionSphere, CollisionHandlerQueue,
    AmbientLight, DirectionalLight, PointLight, 
    LVector3, LPoint3, TransparencyAttrib,
    WindowProperties, Filename, CardMaker
)
import sys
import os
from typing import List, Set, Tuple, Optional, Dict, Any
import random
import math

# Import existing maze and A* code
from maze_generator import MazeGenerator
from astar import AStar


class Maze3D(ShowBase):
    """3D Maze visualization using Panda3D."""
    
    def __init__(self, width: int = 10, height: int = 10, seed: Optional[int] = None):
        """Initialize the 3D maze.
        
        Args:
            width: Width of the maze in cells
            height: Height of the maze in cells
            seed: Optional seed for maze generation
        """
        # Initialize ShowBase
        ShowBase.__init__(self)
        
        # Set window properties
        self.set_window_properties()
        
        # Initialize maze parameters
        self.width = width
        self.height = height
        self.seed = seed
        self.cell_size = 2.0  # Size of each cell in 3D units
        self.wall_height = 1.5  # Height of maze walls
        
        # Set up scene
        self.setup_scene()
        
        # Set up maze traversal
        self.traverser = CollisionTraverser()
        
        # Generate the maze
        self.generate_maze()
        
        # Set up the camera
        self.setup_camera()
        
        # Set up lighting
        self.setup_lighting()
        
        # Set up the player
        self.setup_player()
        
        # Set up the goal
        self.setup_goal()
        
        # Calculate path
        self.path = self.astar.find_path(self.start_pos, self.end_pos)
        self.explored_nodes = self.astar.get_explored_nodes()
        
        # Set up UI elements
        self.setup_ui()
        
        # Set up keyboard handlers
        self.setup_controls()
        
        # Add the update task to the task manager
        self.taskMgr.add(self.update, "update")
        
    def set_window_properties(self):
        """Set the window properties."""
        props = WindowProperties()
        props.setTitle("3D A* Maze")
        props.setSize(1024, 768)
        self.win.requestProperties(props)
        
    def setup_scene(self):
        """Set up the 3D scene."""
        # Create an empty node for the maze
        self.maze_node = self.render.attachNewNode(PandaNode("Maze"))
        
        # Create a floor
        cm = CardMaker("floor")
        cm.setFrame(0, self.width * self.cell_size, 0, self.height * self.cell_size)
        floor = self.maze_node.attachNewNode(cm.generate())
        floor.setP(-90)  # Rotate to be horizontal
        floor.setPos(0, 0, 0)
        floor.setTexture(self.loader.loadTexture("models/floor.jpg"))
        
    def generate_maze(self):
        """Generate the maze and create the 3D representation."""
        # Generate maze using existing code
        self.maze_generator = MazeGenerator(self.width, self.height, seed=self.seed)
        self.walls = self.maze_generator.generate()
        
        # Set start and end positions
        self.start_pos = (0, 0)
        self.end_pos = (self.width - 1, self.height - 1)
        
        # Initialize A* pathfinding
        self.astar = AStar(self.width, self.height, self.walls)
        
        # Create 3D walls from the maze data
        self.create_walls()
        
    def create_walls(self):
        """Create 3D walls from the maze data."""
        # Clean up existing walls if any
        if hasattr(self, 'wall_nodes'):
            self.wall_nodes.removeNode()
            
        # Create a parent node for all walls
        self.wall_nodes = self.maze_node.attachNewNode("WallNodes")
        
        # For all cells, create walls where needed
        for x in range(self.width):
            for y in range(self.height):
                # Create all possible walls for this cell
                self.create_cell_walls(x, y)
                
        # Create boundary walls
        self.create_boundary_walls()
        
    def create_cell_walls(self, x: int, y: int):
        """Create walls for a specific cell."""
        # Check right wall
        if x < self.width - 1:
            wall = tuple(sorted([(x, y), (x + 1, y)]))
            if wall in self.walls:
                self.create_wall(x + 1, y, "vertical")
                
        # Check top wall
        if y < self.height - 1:
            wall = tuple(sorted([(x, y), (x, y + 1)]))
            if wall in self.walls:
                self.create_wall(x, y + 1, "horizontal")
    
    def create_boundary_walls(self):
        """Create the boundary walls around the maze."""
        # Left boundary
        for y in range(self.height):
            self.create_wall(0, y, "vertical")
            
        # Bottom boundary
        for x in range(self.width):
            self.create_wall(x, 0, "horizontal")
            
        # Right boundary (if not opened by the algorithm)
        for y in range(self.height):
            wall = tuple(sorted([(self.width - 1, y), (self.width, y)]))
            if wall not in self.walls:
                self.create_wall(self.width, y, "vertical")
                
        # Top boundary (if not opened by the algorithm)
        for x in range(self.width):
            wall = tuple(sorted([(x, self.height - 1), (x, self.height)]))
            if wall not in self.walls:
                self.create_wall(x, self.height, "horizontal")
    
    def create_wall(self, x: float, y: float, orientation: str):
        """Create a single wall at the specified position."""
        # Create a wall model
        if orientation == "vertical":
            # Vertical wall (along y-axis)
            cm = CardMaker(f"wall-v-{x}-{y}")
            cm.setFrame(0, self.cell_size, 0, self.wall_height)
            wall = self.wall_nodes.attachNewNode(cm.generate())
            wall.setPos(x * self.cell_size, y * self.cell_size, 0)
            wall.setH(90)  # Rotate to be vertical along Y
        else:
            # Horizontal wall (along x-axis)
            cm = CardMaker(f"wall-h-{x}-{y}")
            cm.setFrame(0, self.cell_size, 0, self.wall_height)
            wall = self.wall_nodes.attachNewNode(cm.generate())
            wall.setPos(x * self.cell_size, y * self.cell_size, 0)
            
        # Apply texture
        wall.setTexture(self.loader.loadTexture("models/wall.jpg"))
        wall.setTwoSided(True)  # Show texture on both sides
        
    def setup_camera(self):
        """Set up the camera for the 3D view."""
        # Disable default mouse control
        self.disableMouse()
        
        # Position camera above the maze looking down initially
        camera_height = max(self.width, self.height) * self.cell_size * 0.8
        self.camera.setPos(
            self.width * self.cell_size / 2,
            self.height * self.cell_size / 2,
            camera_height
        )
        self.camera.lookAt(
            self.width * self.cell_size / 2,
            self.height * self.cell_size / 2,
            0
        )
        
        # Store original camera position for reset
        self.original_camera_pos = self.camera.getPos()
        self.original_camera_hpr = self.camera.getHpr()
        
    def setup_lighting(self):
        """Set up lighting for the scene."""
        # Ambient light
        alight = AmbientLight('alight')
        alight.setColor((0.3, 0.3, 0.3, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        # Directional light (like sun)
        dlight = DirectionalLight('dlight')
        dlight.setColor((0.8, 0.8, 0.8, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(0, -60, 0)  # Point light downward
        self.render.setLight(dlnp)
        
        # Point light near player
        self.plight = PointLight('plight')
        self.plight.setColor((0.8, 0.8, 0.6, 1))
        self.plight.setAttenuation((1, 0, 0.5))  # Set light falloff
        self.plnp = self.render.attachNewNode(self.plight)
        self.render.setLight(self.plnp)
        
    def setup_player(self):
        """Set up the player object."""
        # Create a simple sphere for the player
        self.player = self.loader.loadModel("models/misc/sphere")
        self.player.setColor(0, 0.8, 0, 1)  # Green
        self.player.setScale(0.3)
        self.player.setPos(
            self.start_pos[0] * self.cell_size + self.cell_size/2,
            self.start_pos[1] * self.cell_size + self.cell_size/2,
            0.3
        )
        self.player.reparentTo(self.render)
        
        # Update player light position
        self.plnp.setPos(self.player.getPos() + LVector3(0, 0, 1))
        
    def setup_goal(self):
        """Set up the goal object."""
        # Create a simple cube for the goal
        self.goal = self.loader.loadModel("models/misc/sphere")
        self.goal.setColor(0.8, 0, 0, 1)  # Red
        self.goal.setScale(0.3)
        self.goal.setPos(
            self.end_pos[0] * self.cell_size + self.cell_size/2,
            self.end_pos[1] * self.cell_size + self.cell_size/2,
            0.3
        )
        self.goal.reparentTo(self.render)
        
        # Add a point light at the goal
        glight = PointLight('glight')
        glight.setColor((0.8, 0.2, 0.2, 1))
        glight.setAttenuation((1, 0, 1))
        glnp = self.render.attachNewNode(glight)
        glnp.setPos(self.goal.getPos() + LVector3(0, 0, 1))
        self.render.setLight(glnp)
        
    def setup_ui(self):
        """Set up UI elements."""
        # Create minimap background
        minimap_size = 0.3  # 30% of screen size
        self.minimap_frame = DirectFrame(
            frameColor=(0, 0, 0, 0.5),
            frameSize=(-minimap_size, minimap_size, -minimap_size, minimap_size),
            pos=(1-minimap_size, 0, 1-minimap_size)
        )
        
        # Set proper render order for minimap to be on top
        self.minimap_frame.setBin('fixed', 0)
        self.minimap_frame.setDepthTest(False)
        self.minimap_frame.setDepthWrite(False)
        
        # Instructions text
        self.instructions = OnscreenText(
            text="WASD: Move | Q/E: Rotate | Z/X: Zoom In/Out | R: Reset | P: Path | ESC: Quit",
            pos=(-0.95, -0.95),
            scale=0.05,
            align=TextNode.ALeft,
            mayChange=False
        )
        
        # Counter to limit minimap updates (every 15 frames)
        self.minimap_update_counter = 0
        
        # Update minimap
        self.update_minimap()
        
    def update_minimap(self):
        """Update the minimap display."""
        # Remove existing minimap content if any
        if hasattr(self, 'minimap_content') and self.minimap_content is not None:
            self.minimap_content.removeNode()
            
        # Create a parent node for minimap content
        self.minimap_content = self.minimap_frame.attachNewNode("MinimapContent")
        self.minimap_content.setBin('fixed', 1)  # Make sure content renders on top
        self.minimap_content.setDepthTest(False)
        self.minimap_content.setDepthWrite(False)
        
        minimap_size = 0.3  # Same as frame size
        
        # Calculate cell size in minimap
        cell_size_ratio = minimap_size * 2 / max(self.width, self.height)
        
        # Create cells for each maze position
        for x in range(self.width):
            for y in range(self.height):
                # Calculate position in minimap space (-1 to 1)
                pos_x = -minimap_size + (x + 0.5) * cell_size_ratio
                pos_y = -minimap_size + (y + 0.5) * cell_size_ratio
                
                # Create a rectangle for this cell
                cm = CardMaker(f"cell-{x}-{y}")
                cm.setFrame(
                    pos_x - cell_size_ratio * 0.4, 
                    pos_x + cell_size_ratio * 0.4,
                    pos_y - cell_size_ratio * 0.4, 
                    pos_y + cell_size_ratio * 0.4
                )
                cell = self.minimap_content.attachNewNode(cm.generate())
                cell.setBin('fixed', 1)  # Set render order
                
                # Color cells (dark gray for normal, light for path)
                is_in_path = (x, y) in self.path
                cell.setColor(
                    0.7 if is_in_path else 0.3,  # R
                    0.7 if is_in_path else 0.3,  # G
                    0.7 if is_in_path else 0.3,  # B
                    1.0  # A
                )
        
        # Add walls to minimap
        for x in range(self.width):
            for y in range(self.height):
                # Calculate position in minimap space (-1 to 1)
                pos_x = -minimap_size + x * cell_size_ratio
                pos_y = -minimap_size + y * cell_size_ratio
                
                # Check right wall
                if x < self.width - 1:
                    wall = tuple(sorted([(x, y), (x + 1, y)]))
                    if wall in self.walls:
                        # Create vertical wall line
                        cm = CardMaker(f"wall-v-{x}-{y}")
                        wall_x = pos_x + cell_size_ratio
                        cm.setFrame(
                            wall_x - cell_size_ratio * 0.05, 
                            wall_x + cell_size_ratio * 0.05,
                            pos_y, 
                            pos_y + cell_size_ratio
                        )
                        wall = self.minimap_content.attachNewNode(cm.generate())
                        wall.setColor(0.8, 0.4, 0.2, 1)  # Brown wall
                
                # Check top wall
                if y < self.height - 1:
                    wall = tuple(sorted([(x, y), (x, y + 1)]))
                    if wall in self.walls:
                        # Create horizontal wall line
                        cm = CardMaker(f"wall-h-{x}-{y}")
                        wall_y = pos_y + cell_size_ratio
                        cm.setFrame(
                            pos_x, 
                            pos_x + cell_size_ratio,
                            wall_y - cell_size_ratio * 0.05, 
                            wall_y + cell_size_ratio * 0.05
                        )
                        wall = self.minimap_content.attachNewNode(cm.generate())
                        wall.setColor(0.8, 0.4, 0.2, 1)  # Brown wall
        
        # Draw boundary walls
        # Left boundary
        cm = CardMaker("left-boundary")
        cm.setFrame(
            -minimap_size - cell_size_ratio * 0.05, 
            -minimap_size + cell_size_ratio * 0.05,
            -minimap_size, 
            -minimap_size + cell_size_ratio * self.height
        )
        wall = self.minimap_content.attachNewNode(cm.generate())
        wall.setColor(0.8, 0.4, 0.2, 1)  # Brown wall
        
        # Bottom boundary
        cm = CardMaker("bottom-boundary")
        cm.setFrame(
            -minimap_size, 
            -minimap_size + cell_size_ratio * self.width,
            -minimap_size - cell_size_ratio * 0.05, 
            -minimap_size + cell_size_ratio * 0.05
        )
        wall = self.minimap_content.attachNewNode(cm.generate())
        wall.setColor(0.8, 0.4, 0.2, 1)  # Brown wall
        
        # Right boundary
        cm = CardMaker("right-boundary")
        cm.setFrame(
            -minimap_size + cell_size_ratio * self.width - cell_size_ratio * 0.05, 
            -minimap_size + cell_size_ratio * self.width + cell_size_ratio * 0.05,
            -minimap_size, 
            -minimap_size + cell_size_ratio * self.height
        )
        wall = self.minimap_content.attachNewNode(cm.generate())
        wall.setColor(0.8, 0.4, 0.2, 1)  # Brown wall
        
        # Top boundary
        cm = CardMaker("top-boundary")
        cm.setFrame(
            -minimap_size, 
            -minimap_size + cell_size_ratio * self.width,
            -minimap_size + cell_size_ratio * self.height - cell_size_ratio * 0.05, 
            -minimap_size + cell_size_ratio * self.height + cell_size_ratio * 0.05
        )
        wall = self.minimap_content.attachNewNode(cm.generate())
        wall.setColor(0.8, 0.4, 0.2, 1)  # Brown wall
        
        # Add player indicator (green dot)
        player_x = -minimap_size + (self.player.getX() / self.cell_size) * cell_size_ratio
        player_y = -minimap_size + (self.player.getY() / self.cell_size) * cell_size_ratio
        
        cm = CardMaker("player-indicator")
        cm.setFrame(
            player_x - cell_size_ratio * 0.2, 
            player_x + cell_size_ratio * 0.2,
            player_y - cell_size_ratio * 0.2, 
            player_y + cell_size_ratio * 0.2
        )
        player_indicator = self.minimap_content.attachNewNode(cm.generate())
        player_indicator.setColor(0, 1, 0, 1)  # Bright green
        
        # Add goal indicator (red dot)
        goal_x = -minimap_size + (self.goal.getX() / self.cell_size) * cell_size_ratio
        goal_y = -minimap_size + (self.goal.getY() / self.cell_size) * cell_size_ratio
        
        cm = CardMaker("goal-indicator")
        cm.setFrame(
            goal_x - cell_size_ratio * 0.2, 
            goal_x + cell_size_ratio * 0.2,
            goal_y - cell_size_ratio * 0.2, 
            goal_y + cell_size_ratio * 0.2
        )
        goal_indicator = self.minimap_content.attachNewNode(cm.generate())
        goal_indicator.setColor(1, 0, 0, 1)  # Bright red
        
        # Ensure all minimap elements have proper z-ordering
        for np in self.minimap_content.findAllMatches('*'):
            np.setBin('fixed', 1)
            np.setDepthTest(False)
            np.setDepthWrite(False)
            
    def setup_controls(self):
        """Set up keyboard controls."""
        # Movement controls
        self.keyMap = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "rotate-left": False,
            "rotate-right": False,
            "zoom-in": False,
            "zoom-out": False
        }
        
        # Register keyboard handlers
        self.accept("escape", sys.exit)
        self.accept("w", self.set_key, ["forward", True])
        self.accept("a", self.set_key, ["left", True])
        self.accept("s", self.set_key, ["backward", True])
        self.accept("d", self.set_key, ["right", True])
        self.accept("q", self.set_key, ["rotate-left", True])
        self.accept("e", self.set_key, ["rotate-right", True])
        self.accept("z", self.set_key, ["zoom-in", True])
        self.accept("x", self.set_key, ["zoom-out", True])
        self.accept("w-up", self.set_key, ["forward", False])
        self.accept("a-up", self.set_key, ["left", False])
        self.accept("s-up", self.set_key, ["backward", False])
        self.accept("d-up", self.set_key, ["right", False])
        self.accept("q-up", self.set_key, ["rotate-left", False])
        self.accept("e-up", self.set_key, ["rotate-right", False])
        self.accept("z-up", self.set_key, ["zoom-in", False])
        self.accept("x-up", self.set_key, ["zoom-out", False])
        
        # Additional function keys
        self.accept("r", self.reset_camera)
        self.accept("p", self.toggle_path_display)
        
    def set_key(self, key, value):
        """Set the value of a key in the key map."""
        self.keyMap[key] = value
        
    def reset_camera(self):
        """Reset the camera to the original position."""
        self.camera.setPos(self.original_camera_pos)
        self.camera.setHpr(self.original_camera_hpr)
        
    def toggle_path_display(self):
        """Toggle the display of the A* path."""
        if hasattr(self, 'path_nodes') and self.path_nodes is not None:
            # If path is already displayed, remove it
            self.path_nodes.removeNode()
            self.path_nodes = None
        else:
            # Create the path visualization
            self.path_nodes = self.render.attachNewNode("PathNodes")
            
            # Visualize the path
            for i, (x, y) in enumerate(self.path):
                # Create a marker for each step in the path
                path_marker = self.loader.loadModel("models/misc/sphere")
                path_marker.setScale(0.15)  # Make it smaller than player/goal
                
                # Color gradient from green (start) to red (end)
                progress = i / max(1, len(self.path) - 1)
                path_marker.setColor(progress, 1 - progress, 0, 0.8)
                
                # Position slightly above the floor
                path_marker.setPos(
                    x * self.cell_size + self.cell_size/2,
                    y * self.cell_size + self.cell_size/2,
                    0.2  # Just above the floor
                )
                path_marker.reparentTo(self.path_nodes)
            
            # Add a light to make the path glow
            plight = PointLight('pathlight')
            plight.setColor((0.5, 0.5, 0.8, 1))
            plight.setAttenuation((1, 0, 2))
            plnp = self.path_nodes.attachNewNode(plight)
            plnp.setPos(
                self.width * self.cell_size / 2,
                self.height * self.cell_size / 2,
                1.0
            )
            self.render.setLight(plnp)
        
    def update(self, task):
        """Update function called each frame."""
        # Handle keyboard input
        self.handle_movement()
        
        # Update player light position
        self.plnp.setPos(self.player.getPos() + LVector3(0, 0, 1))
        
        # Update the minimap less frequently to improve performance
        self.minimap_update_counter += 1
        if self.minimap_update_counter >= 15:  # Update every 15 frames
            self.update_minimap()
            self.minimap_update_counter = 0
        
        return Task.cont
        
    def handle_movement(self):
        """Handle player movement based on keyboard input."""
        # Get camera direction for relative movement
        heading = self.camera.getH() * math.pi / 180  # Convert to radians
        
        # Calculate movement direction
        move_speed = 0.1
        move_x = 0
        move_y = 0
        
        if self.keyMap["forward"]:
            move_x += -math.sin(heading) * move_speed
            move_y += -math.cos(heading) * move_speed
        if self.keyMap["backward"]:
            move_x += math.sin(heading) * move_speed
            move_y += math.cos(heading) * move_speed
        if self.keyMap["left"]:
            move_x += -math.cos(heading) * move_speed
            move_y += math.sin(heading) * move_speed
        if self.keyMap["right"]:
            move_x += math.cos(heading) * move_speed
            move_y += -math.sin(heading) * move_speed
            
        # Apply movement
        self.camera.setPos(
            self.camera.getX() + move_x,
            self.camera.getY() + move_y,
            self.camera.getZ()
        )
        
        # Handle rotation
        if self.keyMap["rotate-left"]:
            self.camera.setH(self.camera.getH() + 1)
        if self.keyMap["rotate-right"]:
            self.camera.setH(self.camera.getH() - 1)
        
        # Handle zoom with a smooth rate and bounds
        zoom_speed = 0.1
        min_height = 1.0  # Don't go below this height
        max_height = max(self.width, self.height) * self.cell_size * 1.5  # Don't go too high
        
        if self.keyMap["zoom-in"]:
            new_z = max(self.camera.getZ() - zoom_speed, min_height)
            self.camera.setZ(new_z)
        if self.keyMap["zoom-out"]:
            new_z = min(self.camera.getZ() + zoom_speed, max_height)
            self.camera.setZ(new_z)
        

def run_maze3d(width: int = 10, height: int = 10, seed: Optional[int] = None):
    """Run the 3D maze application.
    
    Args:
        width: Width of the maze in cells
        height: Height of the maze in cells
        seed: Optional seed for maze generation
    """
    app = Maze3D(width, height, seed)
    app.run()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="3D Maze Visualization with A* Pathfinding")
    parser.add_argument("--width", type=int, default=10, help="Maze width (default: 10)")
    parser.add_argument("--height", type=int, default=10, help="Maze height (default: 10)")
    parser.add_argument("--seed", type=int, default=None, help="Seed for maze generation (default: random)")
    args = parser.parse_args()
    
    run_maze3d(args.width, args.height, args.seed)