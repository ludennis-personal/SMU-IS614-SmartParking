import logging
import math
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from typing import List, Tuple
from google.cloud.firestore_v1.base_query import FieldFilter
from path_finder import PathFinder
from navigation import ParkingNavigation

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(filename)s:%(funcName)s():%(lineno)i: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Constants
FIREBASE_CREDENTIALS_PATH = "./credentials/smu-is614-project-firebase-adminsdk-e2hbf-4acd7e6ccc.json"
COLLECTION_NAME = 'test'
TIME_FORMAT = '%d/%m/%Y %H:%M:%S'
DATE_FORMAT = "%Y-%m-%d_%H:%M:%S"
CURRENT_POSITION = "*"
PT = -75
ENVIRONMENT = 2

# Parking Map 9x10
## A = VIP, B = RESERVED, W = FREE
PARKING_MAP = [
    [0,0,0,0,'MALL','MALL',0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,'ENT'],
    [0,'-','-','-','-','-','-',0,0,0,'ENT'],
    [0,'-','V','V','V','V','-',0,0,0,0],
    [0,'-','V','V','V','V','-',0,0,0,0],
    [0,'VEXIT',0,0,0,0,'A',0,0,'W','W'],
    [0,'VEXIT',0,0,0,0,'A',0,0,'W','W'],
    [0,'-','-','-','-','-','-','-',0,'W','W'],
    [0,0,'-','R','R','R','R','-',0,'W','W'],
    [0,0,'-','R','R','R','R','-',0,'W','W'],
    [0,0,'REXIT',0,0,0,0,'B',0,'W','W'],
    ['EXT',0,'REXIT',0,0,0,0,'B',0,'W','W'],
    ['EXT',0,'-','-','-','-','-','-',0,'W','W'],
    [0,0,0,0,0,0,0,0,0,'W','W'],
    [0,0,0,0,0,0,0,0,0,'W','W'],
]

res = []
rows = len(PARKING_MAP)
cols = len(PARKING_MAP[0])
for r in range(rows):
    for c in range(cols):
        if PARKING_MAP[r][c] == 0:
            res.append([r,c])
# print(res)

# Parking prices by zone
ZONE_PRICES = {
    'A': 10,
    'B': 8,
    'W': 5
}

# Gate to Zone mapping
GATE_TO_ZONE = {
    'A': 'A',
    'B': 'B',
    'W': 'W'
}


class DatabaseConnection:
    def __init__(self):
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.carpark_ref = self.db.collection(COLLECTION_NAME)
        
        if self.db:
            logger.info("Connected to Database")
        else:
            logger.error("Failed to connect to Database")

class ParkingSystem:
    def __init__(self):
        self.db_conn = DatabaseConnection()
        self.pathfinder = PathFinder(PARKING_MAP)
        self.nav_system = ParkingNavigation([(3, 1), (13, 7)], res)
        self.PT = PT
        self.ENVIRONMENT = ENVIRONMENT

    def calculate_duration(self, entrance_time: str, exit_time: str) -> int:
        """Calculate parking duration in hours (rounded up)"""
        entrance = datetime.strptime(entrance_time, TIME_FORMAT)
        exit_dt = datetime.strptime(exit_time, TIME_FORMAT)
        duration_minutes = (exit_dt - entrance).total_seconds() / 60
        return math.ceil(duration_minutes / 60)

    def record_entrance(self, car_id: str, zone: str) -> List[Tuple[int, int]]:
        """Record car entrance and return navigation path"""
        logger.info("Recording car entrance")

        # Record entrance in database
        now = datetime.now()
        entrance_time = now.strftime(TIME_FORMAT)
        document_id = f"{now.strftime(DATE_FORMAT)}_{car_id}"
        
        self.db_conn.carpark_ref.document(document_id).set({
            'car_id': car_id,
            'zone': zone,
            'entrance_time': entrance_time,
            'exit_time': "",
            'duration': "",
            'amount': 0.0
        })
        
        logger.info(f"Car entrance recorded - car_id: {car_id}, zone: {zone}")

    def record_exit(self, car_id: str, gate: str) -> None:
        """Record car exit and calculate parking fee"""
        logger.info("Recording car exit")
        
        zone = GATE_TO_ZONE.get(gate)
        if not zone:
            logger.error(f"Invalid gate: {gate}")
            return

        exit_time = datetime.now().strftime(TIME_FORMAT)
        
        # Query for the car's entrance record
        car_query = (
            self.db_conn.carpark_ref
            .where(filter=FieldFilter('car_id', '==', car_id))
            .where(filter=FieldFilter('zone', '==', zone))
            .where(filter=FieldFilter('exit_time', '==', ''))
            .stream()
        )

        car_doc = next(car_query, None)
        if not car_doc:
            logger.error(f"No entrance record found for car_id: {car_id}")
            return

        car_data = car_doc.to_dict()
        duration = self.calculate_duration(car_data['entrance_time'], exit_time)
        amount = ZONE_PRICES[zone] * duration

        # Update record with exit information
        self.db_conn.carpark_ref.document(car_doc.id).update({
            "amount": amount,
            "exit_time": exit_time,
            "duration": duration
        })
        logger.info(f"Car exit recorded - car_id: {car_id}, duration: {duration}h, amount: ${amount}")

    def get_current_distance(self, rssi):
        """Get the current distance of the car"""
        top = self.PT - rssi
        bottom = 10 * self.ENVIRONMENT

        distance = 10 ** (top/bottom)
        logger.info(f"distance: {distance}")

        return float(distance)
    
    def navigate(self, car_id, gate, rssi_1, rssi_2):
        """Navigation for Car"""
        logger.info(f'RSSI_1: {rssi_1}, RSSI_2: {rssi_2}')

        # Simulate receiving distance data
        current_distances = [self.get_current_distance(rssi_1), self.get_current_distance(rssi_2)]
        
        # Get navigation instructions
        result = self.nav_system.get_navigation_instructions(current_distances)
        logger.info(f"result: {result}\n")

        # Find start and end positions first
        #start = self.pathfinder.find_symbol(result['nearest_path_point'])
        start = result['nearest_path_point']
        end = self.pathfinder.find_symbol(gate)
        
        # Calculate path using these positions
        path = self.pathfinder.calculate_path(start, gate)
        
        if path:
            # Calculate distances matrix from the end position
            distances = self.pathfinder.calculate_distances(end, gate)
            
            # Use the distances matrix to find the path from start
            path_matrix = self.pathfinder.find_path(
                start=start,
                distance_matrix=distances,
                target_symbol=gate
            )
            
            logger.info(f"Navigation path for car {car_id} from gate {gate}:")
            self.pathfinder.print_path(path_matrix)
