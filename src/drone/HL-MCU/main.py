print("----- CENTAURI HIGH-LEVEL MCU -----")
print("gitub.com/TimHanewich/centauri")
print()

# all imports
print("Importing libraries...")
import machine
import asyncio
import tools
from HC12 import HC12
from TFLuna import TFLuna
from QMC5883L import QMC5883L
from bmp085 import BMP180


# First thing is first: set up onboard LED, turn it on while loading
led = machine.Pin("LED", machine.Pin.OUT)
led.on()

# establish failure pattern
import time
def FATAL_ERROR() -> None:
    while True:
        led.on()
        time.sleep(1.0)
        led.off()
        time.sleep(1.0)

async def main() -> None:

    # next, set up radio communication via HC-12. 
    # this is a priority to confirm it is online
    uart_hc12:machine.UART = machine.UART(1, tx=machine.Pin(4), rx=machine.Pin(5), baudrate=9600) # 9600 baudrate is the default baudrate for the HC12
    hc12:HC12 = HC12(uart_hc12, 3) # set pin = GP3
    hc12_connected:bool = False
    for t in range(0, 5): # 5 attempts:
        print("Attempt # " + str(t + 1) + " to validate HC-12 is connected...")
        if hc12.pulse:
            print("HC-12 connection confirmed!")
            hc12_connected = True
            break
        else:
            print("Attempt to pulse HC-12 failed.")
            time.sleep(0.5)

    # if the HC-12 is not connected, fail
    if hc12_connected == False:
        print("Unable to confirm HC-12 connection. Failing.")
        FATAL_ERROR()

    # configure HC-12:
    print("Setting HC-12 mode...")
    hc12.mode = 3
    print("Setting HC-12 channel...")
    hc12.channel = 2
    print("Setting HC-12 power...")
    hc12.power = 8
    print("HC-12 settings complete!")

    # send out an HC-12 message to confirm we are online
    print("Sending online message...")
    hc12.send(tools.pack_special_packet("online") + "\r\n".encode())
    print("Online message sent.")

    # set up I2C bus for all 3 I2C devices connected to the HL MCU: TF Luna (0x10), BMP180 (0x77), and QMC5883L (0x0D)
    i2c = machine.I2C(1, sda=machine.Pin(6), scl=machine.Pin(7))
    i2c_scan:list[int] = i2c.scan()
    print("I2C scan: " + str(i2c_scan))

    # confirm TF Luna is connected
    if 0x10 not in i2c_scan:
        print("TF-Luna not connected on I2C bus!")
        hc12.send(tools.pack_special_packet("no luna") + "\r\n".encode())
        FATAL_ERROR()
    luna:TFLuna = TFLuna(i2c)
    if luna.signature:
        print("TF Luna connected!")
        hc12.send(tools.pack_special_packet("luna good") + "\r\n".encode())
    else:
        print("TF-Luna not connected! Signature unsuccessful.")
        hc12.send(tools.pack_special_packet("no luna sig") + "\r\n".encode())
        FATAL_ERROR()

    # confirm if BMP180 is connected
    if 0x77 in i2c_scan:
        print("BMP180 confirmed to be connected.")
        hc12.send(tools.pack_special_packet("BMP180 good") + "\r\n".encode())
    else:
        print("BMP180 not found on expected I2C bus!")
        hc12.send(tools.pack_special_packet("no BMP180") + "\r\n".encode())
        FATAL_ERROR()
    bmp180:BMP180 = None
    try:
        bmp180 = BMP180(i2c)
    except:
        hc12.send(tools.pack_special_packet("BMP180 init fail") + "\r\n".encode())
        print("BMP180 initialization fail.")
        FATAL_ERROR()

    # confirm if QMC5883L is connected
    if 0x0D in i2c_scan:
        print("QMC5883L confirmed to be connected!")
        hc12.send(tools.pack_special_packet("QMC5883L good") + "\r\n".encode())
    else:
        print("QMC5883L not connected!")
        hc12.send(tools.pack_special_packet("no QMC5883L") + "\r\n".encode())
        FATAL_ERROR()
    qmc:QMC5883L = None
    try:
        qmc = QMC5883L(i2c)
        qmc.calibrate(0, 0, 0, 0, 0, 0) # calibrate with basic values, later to be replaced
    except:
        hc12.send(tools.pack_special_packet("QMC5883L init fail") + "\r\n".encode())
        print("QMC5883L initialization fail.")
        FATAL_ERROR()

    # Confirm LL MCU is operating
    uart_llmcu = machine.UART(0, tx=machine.Pin(16), rx=machine.Pin(17), baudrate=115200)
    print("Sending PING to LL-MCU...")
    uart_llmcu.write("TIMHPING\r\n".encode()) # send ping
    LLMCU_Ponged:bool = False
    started = time.ticks_ms()
    while (time.ticks_ms() - started) < 10000: # wait for a max of 10 seconds
        if uart_llmcu.any() > 0:
            print("Data available! Reading line...")
            data = uart_llmcu.readline()
            if "TIMHPONG\r\n".encode() in data:
                print("LL-MCU ponged!")
                LLMCU_Ponged = True
                break
            else:
                print("It was not a PONG. Waiting a bit longer for PONG...")
        time.sleep(0.1)

    # if the LL MCU did not pong back, fail
    #LLMCU_Ponged = True # uncomment this to bypass LLMCU needing to be on and communicated with (for testing purposes)
    if LLMCU_Ponged == False:
        print("LLMCU did not pong back. Failing.")
        hc12.send(tools.pack_special_packet("LLMCU no pong") + "\r\n".encode())
        FATAL_ERROR()

    # Declare all settings variables that will be tracked and continuously sent back to remote controller via HC-12 (radio communication): SYSTEM STATUS
    battery_voltage:float = 0.0
    tfluna_distance:int = 0 # distance reading, in cm (0-800)
    tfluna_strength:int = 0 # strength reading
    altitude:float = 0.0 # altitude reading, in meters (inferred from pressure reading from BMP180)
    heading:float = 0.0 # magnetic heading

    # declare a "container" variable that will contain new Control Status data received from the LL-MCU
    # this will be updated by the llmcu_rx coroutine
    # and later delivered, as is, to the drone via HC-12
    # I ensured the packet identifier in the header byte is the same for both
    # when it is None, that means there is no new information to pass along.
    llmcu_status:bytes = None 
    

    async def led_flicker() -> None:
        while True:
            led.toggle()
            await asyncio.sleep(0.25)
        
    async def sensor_reading() -> None:
        """Continuously collects sensor values from HL-MCU connected sensors (which will later be sent to HL-MCU)"""

        # declare nonlocal variables we will be updating
        nonlocal battery_voltage
        nonlocal tfluna_distance
        nonlocal tfluna_strength
        nonlocal altitude
        nonlocal heading

        # create ADC
        vbat_adc = machine.ADC(machine.Pin(26))

        while True:

            # read battery voltage through ADC
            vbat_u16:int = vbat_adc.read_u16()
            vbat_percent:float = vbat_u16 / 65535 # as percentage
            pin_voltage:float = 3.3 * vbat_percent # the actual voltage on the pin
            battery_voltage:float = pin_voltage / 0.1803571 # this value based on the voltage divider being used (to "reverse" the voltage divider)

            # read the TF Luna values
            tfluna_distance = luna.distance
            tfluna_strength = luna.strength

            # read altitude from BMP180
            altitude = bmp180.altitude

            # read heading from QMC5883L
            heading = qmc.heading

            # print (testing purposes, uncomment if you want)
            #print("vBat: " + str(battery_voltage) + ", TFLuna Dist: " + str(tfluna_distance) + ", TFLuna Strength: " + str(tfluna_strength) + ", altitude: " + str(altitude) + ", heading: " + str(heading))

            # wait
            await asyncio.sleep(0.05) # 20 Hz

    async def llmcu_rx() -> None:
        """Focused on continuously listening for received data from the LL MCU, usually a status packet."""

        # declare nonlocal variables this coroutine will update
        nonlocal llmcu_status

        # declare rxBuffer for data received from LL-MCU via UART
        rxBuffer:bytearray = bytearray()

        while True:
            if uart_llmcu.any() > 0:

                # collect all available bytes
                rxBuffer.extend(uart_llmcu.read())

                while "\r\n".encode() in rxBuffer:

                    # get the line
                    loc:int = rxBuffer.find("\r\n".encode())
                    ThisLine:bytes = rxBuffer[0:loc+2] # include the \r\n at the end
                    rxBuffer = rxBuffer[loc+2:] # remove the line from the buffer

                    # handle the line based on what it is
                    if ThisLine[0] == 0b00000000: # status packet
                        llmcu_status_unpacked:dict = tools.unpack_status(ThisLine) # there is really no need to unpack the full data and parse it, but doing this anyway as a way to validate it is good data
                        if llmcu_status_unpacked != None: # if it unpacked correctly
                            #print(str(llmcu_status_unpacked))
                            llmcu_status = ThisLine # update the llmcu_status variable (only bytes) which will later be sent to remote controller via HC-12
                    else:
                        print("Unknown packet from LL-MCU: " + str(ThisLine))
            
            # wait
            await asyncio.sleep(0.05) # 20 Hz... The LL MCU is supposed to provide at 10 Hz, so reading quicker here to ensure a backlog does not build up

    async def radio_rx() -> None:
        """Focused on continuously receiving commands from the controller via the HC-12 (radio communications)"""
        pass

    async def radio_tx() -> None:
        """Focused on continuously sending status packets and such to the controller via the HC-12."""
        
        # declare nonlocal variables
        nonlocal llmcu_status

        while True:

            # is there control status available from the LL-MCU?
            if llmcu_status != None:

                # append \r\n at the end if needed
                if not llmcu_status.endswith("\r\n".encode()):
                    llmcu_status = llmcu_status + "\r\n".encode()

                # send via HC-12
                hc12.send(llmcu_status)
                print("Just sent: " + str(llmcu_status))

                # clear it out
                llmcu_status = None

            # wait
            await asyncio.sleep(0.1) # 10 hz
                



    # Create functions for threads
    # - update TF Luna reading
    # - update BMP180 reading
    # - update QMC5883L reading
    # - update battery voltage reading
    # - Check for new messages on HC-12 and handle them
    # - Send HC-12 messages (status packets)

    # Get all threads going
    print("Now triggering all coroutines...")
    task_led_flicker = asyncio.create_task(led_flicker())
    task_sensor_reading = asyncio.create_task(sensor_reading())
    task_llmcu_rx = asyncio.create_task(llmcu_rx())
    task_radio_rx = asyncio.create_task(radio_rx())
    task_radio_tx = asyncio.create_task(radio_tx())
    await asyncio.gather(task_led_flicker, task_sensor_reading, task_llmcu_rx, task_radio_rx, task_radio_tx)

# run main program via asyncio
asyncio.run(main())