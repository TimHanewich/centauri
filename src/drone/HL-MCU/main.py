print("Hello! I am the Centauri quadcopter's High-Level MCU.")

# First thing is first: set up onboard LED, turn it on while loading
import machine
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

# all imports
print("Importing libraries...")
import asyncio
import tools
from HC12 import HC12
from TFLuna import TFLuna
from QMC5883L import QMC5883L
from bmp085 import BMP180

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
    except:
        hc12.send(tools.pack_special_packet("QMC5883L init fail") + "\r\n".encode())
        print("QMC5883L initialization fail.")
        FATAL_ERROR()

    # Confirm LL MCU is operating
    uart_llmcu = machine.UART(0, tx=machine.Pin(16), rx=machine.Pin(17), baudrate=115200)

    # Declare all variables that will be tracked and reported on
    llmcu_status_data:bytes = None # the status packet that arrived from the LL MCU
    battery_voltage:float = 0.0
    tfluna_distance:int = 0 # distance reading, in cm (0-800)
    tfluna_strength:int = 0 # strength reading
    altitude:float = 0.0 # altitude reading, in meters (inferred from pressure reading from BMP180)
    heading:float = 0.0 # magnetic heading

    async def llmcu_rx() -> None:
        """Focused on continuously listening for received data from the LL MCU, usually a status packet."""

        # declare nonlocal variables
        nonlocal uart_llmcu
        nonlocal llmcu_status_data

        while True:
            if uart_llmcu.any() > 0:
                data:bytes = uart_llmcu.readline()

                # handle it based on what it is
                if data[0] == 0b00000000: # status packet
                    if data.endswith("\r\n".encode()):
                        data = data[0:-2] # trim off \r\n
                    llmcu_status_data = data
                else:
                    print("Unknown packet from LLMCU: " + str(data))
            
            # wait
            time.sleep(0.05) # 20 Hz... The LL MCU is supposed to provide at 10 Hz, so reading quicker here to ensure a backlog does not build up

    async def radio_rx() -> None:
        """Focused on continuously receiving commands from the controller via the HC-12 (radio communications)"""
        pass

    async def radio_tx() -> None:
        """Focused on continuously sending status packets and such to the controller via the HC-12."""

        # declare nonlocal variables
        nonlocal hc12 # what we will use to send info!
        nonlocal llmcu_status_data
        nonlocal battery_voltage
        nonlocal tfluna_distance
        nonlocal tfluna_strength
        nonlocal altitude
        nonlocal heading

        # continuously send data
        while True:
            if llmcu_status_data != None: # if new data is available from the LL MCU
                
                # prepare and send
                ToAppend:bytes = tools.pack_status_packet_part2(battery_voltage, tfluna_distance, tfluna_strength, altitude, heading)
                ToSend:bytes = llmcu_status_data + ToAppend + "\r\n".encode()
                hc12.send(ToSend) # send it!

                # clear out old data from LL MCU. We will only send again once we have new data
                llmcu_status_data = None

            # wait
            time.sleep(0.1) # 10 Hz


    # Create functions for threads
    # - update TF Luna reading
    # - update BMP180 reading
    # - update QMC5883L reading
    # - update battery voltage reading
    # - Check for new messages on HC-12 and handle them
    # - Send HC-12 messages (status packets)

# run main program via asyncio
asyncio.run(main())