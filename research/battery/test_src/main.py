import time
import machine
import HC12

# set up
vbat_adc = machine.ADC(machine.Pin(26))
led = machine.Pin("LED", machine.Pin.OUT)
uart_hc12 = machine.UART(1, tx=machine.Pin(8), rx=machine.Pin(9), baudrate=9600)
hc12 = HC12.HC12(uart_hc12, 7)

# pulse HC-12
time.sleep(1.0)
print("HC-12 pulse: " + str(hc12.pulse))

while True:

    led.on()

    # read
    vbat_u16:int = vbat_adc.read_u16()
    line:str = str(time.ticks_ms()) + " ms: " + str(vbat_u16) + " ADC reading on GP26"
    
    # send
    hc12.send(line.encode())

    # write
    f = open("battery.txt", "at")
    print(line)
    f.write(line + "\n")
    f.close()

    led.off()

    # wait
    time.sleep(1.0)