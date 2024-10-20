radio.set_group(1)  # The car listens to sensor broadcasts on group 1

sensor1_rssi = 0
sensor2_rssi = 0
car_id = "SG888"  # The unique identifier of the car
zone = "A"  # Initial zone
action_id = 1  # Initialize action_id as an integer

# Button A: Manually send action_id, car_id, and zone info to the gateway
def on_button_pressed_a():
    radio.send_string(f"{str(action_id)},{car_id},{zone}")
input.on_button_pressed(Button.A, on_button_pressed_a)

# Button B: Cycle through action_id values (1 -> 3 -> 4)
def on_button_pressed_b():
    global action_id
    if action_id == 1:
        action_id = 3
    elif action_id == 3:
        action_id = 4
    else:
        action_id = 1
input.on_button_pressed(Button.B, on_button_pressed_b)

# Function to handle received signals (from sensors or other sources)
def on_received_string(receivedString):
    global zone, action_id, sensor1_rssi, sensor2_rssi
    message_parts = receivedString.split(",")  # Split the received message by commas
    
    # Check if the message contains "W", if so, update the zone
    if message_parts[0] == "W":
        zone = "W"
        serial.write_line("Zone: " + zone)
    
    # If the message contains action_id and sensor_id, handle RSSI
    else:
        action_id = int(message_parts[0])  # Extract action_id and convert to integer
        sensor_id = message_parts[1]  # Extract sensor_id
        
        # Only calculate RSSI if action_id is 7
        if action_id == 7:
            # Get the current RSSI (signal strength)
            rssi = radio.received_packet(RadioPacketProperty.SIGNAL_STRENGTH)
            
            # Identify the sensor by its sensor_id and assign RSSI accordingly
            if sensor_id == "S1":
                sensor1_rssi = rssi  # Sensor 1
            elif sensor_id == "S2":
                sensor2_rssi = rssi  # Sensor 2
            
            # Send RSSI info to the gateway, including action_id, car_id, and RSSI values
            message_to_gateway = f"{action_id},{car_id}, Sensor1 RSSI: {sensor1_rssi}, Sensor2 RSSI: {sensor2_rssi}"
            radio.send_string(message_to_gateway)
            
            # Output to serial for debugging
            serial.write_line(f"Sent to gateway: {message_to_gateway}")
radio.on_received_string(on_received_string)

# Serial redirection to USB for debugging
serial.redirect(SerialPin.USB_TX, SerialPin.USB_RX, BaudRate.BAUD_RATE115200)

# Continuously display the current action_id for debugging purposes
def on_forever():
    basic.show_string("" + str(action_id))
basic.forever(on_forever)
