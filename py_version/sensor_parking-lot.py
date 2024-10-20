i = 0
lot2 = 0
lot1 = 0
lots = [lot1, lot2]
basic.show_icon(IconNames.YES)

def on_every_interval():
    global i
    lots[0] = grove.measure_in_centimeters(DigitalPin.P0)
    lots[1] = grove.measure_in_centimeters(DigitalPin.P1)
    i = 0
    while i < len(lots):
        if lots[i] < 10:
            serial.write_line("LOT " + ("" + str(i)) + ": PARKED")
        else:
            serial.write_line("LOT " + ("" + str(i)) + ": NOT PARKED")
        i += 1
    serial.write_line("------------------------------")
loops.every_interval(1000, on_every_interval) # Change to every minute if implementation
