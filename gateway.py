import serial
import subprocess
import sys
import logging
import time
from datetime import datetime
import platform
import serial.tools.list_ports
import math

import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from google.cloud.firestore_v1.base_query import FieldFilter

# Configure logging
logging.basicConfig(format="%(asctime)s %(levelname)s %(filename)s:%(funcName)s():%(lineno)i: %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Realtime Firebase Configure
# FBConn = firebase.FirebaseApplication("https://smu-is614-project-default-rtdb.asia-southeast1.firebasedatabase.app/", None)

# Cloud Firestore Configure
cred = credentials.Certificate("smu-is614-project-6fc3d026a44c.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
carpark_ref = db.collection('test')     # Collection of the carpark

# DEFAULT PRICES
prices = {
    'A': 10,
    'B': 8,
    'W': 5
}


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

def get_time_difference(entrance_time, exit_time):

    time_format = '%d/%m/%Y %H:%M:%S'    

     # Convert the string times to datetime objects
    pEntranceTime = datetime.strptime(entrance_time, time_format)
    pExitTime = datetime.strptime(exit_time, time_format)
    
    # Calculate the time difference
    time_difference = pEntranceTime - pExitTime

    # Convert time difference to total minutes
    total_minutes = time_difference.total_seconds() / 60  # Convert seconds to minutes
    
    # Convert minutes to hours and round up
    total_hours = math.ceil(total_minutes / 60)

    return total_hours

def car_entrance(car_id, zone):

    # Get current time
    now = datetime.now()
    entrance_time = now.strftime("%d/%m/%Y %H:%M:%S")
    logger.info(f"Entrance Time: {entrance_time}")

    # Save data to be inserted to database
    # data_to_insert = {
    #     'car_id': car_id,
    #     'zone': zone,
    #     'entrance_time': entrance_time,
    #     'exit_time': "",
    #     'amount': float(0)
    # }

    # Insert to database
    document = now.strftime("%Y-%m-%d_%H:%M:%S") + "_" + car_id

    carpark_ref.document(document).set({
        'car_id': car_id,
        'zone': zone,
        'entrance_time': entrance_time,
        'exit_time': "",
        'duration': "",
        'amount': float(0)
    })
    logger.info(f'Data inserted to database successfully...\n')


# Function for car exit
def car_exit(car_id, zone):

    # Assuming that there will be no overnight cars yet
    now = datetime.now()
    exit_time = now.strftime("%d/%m/%Y %H:%M:%S")
    logger.info(f"Exit Time: {exit_time}")

    # Query for the car
    date_filter = now.strftime('%d/%m/%Y')
    car_query = carpark_ref.where(
        filter=FieldFilter('car_id', '==', car_id)
    ).where(filter=FieldFilter('entrance_time', '>=', date_filter)
    ).where(filter=FieldFilter('exit_time', '==', '')
    ).where(filter=FieldFilter('zone', '==', zone)
    ).stream()

    # To Dictionary
    car_data = None
    for car in car_query:
        car_data = car.to_dict()
        logger.info(f'car_data: {car_data}\n')
        break

    # Calculate the time, amount, duration etc.
    if car_data:
        # Convert to datetime format
        car_data.update({'duration': get_time_difference(car_data.get('entrance_time'), exit_time)})
        logger.info(f"ceil duration: {car_data.get('duration')}")

        car_data['amount'] = prices[zone] * car_data['duration']
        logger.info(f"amount: {car_data['amount']}")
    
    
# Handles incoming serial data
def handle_serial_data(s: serial.Serial) -> None:

    # Receive Data
    data = s.readline().decode("utf-8").strip()
    logger.info(f"Received data: {data}")   # 2,SG888,A && 5,SG888,A

    # Process Data
    arr = data.split(",")

    car_id = arr[1]
    zone = arr[2]
    # logger.info(f"car_id: {car_id}")
    # logger.info(f"zone: {zone}")

    # if arr[0] == "2" or arr[0] == "5":    
    # Not doing condition, since gateway microbit already have already validated

    # From Main Entrance
    if arr[0] == "2": car_entrance(car_id,zone)
    # From Main Exit
    elif arr[0] == "5": car_exit(car_id,zone)



# def read_config():
#     # Create a ConfigParser object
#     config = configparser.ConfigParser()

#     # Read the configuration file
#     config.read('config.ini')

#     # Access values from the configuration file
#     debug_mode = config.getboolean('General', 'debug')
#     log_level = config.get('General', 'log_level')
#     db_name = config.get('Database', 'db_name')
#     db_host = config.get('Database', 'db_link')

#     # Return a dictionary with the retrieved values
#     config_values = {
#         'debug_mode': debug_mode,
#         'log_level': log_level,
#         'db_name': db_name,
#         'db_link': db_host
#     }

#     return config_values

def main() -> None:

    # Initialize
    # config_data = read_config()

    # Connect to Gateway
    port = get_serial_dev_name()
    # logger.info(f"Port: {port}")

    # Connect to Realtime Database Firebase
    # FBConn = firebase.FirebaseApplication(config_data['db_link'], None)

    # Connect to Cloud Firestore
    # db = firestore.client()

    logger.info("Connected to Database\n") if db else logger.info("Failed to connect to Database\n")

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