# 先用button代替，不然是接收到gate的信号然后发送

def on_button_pressed_a():
    radio.send_string("" + str(action_id) + "," + id2 + "," + zone)
input.on_button_pressed(Button.A, on_button_pressed_a)

def on_received_string(receivedString):
    global zone
    if receivedString == "W":
        zone = "W"
        serial.write_line("Zone: " + zone)
radio.on_received_string(on_received_string)

def on_button_pressed_b():
    global action_id
    if action_id < 6:
        action_id = action_id + 1
    else:
        action_id = 1
input.on_button_pressed(Button.B, on_button_pressed_b)

action_id = 0
zone = ""
id2 = ""
id2 = "SG888"
zone = ""
radio.set_group(1)
action_id = 1

def on_forever():
    basic.show_string("" + str(action_id))
basic.forever(on_forever)
