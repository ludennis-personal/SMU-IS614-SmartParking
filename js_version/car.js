//  先用button代替，不然是接收到gate的信号然后发送
input.onButtonPressed(Button.A, function on_button_pressed_a() {
    radio.sendString("" + ("" + action_id) + "," + id2 + "," + zone)
})
radio.onReceivedString(function on_received_string(receivedString: string) {
    
    if (receivedString == "W") {
        zone = "W"
        serial.writeLine("Zone: " + zone)
    }
    
})
input.onButtonPressed(Button.B, function on_button_pressed_b() {
    
    if (action_id < 6) {
        action_id = action_id + 1
    } else {
        action_id = 1
    }
    
})
let action_id = 0
let zone = ""
let id2 = ""
id2 = "SG888"
zone = "A"
radio.setGroup(1)
action_id = 1
basic.forever(function on_forever() {
    basic.showString("" + ("" + action_id))
})
