radio.setGroup(1)
radio.setTransmitPower(2)
let sensor_id = "s1"
basic.forever(function () {
    basic.showString("S")
    radio.sendString(sensor_id)
    serial.writeLine("" + (radio.receivedPacket(RadioPacketProperty.SignalStrength)))
    basic.pause(1000)
})
