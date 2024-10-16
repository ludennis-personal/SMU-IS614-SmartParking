radio.onReceivedString(function (receivedString) {
    data = receivedString
    serial.writeLine("Data: " + data)
    arr = data.split(",")
    // serial.writeLine("action_id: " + arr[0])
    // serial.writeLine("zone: " + arr[2])
    // car_id, zone
    if (arr[0] == valid_id) {
        if (arr[2] != "A" && "B") {
            radio.sendString("W")
            arr[2] = "W"
        }
        radio.sendString("2," + arr[1] + "," + arr[2])
    }
    basic.showArrow(ArrowNames.East)
})
let arr: string[] = []
let data = ""
let valid_id = ""
serial.redirect(
SerialPin.USB_TX,
SerialPin.USB_RX,
BaudRate.BaudRate115200
)
radio.setGroup(1)
valid_id = "1"
basic.forever(function () {
    basic.showLeds(`
        # # # # #
        # # # # #
        # . . . #
        # . . . #
        # . . . #
        `)
})
