print("----- CENTAURI LOW-LEVEL MCU -----")
print("gitub.com/TimHanewich/centauri")
print()

import machine
import time
import tools
import math

# First thing is first: set up onboard LED, turn it on while loading
print("Turning LED on...")
led = machine.Pin("LED", machine.Pin.OUT)
led.on()

####################
##### SETTINGS #####
####################

target_hz:int = 250 # the number of times to run the PID loop, per second
alpha:float = 98 # complementary filter alpha value for pitch/roll angle estimation. higher values favor gyroscope's opinion, lower favors accelerometer (noisy) 
PID_SCALING_FACTOR:int = 1000 # PID scaling factor that will later be used to "divide down" the PID values. We do this so the PID gains can be in a much larger range and thus can be further fine tuned.

# Flight Control PID Gains
# Set initial setting here, though they can be updated via settings update packet later
pitch_kp:int = 5000
pitch_ki:int = 0
pitch_kd:int = 0
roll_kp:int = 5000
roll_ki:int = 0
roll_kd:int = 0
yaw_kp:int = 5000
yaw_ki:int = 0
yaw_kd:int = 0
i_limit:int = 0

####################
####################
####################

# set up UART interface with HL MCU
print("Establishing UART interface...")
uart = machine.UART(0, tx=machine.Pin(12), rx=machine.Pin(13), baudrate=115200)

# Declare helper function for sending private diagnostic message to HL-MCU
def sendtimhmsg(message:str) -> None:
    """Send a private message (diagnostic-like) to the HL-MCU (not something intended to be sent to the remote controller)."""
    ToSend = "TIMH" + message + "\r\n"
    uart.write(ToSend.encode())

# establish failure pattern
def FATAL_ERROR(error_msg:str = None) -> None:
    print("FATAL ERROR ENCOUNTERED!")
    while True:
        if error_msg != None:
            print("FATAL ERROR: " + error_msg)
            sendtimhmsg("FATERR: " + error_msg) # "FATERR" short for "Fatal Error"
        led.toggle()
        time.sleep(1.0)

# Send booting message over UART
print("Sending BOOTING message over UART...")
sendtimhmsg("BOOTING") # send a single "BOOTING" message to confirm we are booting

# Confirm MPU-6050 is connected via I2C
print("Setting up I2C...")
i2c = machine.I2C(0, sda=machine.Pin(16), scl=machine.Pin(17))
if 0x68 not in i2c.scan():
    print("MPU-6050 not connected via I2C!")
    FATAL_ERROR("MPU-6050 not connected!")
else:
    print("MPU-6050 confirmed to be connected via I2C.")

# Confirm MPU-6050 is on and operational by reading the "whoami" register
print("Reading MPU-6050 WHOAMI register...")
whoami:int = i2c.readfrom_mem(0x68, 0x75, 1)[0]
if whoami == 0x68:
    print("MPU-6050 WHOAMI passed!")
    sendtimhmsg("IMU OK")
else:
    print("MPU-6050 WHOAMI Failed!")
    FATAL_ERROR("MPU6050 WHOAMI Fail")

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
    FATAL_ERROR("MPU6050 gyro range set failed.")
if i2c.readfrom_mem(0x68, 0x1C, 1)[0] == 0x00:
    print("MPU-6050 accelerometer full scale range confirmed to be set at 2g")
else:
    print("MPU-6050 accelerometer full scale range set failed!")
    FATAL_ERROR("MPU6050 accel range set failed!")
if i2c.readfrom_mem(0x68, 0x1A, 1)[0] == 0x05:
    print("MPU-6050 low pass filter confirmed to be at 10 Hz")
else:
    print("MPU-6050 low pass filter failed to set!")
    FATAL_ERROR("MPU6050 LPF set failed!")

# Send message to confirm IMU is all set up
sendtimhmsg("IMU SET")

# measure gyro to estimate bias
gxs:int = 0
gys:int = 0
gzs:int = 0
samples:int = 0
for i in range(3):
    print("Beginning gyro calibration in " + str(3 - i) + "... ")
    sendtimhmsg("GyroCal in " + str(3 - i))
    time.sleep(1.0)
