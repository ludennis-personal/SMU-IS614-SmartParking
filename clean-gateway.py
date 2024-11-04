import logging
import platform
import serial
import serial.tools.list_ports
import sys
import time

# Import custom modules
from parking_system import ParkingSystem

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(filename)s:%(funcName)s():%(lineno)i: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Constants
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 10
ENTRANCE_SYMBOL = "*"

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
            car_id = data[1]
            gate = data[2]

            if action == "2":  # Entrance
                # car_id = data[1]
                # gate = data[2]

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
                    
                    logger.info(f"Navigation path for car {car_id} from gate {gate}:")
                    parking_system.pathfinder.print_path(path_matrix)
                
            elif action == "5":  # Exit
                # car_id = data[1]
                # gate = data[2]
                parking_system.record_exit(car_id, gate)
            
            elif action == "7":  # Get Distance #7,CarID,RSSI_1,RSSI_2
                s1_rssi = float(data[3])
                s2_rssi = float(data[4])

                parking_system.navigate(car_id, gate, s1_rssi, s2_rssi)

            else:
                logger.warning(f"Unknown action code: {action}")
                
        except ValueError as e:
            logger.info(f"Message parsing error: {message}, Error: {str(e)}")

def main():
    try:
        parking_system = ParkingSystem()
        port = SerialConnection.get_serial_port()
        
        # port = "COM5"

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
        logger.info(f"Fatal error: {str(e)}")
        # sys.exit(1)

if __name__ == "__main__":
    main()