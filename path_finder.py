from typing import List, Tuple, Any
from collections import deque

class PathFinder:
    """A class to handle pathfinding operations on a 2D grid."""
    
    def __init__(self, matrix: List[List[Any]]):
        """Initialize PathFinder with a matrix."""
        self.matrix = matrix
        self.rows = len(matrix)
        self.cols = len(matrix[0]) if matrix else 0
        self.directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # down, up, right, left

    def find_symbol(self, symbol: str) -> Tuple[int, int]:
        """Find coordinates of a specific symbol in the matrix."""
        for r in range(self.rows):
            for c in range(self.cols):
                if str(self.matrix[r][c]) == str(symbol):
                    return (r, c)
        raise ValueError(f"Symbol {symbol} not found in matrix")

    def is_traversable(self, value: Any, target_symbol: str) -> bool:
        """
        Check if a cell is traversable.
        Only allows:
        - Cells with value 0
        - The specific target symbol
        - The start symbol '*'
        """
        return (
            value == 0 or 
            str(value) == str(target_symbol) or 
            str(value) == '*'
        )

    def calculate_path(self, start, end_symbol: str) -> List[Tuple[int, int]]:
        """Calculate the shortest path between two points and return as coordinates."""
        try:
            start = start
            end = self.find_symbol(end_symbol)
            
            # Calculate distances from the end point
            distances = self.calculate_distances(end, end_symbol)
            
            # Find path from start to end using the calculated distances
            path = self.find_path(
                start=start,
                distance_matrix=distances,
                target_symbol=end_symbol
            )
            
            return path if path else []
            
        except ValueError as e:
            print(f"Error calculating path: {str(e)}")
            return []

    def calculate_distances(self, target: Tuple[int, int], target_symbol: str) -> List[List[float]]:
        """Calculate distances from target point using BFS."""
        distances = [[float('inf')] * self.cols for _ in range(self.rows)]
        queue = deque([target])
        distances[target[0]][target[1]] = 0
        
        while queue:
            row, col = queue.popleft()
            current_distance = distances[row][col]

            for dx, dy in self.directions:
                new_row, new_col = row + dx, col + dy
                
                # Check bounds
                if not (0 <= new_row < self.rows and 0 <= new_col < self.cols):
                    continue
                    
                # Skip if we already found a shorter path
                if distances[new_row][new_col] <= current_distance + 1:
                    continue
                    
                # Check if cell is traversable
                cell_value = self.matrix[new_row][new_col]
                if not self.is_traversable(cell_value, target_symbol):
                    continue

                distances[new_row][new_col] = current_distance + 1
                queue.append((new_row, new_col))

        return distances

    def find_path(self, start, distance_matrix: List[List[float]], 
                 target_symbol: str) -> List[Tuple[int, int]]:
        """Find the shortest path using the distance matrix."""
        if distance_matrix[start[0]][start[1]] == float('inf'):
            return []  # No path exists
            
        path = [(start[0], start[1])]
        current = start
        # print(f"Current {current}")
        while distance_matrix[current[0]][current[1]] > 0:  # Continue until we reach distance 0 (target)
            row, col = current
            
            # Find the neighbor with minimum distance
            min_distance = float('inf')
            next_pos = None
            
            for dx, dy in self.directions:
                new_row, new_col = row + dx, col + dy
                
                if not (0 <= new_row < self.rows and 0 <= new_col < self.cols):
                    continue
                    
                if not self.is_traversable(self.matrix[new_row][new_col], target_symbol):
                    continue
                    
                dist = distance_matrix[new_row][new_col]
                if dist < min_distance:
                    min_distance = dist
                    next_pos = (new_row, new_col)
            
            if next_pos is None:
                return []  # No path found
                
            path.append(next_pos)
            current = next_pos
            
            if len(path) > self.rows * self.cols:  # Prevent infinite loops
                return []

        return path

    def print_path(self, path: List[Tuple[int, int]]) -> None:
        """Print the matrix with the path marked."""
        display_matrix = [row[:] for row in self.matrix]
        
        # Mark path with '$$'
        for row, col in path:
            if isinstance(display_matrix[row][col], (int, str)):
                display_matrix[row][col] = '**'
                
        # Print the matrix
        for row in display_matrix:
            print(" ".join(f"{str(elem):>6}" for elem in row))

        print("\n")