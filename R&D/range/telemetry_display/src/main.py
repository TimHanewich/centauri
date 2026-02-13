import machine
import time
from HC12 import HC12
from ssd1306 import SSD1306_I2C
from tools import unpack_control_packet

# create LED
led = machine.Pin("LED", machine.Pin.OUT)
led.on()

# issue pattern
def ISSUE_PATTERN() -> None:
    while True:
        led.on()
        time.sleep(1.0)
        led.off()
        time.sleep(1.0)

try:

    # Set up SSD-1306
    i2c = machine.I2C(0, sda=machine.Pin(20), scl=machine.Pin(21))
    oled = SSD1306_I2C(128, 64, i2c)

    # set up display msg function
    def msg(txt:str) -> None:
        oled.fill(0)
        oled.text(txt, 0, 0)
        oled.show()

    # display
    msg("Loading...")

    # set up HC-12
    uart = machine.UART(0, rx=machine.Pin(17), tx=machine.Pin(16), baudrate=9600)
    set_pin = 18
    hc12 = HC12(uart, set_pin)

    # pulse
    msg("Pulsing...")
    pulsed:bool = False
    for a in range(0, 5):
        msg("Pulse # " + str(a+1) + "...")
        if hc12.pulse:
            pulsed = True
            break
        else:
            time.sleep(1.0)

    # didn't work?
    if pulsed == False:
        msg("No pulse.")
        ISSUE_PATTERN()

    # configure
    msg("HC-12 config...")

    # clear out everything
    hc12.receive()
        
    # set mode to FU3 mode
    hc12.mode = 3
    time.sleep(0.25)

    # set mode to channel
    hc12.channel = 2
    time.sleep(0.25)

    # setting power is irrelevant as it is only passively receiving!
    
    # display success msg
    msg("HC-12 Configed!")
    time.sleep(0.5)

    # declare variables
    rxBuffer:bytearray = bytearray()
    ControlInput:list[int] = [0,0,0,0]
    lrecv_ticks_ms:int = None

    # continuously listen for packets
    while True:

        # receive + process
        new_data:bytes = hc12.receive()
        if new_data != None:
            rxBuffer.extend(new_data) # add it

            # is there a terminator?
            terminator:bytes = "\r\n".encode()
            if terminator in rxBuffer:

                # find the terminator
                terminator_loc = rxBuffer.find(terminator)

                # get everything before it
                this_msg:bytearray = rxBuffer[0:terminator_loc]
                rxBuffer = bytearray() # clear the buffer

                # print it
                print("Got this msg: " + str(this_msg))

                # unpack it
                unpack_successful:bool = unpack_control_packet(this_msg, ControlInput)
                if unpack_successful:
                    print("Got one! " + str(ControlInput))
                    lrecv_ticks_ms = time.ticks_ms()

        # display on OLED
        oled.fill(0)

        # show last recv
        if lrecv_ticks_ms != None:
            ms_ago:int = time.ticks_diff(time.ticks_ms(), lrecv_ticks_ms)

            # dont let it exceed 9999 (10 seconds)
            ms_ago = min(ms_ago, 9999)
            ms_ago_txt:str = str(ms_ago)
            while len(ms_ago_txt) < 4:
                ms_ago_txt = " " + ms_ago_txt

            oled.text("LRECV: " + ms_ago_txt + " ms", 0, 0)
        else:
            oled.text("LRECV: never", 0, 0)

        # show inputs
        packable_input_throttle:int = (ControlInput[0] * 100) // 65535                          # express between 0 and 100
        packable_input_pitch:int = ((((ControlInput[1] + 32768) * 100) // 65535) * 2) - 100     # express between -100 and 100
        packable_input_roll:int = ((((ControlInput[2] + 32768) * 100) // 65535) * 2) - 100      # express between -100 and 100
        packable_input_yaw:int = ((((ControlInput[3] + 32768) * 100) // 65535) * 2) - 100       # express between -100 and 100
        oled.text("T: " + str(packable_input_throttle) + "%", 0, 10)
        oled.text("P: " + str(packable_input_pitch) + "%", 0, 20)
        oled.text("R: " + str(packable_input_roll) + "%", 0, 30)
        oled.text("Y: " + str(packable_input_yaw) + "%", 0, 40)

        # put time at bottom (in seconds)
        oled.text("Time: " + str(int(time.ticks_ms() / 1000)), 0, 50)

        # show on OLED
        oled.show()
        
        # small delay
        time.sleep(0.01)


    



except Exception as ex:
    print("ISSUE: " + str(ex))
    ISSUE_PATTERN()


