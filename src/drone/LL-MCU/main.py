import machine
import time
import tools

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
throttle_uint16:int = 0        # from 0 to 65535, representing 0-100%
pitch_int16:int = 0            # from -32768 to 32767, representing -90.0 to 90.0 degrees/second
roll_int16:int = 0             # from -32768 to 32767, representing -90.0 to 90.0 degrees/second
yaw_int16:int = 0              # from -32768 to 32767, representing -90.0 to 90.0 degrees/second

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
   
# motor GPIO pins
gpio_motor1:int = 21 # front left, clockwise
gpio_motor2:int = 20 # front right, counter clockwise
gpio_motor3:int = 19 # rear left, counter clockwise
gpio_motor4:int = 18 # rear right, clockwise

# set up motor PWMs with frequency of 250 Hz and start at 0% throttle
M1:machine.PWM = machine.PWM(machine.Pin(gpio_motor1), freq=250, duty_u16=0)
M2:machine.PWM = machine.PWM(machine.Pin(gpio_motor2), freq=250, duty_u16=0)
M3:machine.PWM = machine.PWM(machine.Pin(gpio_motor3), freq=250, duty_u16=0)
M4:machine.PWM = machine.PWM(machine.Pin(gpio_motor4), freq=250, duty_u16=0)

# declare PID state variables
# declaring them here because their "previous state" (value from previous loop) must be referenced in each loop
pitch_last_i:float = 0.0
pitch_last_error:int = 0
roll_last_i:float = 0.0
roll_last_error:int = 0
yaw_last_i:float = 0.0
yaw_last_error:int = 0

# declare objects we will reuse in the loop instead of remaking each time
terminator:bytes = "\r\n".encode() # example \r\n for comparison sake later on (13, 10 in bytes)
status_packet:bytearray = bytearray([0,0,0,0,0,0,0,0,0,0,13,10]) # used to put status values into before sending to HL-MCU via UART. The status packet is 10 bytes worth of information, but making it 12 here with the \r\n at the end (13, 10) already appended so no need to append it manually later before sending!
gyro_data:bytearray = bytearray(6) # 6 bytes for reading the gyroscope reading directly from the MPU-6050 via I2C (instead of Python creating another 6-byte bytes object each time!)
rxBuffer:bytearray = bytearray() # a buffer of received messages from the HL-MCU, appended to byte by byte
desired_rates_data:list[int, int, int, int] = [0, 0, 0, 0] # desired rate packet data: throttle (uint16), pitch (int16), roll (int16), yaw (int16)

# calculate constant: cycle time, in microseconds (us)
cycle_time_us:int = 1000000 // 250 # 250 Hz. Should come out to 4,000 microseconds. The full PID loop must happen every 4,000 microseconds (4 ms) to achieve the 250 Hz loop speed.

# timestamps for tracking other processes that need to be done on a schedule
# originally was using asyncio for this but now resorting to timestamp-based
led_last_flickered_ticks_ms:int = 0 # the last time the onboard (pico) LED was swapped, in ms ticks
status_last_sent_ticks_ms:int = 0 # the last time the telemetry status was sent to the HL-MCU, in ms ticks

