radio.onReceivedString(function (receivedString) {
    data = receivedString
    serial.writeLine("Data: " + data)
    arr = data.split(",")
    if (arr[0] == valid_id && on_process == false) {
        // 5,SG888,A
        radio.sendString("5," + arr[1] + "," + arr[2])
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
