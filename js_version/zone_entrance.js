radio.onReceivedString(function (receivedString) {
    data = receivedString
    serial.writeLine("Data: " + data)
    arr = data.split(",")
    if (arr[0] == valid_id) {
        // car_id, zone
        if (arr[2] == zone) {
            basic.showArrow(ArrowNames.East)
            serial.writeLine("Zone Matched, Welcome!")
        } else {
            basic.showIcon(IconNames.No)
            serial.writeLine("Either action_id or zone is wrong!")
        }
    }
})
let arr: string[] = []
let data = ""
let valid_id = ""
let zone = ""
serial.redirect(
SerialPin.USB_TX,
SerialPin.USB_RX,
BaudRate.BaudRate115200
)
radio.setGroup(1)
zone = "A"
valid_id = "3"
basic.forever(function () {
    basic.showString(zone)
})