# Infinite loop for all operations!
while True:

    # mark loop start time
    loop_begin_us:int = time.ticks_us() # ticks, in microseconds (us)

    # is it time to flicker the onboard LED?
    if (time.ticks_ms() - led_last_flickered_ticks_ms) >= 250: # every 250 ms (4 times per second)
        led.toggle()
        led_last_flickered_ticks_ms = time.ticks_ms()

    # is it time to send status (telemetry) over UART to the HL-MCU?
    if (time.ticks_ms() - status_last_sent_ticks_ms) >= 100: # every 100 ms (10 times per second)
        tools.pack_status(m1_throttle, m2_throttle, m3_throttle, m4_throttle, pitch_rate, roll_rate, yaw_rate, pitch_angle, roll_angle, status_packet) # pack status data into the preexisting and reusable "status_packet" bytearray (update the values in that bytearray)
        uart.write(status_packet) # send it to HL-MCU via UART. we do not have to append \r\n because that is already at the end of the bytearray.
        status_last_sent_ticks_ms = time.ticks_ms()

    # check for received data (input data)
    # was originally planning to do this at only 50-100 hz, but doing this every loop to avoid build up
    try:           
        if uart.any() > 0:
            rxBuffer.extend(uart.read()) # read all available bytes and append to rxBuffer
            while terminator in rxBuffer: # if there is at least one terminator (\r\n) in the rxBuffer, process it!

                # get the line
                loc:int = rxBuffer.find(terminator) # find the \r\n
                ThisLine:bytes = rxBuffer[0:loc] # get the line, but without the \r\n terminator at the end
                rxBuffer = rxBuffer[loc+2:] # remove the line AND the terminator after it. Yes, this does create a whole new bytearray altogether, not good for performance. But can't think of another way.

                # handle according to what it is
                if ThisLine == "TIMHPING\r\n".encode(): # PING: simple check of life from the HL-MCU
                    sendtimhmsg("PONG")
                elif ThisLine[0] & 0b00000001 == 0: # if the last bit is NOT occupied, it is a settings update
                    sendtimhmsg("It is a settings packet.")
                    settings:dict = tools.unpack_settings_update(ThisLine)
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
                elif ThisLine[0] & 0b00000001 != 0: # if the last bit IS occupied, it is a desired rates packet
                    sendtimhmsg("It is a DRates packet")
                    if tools.unpack_desired_rates(ThisLine, desired_rates_data): # returns True if successfully, False if not
                        throttle_uint16 = desired_rates_data[0]
                        pitch_int16 = desired_rates_data[1]
                        roll_int16 = desired_rates_data[2]
                        yaw_int16 = desired_rates_data[3]
                        print("desired rates captured!")
                        sendtimhmsg("DRates set!")
                else: # unknown packet
                    print("Unknown data received: " + str(ThisLine))
    except Exception as ex:
        throttle_uint16 = 0
        pitch_int16 = 0
        roll_int16 = 0
        yaw_int16 = 0
        sendtimhmsg("CommsRx Err: " + str(ex))

    # Capture raw IMU data: gyroscope from MPU-6050
    i2c.readfrom_mem_into(0x68, 0x43, gyro_data) # read 6 bytes, 2 for each axis, into the "gyro_data" bytearray (update values in that bytearray to have to avoid creating a new bytes object)
    gyro_x = (gyro_data[0] << 8) | gyro_data[1]
    gyro_y = (gyro_data[2] << 8) | gyro_data[3]
    gyro_z = (gyro_data[4] << 8) | gyro_data[5]
    if gyro_x >= 32768: gyro_x = ((65535 - gyro_x) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    if gyro_y >= 32768: gyro_y = ((65535 - gyro_y) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    if gyro_z >= 32768: gyro_z = ((65535 - gyro_z) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    pitch_rate = gyro_x / 131 # now, divide by the scale factor to get the actual degrees per second
    roll_rate = gyro_y / 131 # now, divide by the scale factor to get the actual degrees per second
    yaw_rate = gyro_z / 131 # now, divide by the scale factor to get the actual degrees per second

    # conver the throttle input, as a uint16, into a percentage (between 0.0 and 1.0)
    desired_throttle:float = throttle_uint16 / 65535.0

    # convert the desired pitch, roll, and yaw into degrees per second
    desired_pitch_rate:float = pitch_int16 / 32767.0
    desired_roll_rate:float = roll_int16 / 32767.0
    desired_yaw_rate:float = yaw_int16 / 32767.0

    # now compare those ACTUAL rates with the DESIRED rates (calculate error)
    # error = desired - actual
    error_pitch_rate:int = desired_pitch_rate - pitch_rate
    error_roll_rate = desired_roll_rate - roll_rate
    error_yaw_rate = desired_yaw_rate - yaw_rate

    # Pitch PID calculation
    pitch_p:float = error_pitch_rate * pitch_kp
    pitch_i:float = pitch_last_i + (error_pitch_rate * pitch_ki * cycle_time_us)
    pitch_i = min(max(pitch_i, -i_limit), i_limit) # constrain within I limit
    pitch_d:float = pitch_kd * (error_pitch_rate - pitch_last_error) / cycle_time_us
    pitch_pid = pitch_p + pitch_i + pitch_d

    # Roll PID calculation
    roll_p:float = error_roll_rate * roll_kp
    roll_i:float = roll_last_i + (error_roll_rate * roll_ki * cycle_time_us)
    roll_i = min(max(roll_i, -i_limit), i_limit) # constrain within I limit
    roll_d:float = roll_kd * (error_roll_rate - roll_last_error) / cycle_time_us
    roll_pid = roll_p + roll_i + roll_d

    # Yaw PID calculation
    yaw_p:float = error_yaw_rate * yaw_kp
    yaw_i:float = yaw_last_i + (error_yaw_rate * yaw_ki * cycle_time_us)
    yaw_i = min(max(yaw_i, -i_limit), i_limit) # constrain within I limit
    yaw_d:float = yaw_kd * (error_yaw_rate - yaw_last_error) / cycle_time_us
    yaw_pid = yaw_p + yaw_i + yaw_d

    # calculate throttle values for each motor using those PID influences
    # we are using the nonlocal variables here so the status being sent will also update
    m1_throttle = desired_throttle + pitch_pid + roll_pid - yaw_pid
    m2_throttle = desired_throttle + pitch_pid - roll_pid + yaw_pid
    m3_throttle = desired_throttle - pitch_pid + roll_pid + yaw_pid
    m4_throttle = desired_throttle - pitch_pid - roll_pid - yaw_pid

    # calculate what the duty time of each motor PWM should be, in nanoseconds (not to be confused with "us", microseconds!)
    m1_ns:int = 1000000 + int(1000000 * m1_throttle)
    m2_ns:int = 1000000 + int(1000000 * m2_throttle)
    m3_ns:int = 1000000 + int(1000000 * m3_throttle)
    m4_ns:int = 1000000 + int(1000000 * m4_throttle)

    # min/max those duty times
    # constrain to within 1 ms and 2 ms (1,000,000 nanoseconds and 2,000,000 nanoseconds)
    m1_ns = min(max(m1_ns, 1000000), 2000000)
    m2_ns = min(max(m2_ns, 1000000), 2000000)
    m3_ns = min(max(m3_ns, 1000000), 2000000)
    m4_ns = min(max(m4_ns, 1000000), 2000000)

    # adjust throttles on PWMs
    M1.duty_ns(m1_ns)
    M2.duty_ns(m2_ns)
    M3.duty_ns(m3_ns)
    M4.duty_ns(m4_ns)

    # save state values for next loop
    pitch_last_error = error_pitch_rate
    roll_last_error = error_roll_rate
    yaw_last_error = error_yaw_rate
    pitch_last_i = pitch_i
    roll_last_i = roll_i
    yaw_last_i = yaw_i

    # wait if there is excess time
    excess_us:int = cycle_time_us - (time.ticks_us() - loop_begin_us) # calculate how much excess time we have to kill until it is time for the next loop
    if excess_us > 0:
        time.sleep_us(excess_us)