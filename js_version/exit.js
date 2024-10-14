radio.onReceivedString(function (receivedString) {
    data = receivedString
    serial.writeLine("Data: " + data)
    arr = data.split(",")
    // serial.writeLine("action_id: " + arr[0])
    // serial.writeLine("car_id: " + arr[1])
    if (arr[0] == valid_id && on_process == false) {
        serial.writeLine("Sending data to Gateway and waiting for feedback....")
        on_process = true
    }
})
let arr: string[] = []
let data = ""
let valid_id = ""
let on_process = false
serial.redirect(
SerialPin.USB_TX,
SerialPin.USB_RX,
BaudRate.BaudRate115200
)
radio.setGroup(1)
on_process = false
valid_id = "4"
basic.forever(function () {
    basic.showLeds(`
        # # # # #
        # # # # #
        # . . . #
        # . . . #
        # . . . #
        `)
})
