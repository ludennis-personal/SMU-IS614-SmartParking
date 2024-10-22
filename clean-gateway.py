import logging
import math
import platform
import serial
import serial.tools.list_ports
import sys
import time
from datetime import datetime

# Firebase Packages
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

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

# Parking prices by zone
ZONE_PRICES = {
    'A': 10,
    'B': 8,
    'W': 5
}

# DATABASE
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

# PARKING SYSTEM
class ParkingSystem:
    def __init__(self):
        self.db_conn = DatabaseConnection()
    
    def calculate_duration(self, entrance_time: str, exit_time: str) -> int:
        """Calculate parking duration in hours (rounded up)"""
        entrance = datetime.strptime(entrance_time, TIME_FORMAT)
        exit_dt = datetime.strptime(exit_time, TIME_FORMAT)
        
        duration_minutes = (exit_dt - entrance).total_seconds() / 60
        return math.ceil(duration_minutes / 60)

    def record_entrance(self, car_id: str, zone: str) -> None:
        """Record car entrance in database"""
        logger.info("Recording car entrance")
        
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
        logger.info("Car entrance recorded successfully")
        logger.info(f"car_id: {car_id}, zone {zone}, entrance_time: {entrance_time}")

    def record_exit(self, car_id: str, zone: str) -> None:
        """Record car exit and calculate parking fee"""
        logger.info("Recording car exit")
        
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
        logger.info(f"Car exit recorded for car_id: {car_id}. Duration: {duration} h, Amount: ${amount}")


# Serial Connection for Gateway Microbit
class SerialConnection:
    @staticmethod
    def get_serial_port() -> str:
        """Get the serial port for the micro:bit"""
        if "windows" not in platform.system().lower():
            raise SystemError(f"Unsupported platform: {sys.platform}")

        ports = list(serial.tools.list_ports.comports())
        if not ports:
            raise ConnectionError("No serial ports found. Please check device connection.")

        logger.info(f"Available serial ports: {ports}")
        return ports[0].device

    @staticmethod
    def handle_serial_message(message: str, parking_system: ParkingSystem) -> None:
        """Process incoming serial messages"""
        try:
            action, car_id, zone = message.split(",")
            
            if action == "2":  # Entrance
                parking_system.record_entrance(car_id, zone)
            elif action == "5":  # Exit
                parking_system.record_exit(car_id, zone)
            else:
                logger.warning(f"Unknown action code: {action}")
                
        except ValueError:
            logger.error(f"Message: {message}")

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
                    SerialConnection.handle_serial_message(data, parking_system)
                    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
