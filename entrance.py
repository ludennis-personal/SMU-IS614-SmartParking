radio.onReceivedString(function on_received_string(receivedString: string) {
    
    data = receivedString
    serial.writeLine("Data: " + data)
    arr = data.split(",")
    serial.writeLine("action_id: " + arr[0])
    //  car_id, zone
    if (arr[0] == "1") {
        if (arr[2] != "A" || "B") {
            radio.sendString("W")
        }
        
    }
    
    basic.showArrow(ArrowNames.East)
})
let data = ""
let arr : string[] = []
radio.setGroup(1)
basic.forever(function on_forever() {
    basic.showLeds(`
        # # # # #
        # # # # #
        # . . . #
        # . . . #
        # . . . #
        `)
})
