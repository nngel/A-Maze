import heapq
from typing import Dict, List, Tuple, Set, Optional


class AStar:
    def __init__(self, width: int, height: int, walls: Set[Tuple[Tuple[int, int], Tuple[int, int]]]):
        """Initialize the A* algorithm with maze dimensions and walls."""
        self.width = width
        self.height = height
        self.walls = walls
        # Track the nodes we've explored for visualization
        self.explored_nodes = set()
        # Track the order in which nodes are explored
        self.explored_order = []
    
    def _get_neighbors(self, node: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring cells for a given node."""
        x, y = node
        neighbors = []
        
        # Check all four adjacent cells
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            
            # Check if the neighbor is within the maze boundaries
            if 0 <= nx < self.width and 0 <= ny < self.height:
                # Check if there's no wall between the current node and the neighbor
                wall = tuple(sorted([(x, y), (nx, ny)]))
                if wall not in self.walls:
                    neighbors.append((nx, ny))
        
        return neighbors
    
    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Manhattan distance heuristic."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def find_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Find the shortest path from start to end using A* algorithm.
        
        Args:
            start: Starting point coordinates (x, y)
            end: Ending point coordinates (x, y)
            
        Returns:
            List of coordinates representing the path from start to end, or None if no path exists
        """
        # Reset explored nodes
        self.explored_nodes = set()
        self.explored_order = []
        
        # Priority queue for open nodes
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        # For tracking where nodes came from
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {}
        came_from[start] = None
        
        # Cost from start to each node
        g_score: Dict[Tuple[int, int], float] = {start: 0}
        
        # Estimated total cost from start to goal through each node
        f_score: Dict[Tuple[int, int], float] = {start: self._heuristic(start, end)}
        
        # Set of visited nodes
        open_set_hash = {start}
        
        while open_set:
            # Get the node with the lowest f_score
            _, current = heapq.heappop(open_set)
            open_set_hash.remove(current)
            
            # Add to explored nodes for visualization
            self.explored_nodes.add(current)
            self.explored_order.append(current)  # Record the exact order of exploration
            
            # If we reached the goal, reconstruct and return the path
            if current == end:
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            
            # Explore neighbors
            for neighbor in self._get_neighbors(current):
                # Calculate tentative g_score
                tentative_g_score = g_score[current] + 1
                
                # If we found a better path to the neighbor
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self._heuristic(neighbor, end)
                    
                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
                        open_set_hash.add(neighbor)
        
        # No path found
        return None
        
    def get_explored_nodes(self) -> Set[Tuple[int, int]]:
        """Return the set of nodes that were explored during the search."""
        return self.explored_nodes
        
    def get_explored_order(self) -> List[Tuple[int, int]]:
        """Return the ordered list of nodes as they were explored during the search."""
        return self.explored_order