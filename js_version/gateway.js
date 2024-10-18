radio.onReceivedString(function (receivedString) {
    data = receivedString
    arr = data.split(",")
    serial.writeLine(data)
    // Serial write for database insert
    if (arr[0] == valid_id[0] || arr[0] == valid_id[1]) {
        serial.writeString("" + arr[0] + "," + arr[1] + "," + arr[2])
    }
})
let arr: string[] = []
let data = ""
let valid_id: string[] = []
serial.redirect(
SerialPin.USB_TX,
SerialPin.USB_RX,
BaudRate.BaudRate115200
)
radio.setGroup(1)
valid_id = ["2", "5"]
basic.forever(function () {
    basic.showLeds(`
        # # # # #
        # . . . .
        # . # # #
        # . . . #
        # # # # #
        `)
})
