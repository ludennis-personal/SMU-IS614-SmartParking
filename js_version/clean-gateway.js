// Initialize radio
function initializeRadio () {
    radio.setGroup(RADIO_GROUP)
}
// Handle button press
input.onButtonPressed(Button.A, function () {
    radio.sendValue("paid", 1)
})
// Initialize everything
function initialize () {
    initializeSerial()
    initializeRadio()
}
// Initialize serial communication
function initializeSerial () {
    serial.redirect(
    SerialPin.USB_TX,
    SerialPin.USB_RX,
    BaudRate.BaudRate115200
    )
}
// Handle received radio messages
radio.onReceivedString(function (receivedString) {
    // Ignore duplicate messages
    // if (receivedString == lastReceivedData) {
    // return
    // }
    lastReceivedData = receivedString
    // Split and validate message
    messageParts = receivedString.split(",")
    // Check if first element is a valid ID
    if (VALID_IDS.indexOf(messageParts[0]) != -1) {
        serial.writeLine(receivedString)
    }
})
/**
 * Initialize variables
 */
let messageParts: string[] = []
let lastReceivedData = ""
let RADIO_GROUP = 0
let VALID_IDS: string[] = []
// Constants for configuration
VALID_IDS = ["2", "5", "6", "7"]
RADIO_GROUP = 1
// Start the program
initialize()
// Display pattern on LED matrix
basic.forever(function () {
    basic.showLeds(`
        # # # # #
        # . . . .
        # . # # #
        # . . . #
        # # # # #
        `)
})
