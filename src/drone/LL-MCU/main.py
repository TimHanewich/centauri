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

    # measure gyro to estimate bias
    gxs:float = 0.0
    gys:float = 0.0
    gzs:float = 0.0
    samples:int = 0
    for i in range(3):
        print("Beginning gyro calibration in " + str(3 - i) + "... ")
        time.sleep(1.0)
    print("Calibrating gyro...")
    started_at_ticks_ms:int = time.ticks_ms()
    while (time.ticks_ms() - started_at_ticks_ms) < 3000: # 3 seconds
        gyro_data:bytes = i2c.readfrom_mem(0x68, 0x43, 6) # read 6 bytes, 2 for each axis
        gyro_x = (gyro_data[0] << 8) | gyro_data[1]
        gyro_y = (gyro_data[2] << 8) | gyro_data[3]
        gyro_z = (gyro_data[4] << 8) | gyro_data[5]
        if gyro_x >= 32768: gyro_x = ((65535 - gyro_x) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        if gyro_y >= 32768: gyro_y = ((65535 - gyro_y) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        if gyro_z >= 32768: gyro_z = ((65535 - gyro_z) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        gyro_x = gyro_x / 131 # now, divide by the scale factor to get the actual degrees per second
        gyro_y = gyro_y / 131 # now, divide by the scale factor to get the actual degrees per second
        gyro_z = gyro_z / 131 # now, divide by the scale factor to get the actual degrees per second
        gxs = gxs + gyro_x
        gys = gys + gyro_y
        gzs = gzs + gyro_z
        samples = samples + 1
        time.sleep(0.01)
    
    # calculate gyro bias
    print(str(samples) + " gyro samples collected.")
    gyro_bias_x:float = gxs / samples
    gyro_bias_y:float = gys / samples
    gyro_bias_z:float = gzs / samples
    print("Gyro Bias: " + str(gyro_bias_x) + ", " + str(gyro_bias_y) + ", " + str(gyro_bias_z))

    # declare variables that will be used across multiple coroutines: desired rate inputs
    # enter in via rx coroutine
    # used in flight control (pid loop) coroutine
    throttle_uint16:int = 0
    pitch_int16:int = 0
    roll_int16:int = 0
    yaw_int16:int = 0

    # declare variables that will be used accross multiple coroutines: flight control loop
    pitch_kp:float = 0.0
    pitch_ki:float = 0.0
    pitch_kd:float = 0.0
    roll_kp:float = 0.0
    roll_ki:float = 0.0
    roll_kd:float = 0.0
    yaw_kp:float = 0.0
    yaw_ki:float = 0.0
    yaw_kd:float = 0.0
    i_limit:float = 0.0

    # declare variables that will be used accross multiple coroutines: status
    m1_throttle:float = 0.0
    m2_throttle:float = 0.0
    m3_throttle:float = 0.0
    m4_throttle:float = 0.0
    pitch_rate:float = 0.0
    roll_rate:float = 0.0
    yaw_rate:float = 0.0
    pitch_angle:float = 0.0
    roll_angle:float = 0.0

    # overclock
    print("Overclocking...")
    #machine.freq(250000000)

    ### SIMPLE HELPER FUNCTIONS ###
    def sendtimhmsg(message:str) -> None:
        """Send a private message (diagnostic-like) to the HL-MCU (not something intended to be sent to the remote controller)."""
        ToSend = "TIMH" + message + "\r\n"
        uart.write(ToSend.encode())
    ########################

    async def ledflicker() -> None:
        """Continuously flick the onboard LED."""
        while True:
            led.on()
            await asyncio.sleep(0.25)
            led.off()
            await asyncio.sleep(0.25)

    async def comms_rx() -> None:
        """Handles receiving of any data from the HL MCU"""

        # declare nonlocal variables
        nonlocal uart # the interface with the HL-MCU, which the incoming data will be coming from
        nonlocal pitch_kp
        nonlocal pitch_ki
        nonlocal pitch_kd
        nonlocal roll_kp
        nonlocal roll_ki
        nonlocal roll_kd
        nonlocal yaw_kp
        nonlocal yaw_ki
        nonlocal yaw_kd
        nonlocal i_limit
        nonlocal throttle_uint16
        nonlocal pitch_int16
        nonlocal roll_int16
        nonlocal yaw_int16

        try:           

            while True:
                if uart.any() > 0: # if there is data available
                    data:bytes = tools.readuntil(uart, "\r\n".encode()) # read until \r\n at the end (newline, in bytes)... YES THIS IS BLOCKING
                    sendtimhmsg("Got " + str(len(data)) + " bytes")

                    # handle according to what it is
                    if data == "TIMHPING\r\n".encode(): # PING: simple check of life from the HL-MCU
                        sendtimhmsg("PONG")
                    elif data[0] & 0b00000001 == 0: # if the last bit is NOT occupied, it is a settings update
                        sendtimhmsg("It is a settings packet.")
                        settings:dict = tools.unpack_settings_update(data)
                        if settings != None: # it would return None if the checksum did not validate correctly
                            pitch_kp = settings["pitch_kp"]
                            pitch_ki = settings["pitch_ki"]
                            pitch_kd = settings["pitch_kd"]
                            roll_kp = settings["roll_kp"]
                            roll_ki = settings["roll_ki"]
                            roll_kd = settings["roll_kd"]
                            yaw_kp = settings["yaw_kp"]
                            yaw_ki = settings["yaw_ki"]
                            yaw_kd = settings["yaw_kd"]
                            i_limit = settings["i_limit"]
                            print("settings updated!")
                            sendtimhmsg("SETUP") # "SETUP" short for "Settings Updated"
                    elif data[0] & 0b00000001 != 0: # if the last bit IS occupied, it is a desired rates packet
                        sendtimhmsg("It is a DRates packet")
                        drates:dict = tools.unpack_desired_rates(data)
                        if drates != None: # it would return None if the checksum did not validate correcrtly
                            throttle_uint16 = drates["throttle_uint16"]
                            pitch_int16 = drates["pitch_int16"]
                            roll_int16 = drates["roll_int16"]
                            yaw_int16 = drates["yaw_int16"]
                            print("desired rates captured!")
                            sendtimhmsg("DRates set!")
                    else: # unknown packet
                        print("Unknown data received: " + str(data))
                
                # wait
                await asyncio.sleep(0.01) # 100 Hz max


        except Exception as ex: # if entire comms_rx coroutine failed
            throttle_uint16 = 0
            pitch_int16 = 0
            roll_int16 = 0
            yaw_int16 = 0
            sendtimhmsg("CommsRx Err: " + str(ex))

    async def status_tx() -> None:
        """Handles continuous sending of status data to HL MCU."""

        # do not need to declare nonlocal variables because we will only be READING from them, not writing. (nonlocal only required to write)

        while True:

            # pack status data
            data:bytes = tools.pack_status(m1_throttle, m2_throttle, m3_throttle, m4_throttle, pitch_rate, roll_rate, yaw_rate, pitch_angle, roll_angle)
            
            # send satus data to HL-MCU via UART
            uart.write(data + "\r\n".encode())

            # wait
            await asyncio.sleep(0.1) # 10 Hz

    async def flightcontrol() -> None:
        """Core flight controller routine."""
        pass

    # Run all threads!
    print("Running all coroutines, here we go!")
    task_led_flicker = asyncio.create_task(ledflicker())
    task_comms_rx = asyncio.create_task(comms_rx())
    task_status_tx = asyncio.create_task(status_tx())
    task_fc = asyncio.create_task(flightcontrol())
    await asyncio.gather(task_led_flicker, task_comms_rx, task_status_tx, task_fc)

asyncio.run(main())