radio.onReceivedString(function (receivedString) {
    data = receivedString
    arr = data.split(",")
    // Serial write for database insert
    if (valid_id.indexOf(arr[0]) != -1) {
        serial.writeString("" + arr[1] + "," + arr[2])
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
