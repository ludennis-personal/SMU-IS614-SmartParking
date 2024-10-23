input.onButtonPressed(Button.A, function () {
    radio.sendValue("paid", 1)
})
radio.onReceivedString(function (receivedString) {
    data = receivedString
    arr = data.split(",")
    // Serial write for database insert
    if (arr[0] == valid_id[0] || arr[0] == valid_id[1]) {
        serial.writeLine(data)
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
