import time
import machine

vbat_adc = machine.ADC(machine.Pin(26))
led = machine.Pin("LED", machine.Pin.OUT)

while True:

    led.on()

    # read
    vbat_u16:int = vbat_adc.read_u16()

    # write
    f = open("battery.txt", "at")
    line:str = str(time.ticks_ms()) + " ms: " + str(vbat_u16) + " ADC reading on GP26"
    print(line)
    f.write(line + "\n")
    f.close()

    led.off()

    # wait
    time.sleep(1.0)