sendtimhmsg("CalibGyro...")
print("Calibrating gyro...")
started_at_ticks_ms:int = time.ticks_ms()
while time.ticks_diff(time.ticks_ms(), started_at_ticks_ms) < 3000: # 3 seconds
    gyro_data:bytes = i2c.readfrom_mem(0x68, 0x43, 6) # read 6 bytes, 2 for each axis
    gyro_x = (gyro_data[0] << 8) | gyro_data[1]
    gyro_y = (gyro_data[2] << 8) | gyro_data[3]
    gyro_z = (gyro_data[4] << 8) | gyro_data[5]
    if gyro_x >= 32768: gyro_x = ((65535 - gyro_x) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    if gyro_y >= 32768: gyro_y = ((65535 - gyro_y) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    if gyro_z >= 32768: gyro_z = ((65535 - gyro_z) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    gyro_x = gyro_x * 1000 // 131 # now, divide by the scale factor to get the actual degrees per second. But multiply by 1,000 to work in larger units so we can do integer math.
    gyro_y = gyro_y * 1000 // 131 # now, divide by the scale factor to get the actual degrees per second. But multiply by 1,000 to work in larger units so we can do integer math.
    gyro_z = gyro_z * 1000 // 131 # now, divide by the scale factor to get the actual degrees per second. But multiply by 1,000 to work in larger units so we can do integer math.
    gxs = gxs + gyro_x
    gys = gys + gyro_y
    gzs = gzs + gyro_z
    samples = samples + 1
    time.sleep(0.01)

# calculate gyro bias
# the resulting gyro bias will be in degrees per second * 1000 (with no decimal). We do this instead of a floating point number because integer math is faster.
print(str(samples) + " gyro samples collected.")
gyro_bias_x:int = gxs // samples
gyro_bias_y:int = gys // samples
gyro_bias_z:int = gzs // samples
print("Gyro Bias: " + str(gyro_bias_x) + ", " + str(gyro_bias_y) + ", " + str(gyro_bias_z))
sendtimhmsg("GyroCalib OK")

# motor GPIO pins
gpio_motor1:int = 21 # front left, clockwise
gpio_motor2:int = 20 # front right, counter clockwise
gpio_motor3:int = 19 # rear left, counter clockwise
gpio_motor4:int = 18 # rear right, clockwise

# set up motor PWMs with frequency of 250 Hz and start at 0% throttle
M1:machine.PWM = machine.PWM(machine.Pin(gpio_motor1), freq=target_hz, duty_u16=0)
M2:machine.PWM = machine.PWM(machine.Pin(gpio_motor2), freq=target_hz, duty_u16=0)
M3:machine.PWM = machine.PWM(machine.Pin(gpio_motor3), freq=target_hz, duty_u16=0)
M4:machine.PWM = machine.PWM(machine.Pin(gpio_motor4), freq=target_hz, duty_u16=0)

# declare variables: desired rate inputs
# these will later be updated via incoming desired rate packets (over UART from HL-MCU)
throttle_uint16:int = 0        # from 0 to 65535, representing 0-100%
pitch_int16:int = 0            # from -32768 to 32767, representing -90.0 to 90.0 degrees/second
roll_int16:int = 0             # from -32768 to 32767, representing -90.0 to 90.0 degrees/second
yaw_int16:int = 0              # from -32768 to 32767, representing -90.0 to 90.0 degrees/second

# declare variables: status (actuals)
# these will later be sent to the HL-MCU via UART as regular status updates
m1_throttle:int = 0    # between 1,000,000 and 2,000,000 (nanoseconds)
m2_throttle:int = 0    # between 1,000,000 and 2,000,000 (nanoseconds)
m3_throttle:int = 0    # between 1,000,000 and 2,000,000 (nanoseconds)
m4_throttle:int = 0    # between 1,000,000 and 2,000,000 (nanoseconds)
pitch_rate:int = 0     # the actual pitch rate, in degrees per second * 1000 (i.e. 90,000 would be +90 degrees per second)
roll_rate:int = 0      # the actual roll rate, in degrees per second * 1000 (i.e. 90,000 would be +90 degrees per second)
yaw_rate:int = 0       # the actual yaw rate, in degrees per second * 1000 (i.e. 90,000 would be +90 degrees per second)
pitch_angle:int = 0    # the actual pitch angle, in degrees * 1000 (i.e. 14000 would be 14 degrees)
roll_angle:int = 0     # the actual pitch angle, in degrees * 1000 (i.e. 14000 would be 14 degrees)

# declare objects we will reuse in the loop instead of remaking each time (for efficiency)
cycle_time_us:int = 1000000 // target_hz # The amount of time, in microseconds, the full PID loop must happen within. 4,000 microseconds (4 ms) to achieve a 250 Hz loop speed for example.
status_packet:bytearray = bytearray([0,0,0,0,0,0,0,0,0,0,13,10]) # used to put status values into before sending to HL-MCU via UART. The status packet is 10 bytes worth of information, but making it 12 here with the \r\n at the end (13, 10) already appended so no need to append it manually later before sending!
gyro_data:bytearray = bytearray(6) # 6 bytes for reading the gyroscope reading directly from the MPU-6050 via I2C (instead of Python creating another 6-byte bytes object each time!)
accel_data:bytearray = bytearray(6) # 6 bytes to reading the accelerometer reading directly from the MPU-6050 via I2C
desired_rates_data:list[int] = [0, 0, 0, 0] # desired rate packet data: throttle (uint16), pitch (int16), roll (int16), yaw (int16)
TIMHPING:bytes = "TIMHPING\r\n".encode() # example TIMHPING\r\n for comparison sake later (so we don't have to keep encoding it and making a new bytes object later)

# declare uart conveyer read objects
rxBufferLen:int = 128
rxBuffer:bytearray = bytearray(rxBufferLen) # a buffer of received messages from the HL-MCU
write_idx:int = 0 # last write location into the rxBuffer
terminator:bytes = "\r\n".encode() # example \r\n for comparison sake later on (13, 10 in bytes)

# declare PID state variables
# declaring them here because their "previous state" (value from previous loop) must be referenced in each loop
pitch_last_i:int = 0
pitch_last_error:int = 0
roll_last_i:int = 0
roll_last_error:int = 0
yaw_last_i:int = 0
yaw_last_error:int = 0

# timestamps for tracking other processes that need to be done on a schedule
# originally was using asyncio for this but now resorting to timestamp-based
led_last_flickered_ticks_ms:int = 0 # the last time the onboard (pico) LED was swapped, in ms ticks
status_last_sent_ticks_ms:int = 0 # the last time the telemetry status was sent to the HL-MCU, in ms ticks
last_compfilt_ticks_us:int = 0 # the last time the complementary filter was used. This is used to know how much time has ELAPSED and thus calculate roughly how many degrees changed based on the degrees per second value from the gyros
drates_last_received_ticks_ms:int = 0 # timestamp (in ms) of the last time a valid desired rates packet was received. This is used to check and shut down motors if it has been too long (failsafe)

# Infinite loop for all operations!
print("Now entering infinite operating loop!")
sendtimhmsg("READY")
try:
    while True:

        # mark loop start time
        loop_begin_us:int = time.ticks_us() # ticks, in microseconds (us)

        # is it time to flicker the onboard LED?
        if time.ticks_diff(time.ticks_ms(), led_last_flickered_ticks_ms) >= 250: # every 250 ms (4 times per second)
            led.toggle()
            led_last_flickered_ticks_ms = time.ticks_ms()

        # is it time to send status (telemetry) over UART to the HL-MCU?
        if time.ticks_diff(time.ticks_ms(), status_last_sent_ticks_ms) >= 100: # every 100 ms (10 times per second)
            tools.pack_status(m1_throttle, m2_throttle, m3_throttle, m4_throttle, pitch_rate, roll_rate, yaw_rate, pitch_angle, roll_angle, status_packet) # pack status data into the preexisting and reusable "status_packet" bytearray (update the values in that bytearray)
            uart.write(status_packet) # send it to HL-MCU via UART. we do not have to append \r\n because that is already at the end of the bytearray.
            status_last_sent_ticks_ms = time.ticks_ms()

        # check for received data (input data)
        # was originally planning to do this at only 50-100 hz, but doing this every loop to avoid build up
        try:  

            # This uses a rather complicated "conveyer belt" approach
            # I know it is complex, but we do this to avoid constantly uart.read() which creates a new bytes. Slow and memory leak.
            # So we want to uart.readinto() which requires an rxBuffer, which requires all of this:

            # Step 1: Read Data
            BytesAvailable:int = uart.any()
            if BytesAvailable > 0:
                available_space:int = rxBufferLen - write_idx # calculate how many bytes we have remaining in the buffer
                if available_space > 0:
                    target_write_window = memoryview(rxBuffer)[write_idx:write_idx + BytesAvailable] # create a memoryview pointer target to the area of the rxBuffer we want to write to with these new bytes
                    bytes_read:int = uart.readinto(target_write_window, BytesAvailable) # read directly into that target window, but specify the number of bytes. Specifying exactly how many bytes to read into drastically improves performance. From like 3,000 microseconds to like 70 (unless the window you want to read into fits the bytes available, which we do here, but adding number of bytes just to be sure)
                    write_idx = write_idx + bytes_read # increment the write location forward
                else:
                    write_idx = 0 # if there is no space, reset the write location for next time around 

            # Step 2: Process Lines
            search_from:int = 0
            while True:

                # find terminator
                loc = rxBuffer.find(terminator, search_from, write_idx) # search for a terminator somewhere in the new data
                if loc == -1:
                    break
                
                # Get line
                ThisLine = memoryview(rxBuffer)[search_from:write_idx]

                # handle according to what it is
                # check first for a desired rates packet as that is the most common thing that will come accross anyway so no need to waste time checking other things first when in the important tight pid loop
                if ThisLine[0] & 0b00000001 != 0: # if the last bit IS occupied, it is a desired rates packet.
                    if tools.unpack_desired_rates(ThisLine, desired_rates_data): # returns True if successfully, False if not

                        # set the input values based on what was placed in the desired_rates_data list
                        throttle_uint16 = desired_rates_data[0]
                        pitch_int16 = desired_rates_data[1]
                        roll_int16 = desired_rates_data[2]
                        yaw_int16 = desired_rates_data[3]

                        # update the last time we have received drates
                        drates_last_received_ticks_ms = time.ticks_ms()

                        # FOR DIAGNOSTIC / TESTING, UNCOMMENT THIS
                        # You can set hijack and desired values below to test PID values / motor throttles according to different conditions
                        # throttle_uint16 = 32767
                        # pitch_int16 = 0
                        # roll_int16 = 0
                        # yaw_int16 = 0

                elif ThisLine == TIMHPING: # PING: simple check of life from the HL-MCU
                    sendtimhmsg("PONG") # respond with PONG, the expected response to confirm we are operating
                elif ThisLine[0] & 0b00000001 == 0: # if the last bit is NOT occupied, it is a settings update
                    sendtimhmsg("It is a settings packet.")
                    settings:dict = tools.unpack_settings_update(ThisLine) # this is quite bad performance wise. Making a new dict each time is memory intensive. However, leaving it for now because really this should happen infrequently... and while not in flight anyway, so its not a big deal.
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
                    else:
                        sendtimhmsg("SETUP FAIL") # short for "Settings Update Failed" to say it failed to indicate the settings were NOT written.
                else: # unknown packet
                    print("Unknown data received: " + str(ThisLine))
                    sendtimhmsg("?") # respond with a simple question mark to indicate the message was not understood.

                # increment search start location... there is possibly another \r\n in there (and thus a new line to process)
                search_from = loc + 2 # +2 to jump after \r\n

            # Step 3: move the conveyer belt
            # the conveyer belt will only be moved if not every byte was processed and thus we are done with
            if search_from > 0: # if search_from was moved, that means at least one line was extracted and processed.
                unprocessed_byte_count:int = write_idx - search_from # how many bytes are on the conveyer and still unprocessed
                if unprocessed_byte_count > 0:
                    rxBuffer[0:unprocessed_byte_count] = rxBuffer[search_from:write_idx]
                write_idx = unprocessed_byte_count


        except Exception as ex:
            throttle_uint16 = 0
            pitch_int16 = 0
            roll_int16 = 0
            yaw_int16 = 0
            sendtimhmsg("CommsRx Err: " + str(ex))

        # Capture RAW IMU data: both gyroscope and accelerometer
        # Goal here is ONLY to capture the data, not to transform it
        GoodRead:bool = False
        imu_read_attemp_started_ticks_ms:int = time.ticks_ms()
        while not GoodRead:
            try:
                i2c.readfrom_mem_into(0x68, 0x43, gyro_data) # read 6 bytes, 2 for each axis, into the "gyro_data" bytearray (update values in that bytearray to have to avoid creating a new bytes object)
                i2c.readfrom_mem_into(0x68, 0x3B, accel_data) # read 6 bytes, two for each axis for accelerometer data, directly into the "accel_data" bytearray
                GoodRead = True
            except:
                GoodRead = False # mark it as a bad read
                if time.ticks_diff(time.ticks_ms(), imu_read_attemp_started_ticks_ms) > 1000: # if it has been over a full second and we STILL haven't been able to get an IMU reading...
                    
                    # turn off all motors!!!!!!!
                    # 1,000,000 nanoseconds = 0% throttle
                    M1.duty_ns(1000000)
                    M2.duty_ns(1000000)
                    M3.duty_ns(1000000)
                    M4.duty_ns(1000000)

                    # fatal fail!
                    FATAL_ERROR("IMU Read Error: read failed")

        # Process & Transform raw Gyroscope data
        gyro_x = (gyro_data[0] << 8) | gyro_data[1]
        gyro_y = (gyro_data[2] << 8) | gyro_data[3]
        gyro_z = (gyro_data[4] << 8) | gyro_data[5]
        if gyro_x >= 32768: gyro_x = ((65535 - gyro_x) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        if gyro_y >= 32768: gyro_y = ((65535 - gyro_y) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        if gyro_z >= 32768: gyro_z = ((65535 - gyro_z) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        roll_rate = gyro_x * 1000 // 131 # now, divide by the scale factor to get the actual degrees per second. But multiply by 1,000 to work in larger units so we can do integer math.
        pitch_rate = gyro_y * 1000 // 131 # now, divide by the scale factor to get the actual degrees per second. But multiply by 1,000 to work in larger units so we can do integer math.
        yaw_rate = gyro_z * 1000 // 131 # now, divide by the scale factor to get the actual degrees per second. But multiply by 1,000 to work in larger units so we can do integer math.

        # subtract out (account for) gyro bias that was calculated during calibration phase
        pitch_rate = pitch_rate - gyro_bias_y
        roll_rate = roll_rate - gyro_bias_x
        yaw_rate = yaw_rate - gyro_bias_z

        # FOR DIAGNOSTICS / TESTING: 
        # You can manually hijack the pitch, roll, and yaw rate below.
        # uncomment these and set a value to observe the PID values / motor throttles adjust.
        # pitch_rate = 0
        # roll_rate = 0
        # yaw_rate = 0

        # Process & Transform raw accelerometer data
        accel_x = (accel_data[0] << 8) | accel_data[1]
        accel_y = (accel_data[2] << 8) | accel_data[3]
        accel_z = (accel_data[4] << 8) | accel_data[5]
        if accel_x >= 32658: accel_x = ((65535 - accel_x) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        if accel_y >= 32658: accel_y = ((65535 - accel_y) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        if accel_z >= 32658: accel_z = ((65535 - accel_z) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        accel_x = (accel_x * 1000) // 16384 # divide by scale factor for 2g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)
        accel_y = (accel_y * 1000) // 16384 # divide by scale factor for 2g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)
        accel_z = (accel_z * 1000) // 16384 # divide by scale factor for 2g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)

        # use ONLY the accelerometer data to estimate pitch and roll
        # you can interpret this as the accelerometer's "opinion" of what pitch and roll angle is based on only its data
        # this will likely be inaccurate as the accelerometer is quite susceptible to vibrations
        # we will later "fuse" this with gyro input in the complementary filter
        # note: the pitch and roll calculated here will be in degrees * 1000. For example, a reading of 22435 can be interpreted as 22.435 degrees (we do this for integer math purposes)
        expected_pitch_angle_accel:int = int(math.atan2(accel_x, math.sqrt(accel_y**2 + accel_z**2)) * 180000 / math.pi) # the accelerometers opinion of what the pitch angle is
        expected_roll_angle_accel:int = int(math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2)) * 180000 / math.pi) # the accelerometers opinion of what the roll angle is

        # calculate what the gyro's expected pitch and roll angle should be
        # you can take this as the gyro's "opinion" of what the pitch and roll angle should be, just on its data
        elapsed_us:int = time.ticks_diff(time.ticks_us(), last_compfilt_ticks_us) # the amount of time, in microseconds (us), that has elapsed since we did this in the last loop
        last_compfilt_ticks_us = time.ticks_us() # update the time
        expected_pitch_angle_gyro:int = pitch_angle + (pitch_rate * elapsed_us // 1000000)
        expected_roll_angle_gyro:int = roll_angle + (roll_rate * elapsed_us // 1000000)

        # Now use a complementary filter to determine angle (fuse gyro + accelerometer data)
        pitch_angle = ((expected_pitch_angle_gyro * alpha) + (expected_pitch_angle_accel * (100 - alpha))) // 100
        roll_angle = ((expected_roll_angle_gyro * alpha) + (expected_roll_angle_accel * (100 - alpha))) // 100

        # convert desired throttle, expressed as a uint16, into nanoseconds
        desired_throttle:int = 1000000 + (throttle_uint16 * 1000000) // 65535

        # convert the desired pitch, roll, and yaw into degrees per second
        # Multiply by 90,000 because each are expressed as an int16 for a range of -90 to +90
        # but multiply it all by 1,000 (not 90) so we can do integer math
        desired_pitch_rate:int = (pitch_int16 * 90000) // 32767
        desired_roll_rate:int = (roll_int16 * 90000) // 32767
        desired_yaw_rate:int = (yaw_int16 * 90000) // 32767

        # now compare those ACTUAL rates with the DESIRED rates (calculate error)
        # error = desired - actual
        error_pitch_rate:int = desired_pitch_rate - pitch_rate
        error_roll_rate:int = desired_roll_rate - roll_rate
        error_yaw_rate:int = desired_yaw_rate - yaw_rate
        #print("ErrPitch: " + str(error_pitch_rate) + ", ErrRoll: " + str(error_roll_rate) + ", ErrYaw: " + str(error_yaw_rate))

        # Pitch PID calculation
        pitch_p:int = (error_pitch_rate * pitch_kp) // PID_SCALING_FACTOR
        pitch_i:int = pitch_last_i + ((error_pitch_rate * pitch_ki * cycle_time_us) // PID_SCALING_FACTOR)
        pitch_i = min(max(pitch_i, -i_limit), i_limit) # constrain within I limit
        pitch_d = (pitch_kd * (error_pitch_rate - pitch_last_error)) // (cycle_time_us * PID_SCALING_FACTOR) # would make more visual sense to divide the entire thing by the scaling factor, but for precision purposes, better to only integer divide ONCE by one big number than do it twice.
        pitch_pid = pitch_p + pitch_i + pitch_d

        # Roll PID calculation
        roll_p:int = (error_roll_rate * roll_kp) // PID_SCALING_FACTOR
        roll_i:int = roll_last_i + ((error_roll_rate * roll_ki * cycle_time_us) // PID_SCALING_FACTOR)
        roll_i = min(max(roll_i, -i_limit), i_limit) # constrain within I limit
        roll_d = (roll_kd * (error_roll_rate - roll_last_error)) // (cycle_time_us * PID_SCALING_FACTOR) # would make more visual sense to divide the entire thing by the scaling factor, but for precision purposes, better to only integer divide ONCE by one big number than do it twice.
        roll_pid = roll_p + roll_i + roll_d

        # Yaw PID calculation
        yaw_p:int = (error_yaw_rate * yaw_kp) // PID_SCALING_FACTOR
        yaw_i:int = yaw_last_i + ((error_yaw_rate * yaw_ki * cycle_time_us) // PID_SCALING_FACTOR)
        yaw_i = min(max(yaw_i, -i_limit), i_limit) # constrain within I limit
        yaw_d = (yaw_kd * (error_yaw_rate - yaw_last_error)) // (cycle_time_us * PID_SCALING_FACTOR) # would make more visual sense to divide the entire thing by the scaling factor, but for precision purposes, better to only integer divide ONCE by one big number than do it twice.
        yaw_pid = yaw_p + yaw_i + yaw_d

        # calculate throttle values for each motor using those PID influences
        #print("Pitch PID: " + str(pitch_pid) + ", Roll PID: " + str(roll_pid) + ", Yaw Pid: " + str(yaw_pid))
        m1_throttle = desired_throttle - pitch_pid + roll_pid + yaw_pid
        m2_throttle = desired_throttle - pitch_pid - roll_pid - yaw_pid
        m3_throttle = desired_throttle + pitch_pid + roll_pid - yaw_pid
        m4_throttle = desired_throttle + pitch_pid - roll_pid + yaw_pid

        # min/max those duty times
        # constrain to within 1 ms and 2 ms (1,000,000 nanoseconds and 2,000,000 nanoseconds)
        m1_throttle = min(max(m1_throttle, 1000000), 2000000)
        m2_throttle = min(max(m2_throttle, 1000000), 2000000)
        m3_throttle = min(max(m3_throttle, 1000000), 2000000)
        m4_throttle = min(max(m4_throttle, 1000000), 2000000)
        #print(str(time.ticks_ms()) + ": M1: " + str(m1_throttle) + ", M2: " + str(m2_throttle) + ", M3: " + str(m3_throttle) + ", M4: " + str(m4_throttle))

        # MOTOR SHUTDOWN CONDITIONS (safety)
        # there are two conditions that would mean, no matter what happened above, ALL FOUR motors should be shut down (0% throttle)
        # scenario 1: desired throttle is 0%. This is obvious. If throttle is 0%, no motors should move. But, the PID loop is still running so it will still be trying to compensate for rate errors, meaning a motor could go OVER 0% throttle.
        # scenario 2: it has been a long time since we received a valid desired rates packet. This could be due to an error or something with the controller not sending data or the HL-MCU not sending data... but if this happens, as a failsafe, turn off all motors to prevent them from being stuck on.
        if desired_throttle == 1000000 or time.ticks_diff(time.ticks_ms(), drates_last_received_ticks_ms) > 2000: # if we havne't received valid drate data in more than 2 seconds
            
            # shut off all motors
            # 1,000,000 nanoseconds = 1 ms, the minumum throttle for an ESC (0% throttle, so no rotation)
            m1_throttle = 1000000
            m2_throttle = 1000000
            m3_throttle = 1000000
            m4_throttle = 1000000

            # reset cumulative PID values (I and D related)
            pitch_last_i = 0
            roll_last_i = 0
            yaw_last_i = 0
            pitch_last_error = 0
            roll_last_error = 0
            yaw_last_error = 0

        # adjust throttles on PWMs
        M1.duty_ns(m1_throttle)
        M2.duty_ns(m2_throttle)
        M3.duty_ns(m3_throttle)
        M4.duty_ns(m4_throttle)

        # save state values for next loop
        pitch_last_error = error_pitch_rate
        roll_last_error = error_roll_rate
        yaw_last_error = error_yaw_rate
        pitch_last_i = pitch_i
        roll_last_i = roll_i
        yaw_last_i = yaw_i

        # wait if there is excess time 
        excess_us:int = cycle_time_us - time.ticks_diff(time.ticks_us(), loop_begin_us) # calculate how much excess time we have to kill until it is time for the next loop
        #print("Excess us: " + str(excess_us))
        if excess_us > 0:
            time.sleep_us(excess_us)
            
except Exception as ex: # unhandled error somewhere in the loop

    # turn off all motors!!!!!!!
    # 1,000,000 nanoseconds = 0% throttle
    M1.duty_ns(1000000)
    M2.duty_ns(1000000)
    M3.duty_ns(1000000)
    M4.duty_ns(1000000)

    # fail!
    FATAL_ERROR("IN-LOOP ERROR: " + str(ex))