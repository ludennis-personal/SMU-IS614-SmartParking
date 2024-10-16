// 先用button代替，不然是接收到gate的信号然后发送
input.onButtonPressed(Button.A, function () {
    radio.sendString("" + action_id + "," + id2 + "," + zone)
})
radio.onReceivedString(function (receivedString) {
    if (receivedString == "W") {
        zone = "W"
        serial.writeLine("Zone: " + zone)
    }
})
input.onButtonPressed(Button.B, function () {
    if (action_id == 1) {
        action_id = 3
    } else if (action_id == 3) {
        action_id = 4
    } else {
        action_id = 1
    }
})
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
basic.forever(function () {
    basic.showString("" + (action_id))
})
