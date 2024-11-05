function on_every_interval () {
    // Read ultrasonic sensors
    // Read ultrasonic sensors
    ultrasonics[0] = grove.measureInCentimeters(DigitalPin.P0)
    ultrasonics[1] = grove.measureInCentimeters(DigitalPin.P1)
    // Log timestamp
    serial.writeLine("" + (input.runningTime()))
    // Check each parking lot
    for (let i = 0; i <= ultrasonics.length - 1; i++) {
        // Get current sensor reading
        distance = ultrasonics[i]
        // Check if car is parked (distance less than threshold)
        if (distance < DISTANCE_THRESHOLD) {
            // If status changed from not parked to parked
            if (!(lots[i])) {
                lots[i] = true
                serial.writeLine("LOT " + i + ": PARKED")
                radio.sendString("6," + lot_group + i + ",parked")
            }
        } else {
            // If status changed from parked to not parked
            if (lots[i]) {
                lots[i] = false
                serial.writeLine("LOT " + i + ": NOT PARKED")
                radio.sendString("6," + lot_group + i + ",not_parked")
            }
        }
    }
}
let distance = 0
let lot_group = ""
let ultrasonics: number[] = []
let lots: boolean[] = []
let DISTANCE_THRESHOLD = 0
radio.setGroup(1)
// cm
DISTANCE_THRESHOLD = 5
// Parking status for each lot
lots = [false, false]
// Sensor readings
ultrasonics = [0, 0]
// Lot group identifier
lot_group = "A"
basic.showIcon(IconNames.SmallHeart)
basic.forever(function () {
    on_every_interval()
    basic.pause(2000)
})
