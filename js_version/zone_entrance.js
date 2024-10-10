radio.onReceivedString(function (receivedString) {
    data = receivedString
    serial.writeLine("Data: " + data)
    arr = data.split(",")
    // serial.writeLine("action_id: " + arr[0])
    // serial.writeLine("car_id: " + arr[1])
    // serial.writeLine("zone: " + arr[2])
    // car_id, zone
    if (arr[0] == "4" && arr[2] == zone) {
        basic.showArrow(ArrowNames.East)
        serial.writeLine("Zone Matched, Welcome!")
    } else {
        basic.showIcon(IconNames.No)
        serial.writeLine("Either action_id or zone is wrong!")
    }
})
let arr: string[] = []
let data = ""
radio.setGroup(1)
let zone = "A"
basic.forever(function () {
    basic.showString("A")
})
