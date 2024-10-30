radio.setGroup(1)
radio.setTransmitPower(2)
let sensor_id = "S1"
basic.forever(function () {
    basic.showString("S")
    radio.sendString(sensor_id)
    basic.pause(1000)
})
