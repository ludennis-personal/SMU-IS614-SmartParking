// 先用button代替，不然是接收到gate的信号然后发送
input.onButtonPressed(Button.A, function () {
    radio.sendString("" + action_id + "," + id2 + "," + zone)
})
radio.onReceivedString(function (receivedString) {
    if (receivedString == "W") {
        zone = "W"
        serial.writeLine("Zone: " + zone)
    }
    if (action_id == 1) {
        if (receivedString == "s1") {
            s1_rssi = radio.receivedPacket(RadioPacketProperty.SignalStrength)
            serial.writeString("s1: " + s1_rssi)
        } else if (receivedString == "s2") {
            s2_rssi = radio.receivedPacket(RadioPacketProperty.SignalStrength)
            serial.writeString("s2: " + s2_rssi)
        }
    }
})
input.onButtonPressed(Button.B, function () {
    if (action_id == 1) {
        action_id = 3
    } else if (action_id == 3) {
        action_id = 4
        s1_rssi = 0
        s2_rssi = 0
    } else {
        action_id = 1
    }
})
let s2_rssi = 0
let s1_rssi = 0
let action_id = 0
let zone = ""
let id2 = ""
serial.redirect(
SerialPin.USB_TX,
SerialPin.USB_RX,
BaudRate.BaudRate115200
)
id2 = "SG888"
zone = "A"
radio.setGroup(1)
action_id = 1
s1_rssi = 0
s2_rssi = 0
basic.forever(function () {
    basic.showString("" + (action_id))
    if (action_id == 1 && (s1_rssi != 0 && s2_rssi != 0)) {
        radio.sendString("7" + "," + s1_rssi + "," + s2_rssi)
        serial.writeString("Send Gateway: 7" + "," + s1_rssi + "," + s2_rssi)
    }
})
