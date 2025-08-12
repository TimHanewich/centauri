import machine
import time
import asyncio
import tools

async def main() -> None:

    # First thing is first: set up onboard LED, turn it on while loading
    print("Turning LED on...")
    led = machine.Pin("LED", machine.Pin.OUT)
    led.on()

    # establish failure pattern
    def FATAL_ERROR() -> None:
        while True:
            led.on()
            time.sleep(1.0)
            led.off()
            time.sleep(1.0)

    # set up UART interface with HL MCU
    print("Establishing UART interface...")
    uart = machine.UART(0, tx=machine.Pin(12), rx=machine.Pin(13), baudrate=115200)
    print("Sending BOOTING message over UART...")
    uart.write("TIMHBOOTING\r\n".encode()) # send a single "BOOTING" message to confirm we are booting

    # Confirm MPU-6050 is connected via I2C
    print("Setting up I2C...")
    i2c = machine.I2C(0, sda=machine.Pin(16), scl=machine.Pin(17))
    if 0x68 not in i2c.scan():
        print("MPU-6050 not connected via I2C!")
        FATAL_ERROR()
    else:
        print("MPU-6050 confirmed to be connected via I2C.")

    # Confirm MPU-6050 is on and operational by reading the "whoami" register
    print("Reading MPU-6050 WHOAMI register...")
    whoami:int = i2c.readfrom_mem(0x68, 0x75, 1)[0]
    if whoami == 0x68:
        print("MPU-6050 WHOAMI passed!")
    else:
        print("MPU-6050 WHOAMI Failed!")
        FATAL_ERROR()
    
    # Set up MPU-6050
    print("Waking up MPU-6050...")
    i2c.writeto_mem(0x68, 0x6B, bytes([0])) # wake up 
    print("Setting MPU-6050 gyro scale range to 250 d/s...")
    i2c.writeto_mem(0x68, 0x1B, bytes([0x00])) # set full scale range of gyro to 250 degrees per second
    print("Setting MPU-6050 accelerometer scale range to 2g...")
    i2c.writeto_mem(0x68, 0x1C, bytes([0x00])) # set full scale range of accelerometer to 2g (lowest, most sensitive)
    print("Setting MPU-6050 LPF to 10 Hz...")
    i2c.writeto_mem(0x68, 0x1A, bytes([0x05])) # set low pass filter for both gyro and accel to 10 hz (level 5 out of 6 in smoothing)

    # wait a moment, then validate MPU-6050 settings have taken place
    time.sleep(0.25)
    if i2c.readfrom_mem(0x68, 0x1B, 1)[0] == 0x00:
        print("MPU-6050 Gyro full scale range confirmed to be set at 250 d/s")
    else:
        print("MPU-6050 Gyro full scale range set failed!")
        FATAL_ERROR()
    if i2c.readfrom_mem(0x68, 0x1C, 1)[0] == 0x00:
        print("MPU-6050 accelerometer full scale range confirmed to be set at 2g")
    else:
        print("MPU-6050 accelerometer full scale range set failed!")
        FATAL_ERROR()
    if i2c.readfrom_mem(0x68, 0x1A, 1)[0] == 0x05:
        print("MPU-6050 low pass filter confirmed to be at 10 Hz")
    else:
        print("MPU-6050 low pass filter failed to set!")
        FATAL_ERROR()

    # declare variables that will be used throughout multiple coroutines
    m1_throttle:float = 0.0
    m2_throttle:float = 0.0
    m3_throttle:float = 0.0
    m4_throttle:float = 0.0
    pitch_rate:float = 0.0
    roll_rate:float = 0.0
    yaw_rate:float = 0.0
    pitch_angle:float = 0.0
    roll_angle:float = 0.0

    async def ledflicker() -> None:
        """Continuously flick the onboard LED."""
        nonlocal led
        while True:
            led.on()
            await asyncio.sleep(0.25)
            led.off()
            await asyncio.sleep(0.25)

    async def comms_rx() -> None:
        """Handles receiving of any data from the HL MCU"""

        # declare nonlocal variables
        nonlocal uart

        while True:
            if uart.any() > 0:
                data:bytes = uart.readline()

                # handle according to what it is
                if data == "TIMHPING\r\n".encode(): # simple check of life
                    uart.write("TIMHPONG\r\n".encode()) # respond pong
                else:
                    print("Unknown data received: " + str(data))
            
            # wait
            await asyncio.sleep(0.01) # 100 Hz max

    async def comms_tx() -> None:
        """Handles continuous sending of status data to HL MCU."""

        # declare nonlocal variables
        nonlocal uart
        nonlocal m1_throttle
        nonlocal m2_throttle
        nonlocal m3_throttle
        nonlocal m4_throttle
        nonlocal pitch_rate
        nonlocal roll_rate
        nonlocal yaw_rate
        nonlocal pitch_angle
        nonlocal roll_angle

        while True:

            # pack all data
            data:bytes = tools.pack_status_packet_part1(m1_throttle, m2_throttle, m3_throttle, m4_throttle, pitch_rate, roll_rate, yaw_rate, pitch_angle, roll_angle)

            # send the data
            uart.write(data + "\r\n".encode())

            # wait
            await asyncio.sleep(0.1) # 10 Hz

    async def flightcontrol() -> None:
        """Core flight controller routine."""
        pass

    # Run all threads!
    task_led_flicker = asyncio.create_task(ledflicker())
    task_comms_rx = asyncio.create_task(comms_rx())
    task_comms_tx = asyncio.create_task(comms_tx())
    task_fc = asyncio.create_task(flightcontrol())
    await asyncio.gather(task_led_flicker, task_comms_rx, task_comms_tx, task_fc)

asyncio.run(main())