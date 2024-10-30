import logging
import math
import platform
import serial
import serial.tools.list_ports
import sys
import time
from datetime import datetime
from typing import List, Tuple

# Firebase Packages
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# Import PathFinder
from pathfinder import PathFinder

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
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 10
TIME_FORMAT = '%d/%m/%Y %H:%M:%S'
DATE_FORMAT = "%Y-%m-%d_%H:%M:%S"
ENTRANCE_SYMBOL = "*"

# Parking Map 9x10
PARKING_MAP = [
    [0,ENTRANCE_SYMBOL,0,0,0,0,0,0,0,0,],
    [0,'-','-',0,0,0,'-','-','-','A',],
    [0,'-','-',0,0,0,'-','A1','A1','A1',],
    [0,'-',0,0,0,0,'-','-','-','-',],
    [0,'-','-',0,0,0,0,'-','-','-',],
    [0,0,0,0,0,0,0,'-','B1','B1',],
    [0,0,0,0,0,0,0,'-','-','B',],
    ['W','W','W','W','W',0,0,0,0,0,],
    ['W','W','W','W','W','W',0,0,0,'%',]
]

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

    
    def get_distance(rssi_1, rssi_2) -> None:
        pass


class SerialConnection:
    @staticmethod
    def get_serial_port() -> str:
        """Get the serial port for the micro:bit"""
        if "windows" not in platform.system().lower():
            raise SystemError(f"Unsupported platform: {sys.platform}")

        ports = list(serial.tools.list_ports.comports())
        if not ports:
            raise ConnectionError("No serial ports found")

        return ports[0].device

    @staticmethod
    def handle_serial_message(message: str, parking_system: ParkingSystem, serial_conn: serial.Serial) -> None:
        """Process incoming serial messages and send responses"""
        try:
            data = message.split(",")
            action = data[0]

            if action == "2":  # Entrance

                car_id = data[1]
                gate = data[2]

                # Insert to database
                parking_system.record_entrance(car_id, gate)

                # Find start and end positions first
                start = parking_system.pathfinder.find_symbol(ENTRANCE_SYMBOL)
                end = parking_system.pathfinder.find_symbol(gate)
                
                # Calculate path using these positions
                path = parking_system.pathfinder.calculate_path(ENTRANCE_SYMBOL, gate)
                
                if path:
                    # Calculate distances matrix from the end position
                    distances = parking_system.pathfinder.calculate_distances(end, gate)
                    
                    # Use the distances matrix to find the path from start
                    path_matrix = parking_system.pathfinder.find_path(
                        start=start,
                        distance_matrix=distances,
                        target_symbol=gate
                    )
                    
                    # Print the path visualization
                    
                    logger.info(f"Navigation path for car {car_id} from gate {gate}:")
                    parking_system.pathfinder.print_path(path_matrix)
                    
                    # Convert path to string format expected by micro:bit
                    # path_str = ";".join(f"{x},{y}" for x, y in path_matrix)
                    # serial_conn.write(f"PATH:{path_str}\n".encode())
                
            elif action == "5":  # Exit

                car_id = data[1]
                gate = data[2]
                
                parking_system.record_exit(car_id, gate)
            
            elif action == "7":     # Get Distance

                s1_rssi = data[1]
                s2_rssi = data[2]

                parking_system.get_distance(s1_rssi, s2_rssi)

            else:
                logger.warning(f"Unknown action code: {action}")
                
        except ValueError as e:
            logger.error(f"Message parsing error: {message}, Error: {str(e)}")

def main():
    try:
        parking_system = ParkingSystem()
        port = SerialConnection.get_serial_port()
        
        with serial.Serial(port=port, baudrate=SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as serial_conn:
            time.sleep(1)  # Allow serial connection to stabilize
            serial_conn.reset_input_buffer()
            serial_conn.reset_output_buffer()
            
            logger.info("Starting main loop...")
            while True:
                if serial_conn.in_waiting > 0:
                    data = serial_conn.readline().decode("utf-8").strip()
                    SerialConnection.handle_serial_message(data, parking_system, serial_conn)
                    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()