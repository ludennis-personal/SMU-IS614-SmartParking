import serial
import subprocess
# import paho.mqtt.client as mqtt
import sys
import logging
import time
import platform
import serial.tools.list_ports
from firebase import firebase
import configparser

# Configure logging
logging.basicConfig(format="%(asctime)s %(levelname)s %(filename)s:%(funcName)s():%(lineno)i: %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)
logger = logging.getLogger(__name__)



# Handles the case when the serial port can't be found
def handle_missing_serial_port() -> None:
    print("Couldn't connect to the micro:bit. Try these steps:")
    print("1. Unplug your micro:bit")
    print("2. Close Tera Term, PuTTY, and all other apps using the micro:bit")
    print("3. Close all MakeCode browser tabs using the micro:bit")
    print("4. Run this app again")
    exit()


# Initializes the serial device. Tries to get the serial port that the micro:bit is connected to
def get_serial_dev_name() -> str:
    logger.info(f"sys.platform: {sys.platform}")
    logger.info(f"platform.system: {platform.system()}\n")

    serial_dev_name = None

    # For Windows
    if "windows" in platform.system().lower():
        # List the serial devices available
        try:
            ports = list(serial.tools.list_ports.comports())
            if not ports:
                handle_missing_serial_port()

            logger.info(f"Available serial ports:\n{ports}")
            
            for port in ports:
                logger.info(f"Port: {port.device}, Description: {port.description}")
            
            serial_dev_name = ports[0].device if ports else None


        except subprocess.CalledProcessError as e:
           logger.error(f"Couldn't list serial ports: {e.output.decode('utf8').strip()}")
           handle_missing_serial_port()

    else:
        logger.error(f"Unknown sys.platform: {sys.platform}")
        exit()


    logger.info(f"serial_dev_name: {serial_dev_name}\n")


    if not serial_dev_name:
        handle_missing_serial_port()


    return serial_dev_name


# Handles incoming serial data
def handle_serial_data(s: serial.Serial) -> None:

    # Receive Data
    data = s.readline().decode("utf-8").strip()
    logger.info(f"Received data: {data}")   # 2,SG888,A && 5,SG888,A

    # Insert to database


    # Check action_id for process

def read_config():
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read('config.ini')

    # Access values from the configuration file
    debug_mode = config.getboolean('General', 'debug')
    log_level = config.get('General', 'log_level')
    db_name = config.get('Database', 'db_name')
    db_host = config.get('Database', 'db_link')

    # Return a dictionary with the retrieved values
    config_values = {
        'debug_mode': debug_mode,
        'log_level': log_level,
        'db_name': db_name,
        'db_link': db_host
    }

    return config_values

def main() -> None:

    # Initialize
    config_data = read_config()

    # Connect to Gateway
    port = get_serial_dev_name()
    # logger.info(f"Port: {port}")

    # Connect to Firebase
    FBConn = firebase.FirebaseApplication(config_data['db_link'], None)
    logger.info("Connected to Database\n") if FBConn else logger.info("Failed to connect to Database\n")

    # Run the Microbit and Get Serial Write
    with serial.Serial(port=port, baudrate=115200, timeout=10) as s:
        # Sleep to make sure serial port has been opened before doing anything else
        time.sleep(1)

        # Reset the input and output buffers in case there is leftover data
        s.reset_input_buffer()
        s.reset_output_buffer()

        # Loopy loop
        while True:

            # Read from the serial port
            if s.in_waiting > 0:
                handle_serial_data(s)


if __name__ == "__main__":
   main()