let distance = 0
basic.forever(function () {
    basic.showIcon(IconNames.SmallSquare)
    distance = grove.measureInCentimeters(DigitalPin.P0)
    if (distance < 10) {
        basic.showArrow(ArrowNames.East)
        serial.writeLine("Car Detected, Gate Open!")
    }
})
