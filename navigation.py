import math
from typing import Tuple, List

class ParkingNavigation:
    def __init__(self, reference_points: List[Tuple[float, float]], predefined_paths: List[List[Tuple[float, float]]]):
        """
        Initialize the parking navigation system.
        
        Args:
            reference_points: A list of reference point coordinates [(x1, y1), (x2, y2)]
            predefined_paths: A list of coordinates for predefined driving paths
        """
        if len(reference_points) != 2:
            raise ValueError("Two reference points must be provided")
        self.reference_points = reference_points
        self.predefined_paths = predefined_paths
        
    def calculate_position(self, distances: Tuple[float, float]) -> Tuple[float, float]:
        """
        Calculate the current position based on the distances to two reference points.
        
        Args:
            distances: Distances to the two reference points (d1, d2)
        
        Returns:
            The current coordinates (x, y)
        """
        x1, y1 = self.reference_points[0]
        x2, y2 = self.reference_points[1]
        d1, d2 = distances
        
        # Use trilateration algorithm to calculate position
        # Based on the intersection of two circles
        dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        
        if dist > d1 + d2:
            raise ValueError("Invalid distance data: The distance between points is greater than the distance between reference points")
            
        # Use the law of cosines to calculate the angle
        cos_angle = (d1 ** 2 + dist ** 2 - d2 ** 2) / (2 * d1 * dist)
        sin_angle = math.sqrt(1 - cos_angle ** 2)
        
        # Calculate current position
        x = x1 + d1 * (cos_angle * (x2 - x1) / dist - sin_angle * (y2 - y1) / dist)
        y = y1 + d1 * (sin_angle * (x2 - x1) / dist + cos_angle * (y2 - y1) / dist)
        
        return x, y
    
    def find_nearest_path_point(self, current_pos: Tuple[float, float]) -> Tuple[float, float]:
        """
        Find the nearest point on the predefined path based on the current position.
        
        Args:
            current_pos: Current position (x, y)
        
        Returns:
            Coordinates of the nearest path point (x, y)
        """
        min_distance = float('inf')
        nearest_point = None
        
        for path in self.predefined_paths:
            for point in path:
                dist = math.sqrt((point[0] - current_pos[0]) ** 2 + 
                               (point[1] - current_pos[1]) ** 2)
                if dist < min_distance:
                    min_distance = dist
                    nearest_point = point
                    
        return nearest_point
    
    def get_navigation_instructions(self, current_distances: Tuple[float, float]) -> dict:
        """
        Get navigation instructions.
        
        Args:
            current_distances: Current distances to the two reference points
        
        Returns:
            A dictionary containing the current position, navigation information, angle, and distance
        """
        try:
            # Calculate current position
            current_pos = self.calculate_position(current_distances)
            
            # Find the nearest path point
            target_point = self.find_nearest_path_point(current_pos)
            
            # Calculate direction angle
            angle = math.degrees(math.atan2(target_point[1] - current_pos[1],
                                          target_point[0] - current_pos[0]))
            
            # Calculate distance
            distance = math.sqrt((target_point[0] - current_pos[0]) ** 2 +
                               (target_point[1] - current_pos[1]) ** 2)
            
            return {
                "current_position": current_pos,
                "nearest_path_point": target_point,
                "angle": angle,
                "distance": distance,
                "status": "success"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

if __name__ == "__main__":
    # Define reference point coordinates
    reference_points = [(0, 0), (10, 0)]
    
    # Define predefined paths
    predefined_paths = [
        [(1, 1), (2, 2), (3, 3), (4, 4)],
        [(5, 1), (6, 2), (7, 3), (8, 4)]
    ]
    
    # Initialize the navigation system
    nav_system = ParkingNavigation(reference_points, predefined_paths)
    
    # Simulate receiving distance data
    current_distances = (5.0, 5.0)
    
    # Get navigation instructions
    result = nav_system.get_navigation_instructions(current_distances)
    print(result)
