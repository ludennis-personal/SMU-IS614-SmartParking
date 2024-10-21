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

# Cloud Firestore Configure
cred = credentials.Certificate("smu-is614-project-firebase-adminsdk-e2hbf-4acd7e6ccc.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
logger.info("Connected to Database\n") if db else logger.info("Failed to connect to Database\n")

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
    logger.info(f"Entrance Time: {entrance_time}\tExit Time: {exit_time}")
    
    # Calculate the time difference
    time_difference = pExitTime - pEntranceTime

    # Convert time difference to total minutes
    total_minutes = time_difference.total_seconds() / 60  # Convert seconds to minutes
    
    # Convert minutes to hours and round up
    total_hours = math.ceil(total_minutes / 60)

    return total_hours

def car_entrance(car_id, zone):
    print('\n--------------------- CAR ENTRANCE ---------------------------')

    # Get current time
    now = datetime.now()
    entrance_time = now.strftime("%d/%m/%Y %H:%M:%S")
    logger.info(f"Entrance Time: {entrance_time}")

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
    logger.info(f'Data inserted to database successfully...')
    print('--------------------- END -------------------------------\n')

# Function for car exit
def car_exit(car_id, zone):
    print('\n--------------------- CAR EXIT ---------------------------')
    # Assuming that there will be no overnight cars yet
    now = datetime.now()
    exit_time = now.strftime("%d/%m/%Y %H:%M:%S")

    # Query for the car
    logger.info(f"[Read] Query: car_id={car_id}, zone={zone}")
    car_query = carpark_ref.where(
        filter=FieldFilter('car_id', '==', car_id)
    ).where(filter=FieldFilter('zone', '==', zone)
    ).where(filter=FieldFilter('exit_time', '==', '')
    ).stream()

    # logger.info(f"car_query: {car_query}")

    # To Dictionary
    car_data = None
    for car in car_query:
        car_data = car.to_dict()
        car_data['id'] = car.id
        logger.info(f'car_data: {car_data}')
        break

    # Calculate the time, amount, duration etc.
    if car_data:
        # Convert to datetime format
        duration = get_time_difference(car_data.get('entrance_time'), exit_time)
        car_data.update({'duration': duration})
        logger.info(f"duration: {car_data.get('duration')} Hours (Round Up)")

        car_data['amount'] = prices[zone] * car_data['duration']
        logger.info(f"amount: {car_data['amount']}")

        # Update database
        carpark_ref.document(car_data['id']).update({
            "amount": car_data['amount'],
            "exit_time": exit_time,
            "duration": duration
        })
        logger.info(carpark_ref.document(car_data['id']).get().to_dict())
        logger.info("[Update] Data Updated Successfully...")
        
    # If data not found
    else:
        logger.info("No Result Found.")
    
    print('--------------------- END -------------------------------\n')

# Handles incoming serial data
def handle_serial_data(s: serial.Serial) -> None:

    # Receive Data
    data = s.readline().decode("utf-8").strip()
    

    try:
        # Process Data
        arr = data.split(",")

        car_id = arr[1]
        zone = arr[2]
        # logger.info(f"car_id: {car_id}")
        # logger.info(f"zone: {zone}")

        logger.info(f"Received data: {data}")   # 2,SG888,A && 5,SG888,A
        # if arr[0] == "2" or arr[0] == "5":        # Not doing condition, since gateway microbit already have already validated
        
        # From Main Entrance
        if arr[0] == "2": car_entrance(car_id,zone)
        # From Main Exit
        elif arr[0] == "5": car_exit(car_id,zone)

    except:
        logger.info(f"Message: {data}") 


def main() -> None:

    # Connect to Gateway
    port = get_serial_dev_name()
    # logger.info(f"Port: {port}")

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