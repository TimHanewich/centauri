print("----- CENTAURI FLIGHT CONTROLLER -----")
print("github.com/TimHanewich/centauri")
print()

import machine

# First thing is first: set up onboard LED, turn it on while loading
print("Turning LED on...")
led = machine.Pin("LED", machine.Pin.OUT)
led.on()

# right away, set up motor PWMs with frequency of 250 Hz and start at 0% throttle (yes, 1,000,000 ns is 0% throttle)
# why do this right away? Some ESCs have a timeout that will refuse to turn on if the PWM signal is not received within a certain number of seconds of powering on
gpio_motor1:int = 21 # front left, clockwise
gpio_motor2:int = 20 # front right, counter clockwise
gpio_motor3:int = 19 # rear left, counter clockwise
gpio_motor4:int = 18 # rear right, clockwise
target_hz:int = 250 # the number of times to run the PID loop, per second. IMPORTANT: if you change this, you will also need to change the time-sensitive PID gains (integral and derivative). I did not build a time-scaling mechanism into those calculations.
M1:machine.PWM = machine.PWM(machine.Pin(gpio_motor1), freq=target_hz, duty_ns=1000000)
M2:machine.PWM = machine.PWM(machine.Pin(gpio_motor2), freq=target_hz, duty_ns=1000000)
M3:machine.PWM = machine.PWM(machine.Pin(gpio_motor3), freq=target_hz, duty_ns=1000000)
M4:machine.PWM = machine.PWM(machine.Pin(gpio_motor4), freq=target_hz, duty_ns=1000000)

print("Importing other libraries...")
import time
import math
import tools

####################
##### SETTINGS #####
####################

alpha:float = 98 # complementary filter alpha value for pitch/roll angle estimation. higher values favor gyroscope's opinion, lower favors accelerometer (noisy) 
PID_SCALING_FACTOR:int = 10000 # PID scaling factor that will later be used to "divide down" the PID values. We do this so the PID gains can be in a much larger range and thus can be further fine tuned.

# Flight Control PID Gains
# Set initial setting here to 0 for safety reasons, though they can be updated via settings update packet later
pitch_kp:int = 0
pitch_ki:int = 0
pitch_kd:int = 0
roll_kp:int = 0
roll_ki:int = 0
roll_kd:int = 0
yaw_kp:int = 0
yaw_ki:int = 0
yaw_kd:int = 0
i_limit:int = 0

####################
####################
####################

# establish failure pattern
def FATAL_ERROR(error_msg:str = None) -> None:
    print("FATAL ERROR ENCOUNTERED!")
    while True:
        if error_msg != None:
            print("FATAL ERROR: " + error_msg)
        led.toggle()
        time.sleep(1.0)

# Print header: HC-12 setup
print()
print("HC-12 SETUP")

# set up UART interface for radio communications via HC-12
print("Setting up HC-12 via UART...")
hc12_set = machine.Pin(7, machine.Pin.OUT) # the SET pin, used for going into and out of AT mode
uart_hc12 = machine.UART(1, tx=machine.Pin(8), rx=machine.Pin(9), baudrate=9600)
uart_hc12.read(uart_hc12.any()) # clear out any RX buffer that may exist

# pulse HC-12
hc12_set.low() # pull it LOW to enter AT command mode
time.sleep(0.2) # wait a moment for AT mode to be entered
hc12_pulsed:bool = False
hc12_pulse_attempts:int = 0
hc12_pulse_rx_buffer:bytearray = bytearray()
while hc12_pulsed == False and hc12_pulse_attempts < 3:
    print("Sending pulse attempt # " + str(hc12_pulse_attempts + 1) + "...")
    uart_hc12.write("AT\r\n".encode()) # send AT command
    hc12_pulse_attempts = hc12_pulse_attempts + 1
    time.sleep(0.2) # wait a moment for it to be responded to

    # if there is data
    if uart_hc12.any():
        hc12_pulse_rx_buffer.extend(uart_hc12.read(uart_hc12.any())) # append
        if "OK\r\n".encode() in hc12_pulse_rx_buffer:
            hc12_pulsed = True
            print("Pulse received!")
            break
        else:
            print("Data received back from HC-12 but it wasn't an OK (pulse)")
    else:
        print("No data received from HC-12.")

    # wait
    time.sleep(1.0)

# handle results of HC-12 pulse attempt
if hc12_pulsed:
    print("HC-12 pulsed! It is connected and working properly.")
else:
    print("HC-12 did not pulse back! Ensure it is connected, in baudrate 9600 mode, and working properly.")
    FATAL_ERROR()

# Configure HC-12 while still in AT mode: mode = FU3
print("Setting HC-12 mode to FU3...")
uart_hc12.write("AT+FU3\r\n".encode()) # go into mode FU3 (normal mode)
time.sleep(0.2) # wait a moment
response:bytes = uart_hc12.read(uart_hc12.any())
if "OK+FU3\r\n".encode() in response:
    print("HC-12 in FU3 mode successful!")
else:
    print("HC-12 not confirmed to be in HC-12 mode!")
    FATAL_ERROR()

# Configure HC-12 while still in AT mode: channel = 2
print("Setting HC-12 channel to 2...")
uart_hc12.write("AT+C002\r\n".encode())
time.sleep(0.2) # wait a moment
response:bytes = uart_hc12.read(uart_hc12.any())
if "OK+C002\r\n".encode() in response:
    print("HC-12 set to channel 2!")
else:
    print("HC-12 not confirmed to be in channel 2.")
    FATAL_ERROR()

# Configure HC-12 while still in AT mode: power
print("Setting HC-12 power to maximum level of 8...")
uart_hc12.write("AT+P8\r\n".encode())
time.sleep(0.2) # wait a moment
response:bytes = uart_hc12.read(uart_hc12.any())
if "OK+P8\r\n".encode() in response:
    print("HC-12 power set to level 8 (20 dBM)")
else:
    print("Unsuccessful in setting HC-12 power level to 8.")
    FATAL_ERROR()

# now that the HC-12 is set up and configured, close out of AT mode by setting the SET pin back to HIGH
print("Returning HC-12 SET pin to HIGH (exiting AT mode)...")
hc12_set.high()
time.sleep(0.5) # wait a moment for the HC-12 to successfully get out of AT mode before proceeding with sending any messages

# define special message packet function for sending special packets (prepend with "TIMH")
print("Defining special message function...")
def send_special(msg:str) -> None:
    ToSend:bytearray = bytearray()
    ToSend.append(0b00000001) # append header byte with bit 0 = 1 to identify it as a special packet
    if len(msg) > 50:
        msg = msg[0:50] # limit to 50 chars
    ToSend.extend(msg.encode())
    ToSend.extend("\r\n".encode()) # terminator
    uart_hc12.write(ToSend)

# send online notification
print("Sending 'HC12 OK' message...")
send_special("HC12 OK")

## Print header: MPU-6050 setup
print()
print("MPU-6050 SETUP")

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
    send_special("IMU OK")
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
send_special("IMU SET")

## print header: Gyro calibration
print()
print("GYRO CALIBRATION")

# measure gyro to estimate bias
gxs:int = 0
gys:int = 0
gzs:int = 0
samples:int = 0
for i in range(3):
    print("Beginning gyro calibration in " + str(3 - i) + "... ")
    #endtimhmsg("GyroCal in " + str(3 - i))
    time.sleep(1.0)
send_special("Gyro Cal...")
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
send_special("Calib Gyro OK")



# set up ADC for reading the battery voltage
vbat_adc = machine.ADC(machine.Pin(26))

# Set up telemetry variables that will be used to store and then send status to remote controller
vbat:int = 0         # battery voltage between 6.0 and 16.8 volts, but expressed as an integer between 60 and 168 (pretend decimal point just before last digit. We do this so integer division can be used).
pitch_rate:int = 0   # pitch rate, multiplied by 1,000. So, for example, 3543 would be 3.543 degrees per second.
roll_rate:int = 0    # roll rate, multiplied by 1,000. So, for example, 3543 would be 3.543 degrees per second.
yaw_rate:int = 0     # yaw rate, multiplied by 1,000. So, for example, 3543 would be 3.543 degrees per second.
pitch_angle:int = 0  # pitch angle, multiplied by 1,000. So, for example, 3543 would be 3.543.
roll_angle:int = 0   # roll angle, multiplied by 1,000. So, for example, 3543 would be 3.543.

# declare objects we will reuse in the loop instead of remaking each time (for efficiency)
cycle_time_us:int = 1000000 // target_hz # The amount of time, in microseconds, the full PID loop must happen within. 4,000 microseconds (4 ms) to achieve a 250 Hz loop speed for example.
gyro_data:bytearray = bytearray(6) # 6 bytes for reading the gyroscope reading directly from the MPU-6050 via I2C (instead of Python creating another 6-byte bytes object each time!)
accel_data:bytearray = bytearray(6) # 6 bytes to reading the accelerometer reading directly from the MPU-6050 via I2C
control_input:list[int] = [0,0,0,0] # array that we will unpack control input into (throttle input, pitch input, roll input, yaw input) - throttle as uint16, the rest as int16
telemetry_packet:bytearray = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\r\n') # array that we will repopulate with updated telemetry data (i.e. battery level, pitch rate, etc.). We set it up with 9 bytes: 1 for the header, 6 for the data, two for the \r\n terminator (so we don't have to keep appending \r\n at the end and causing more overhead in the loop)
TIMHPING:bytes = "TIMHPING\r\n".encode() # example TIMHPING\r\n for comparison sake later (so we don't have to keep encoding it and making a new bytes object later)

# declare variables: desired rate inputs
# these will later be updated via incoming desired rate packets (over UART from HL-MCU)
input_throttle_uint16:int = 0        # from 0 to 65535, representing 0-100%
input_pitch_int16:int = 0            # from -32768 to 32767, later interpreted to -90.0 to 90.0 degrees/second
input_roll_int16:int = 0             # from -32768 to 32767, later interpreted to -90.0 to 90.0 degrees/second
input_yaw_int16:int = 0              # from -32768 to 32767, later interpreted to -90.0 to 90.0 degrees/second

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
status_last_sent_ticks_ms:int = 0 # the last time the telemetry status was sent to the remote controller via HC-12
last_compfilt_ticks_us:int = 0 # the last time the complementary filter was used. This is used to know how much time has ELAPSED and thus calculate roughly how many degrees changed based on the degrees per second value from the gyros
control_input_last_received_ticks_ms:int = 0 # timestamp (in ms) of the last time a valid control packet was received. This is used to check and shut down motors if it has been too long (failsafe)
LAST_PRINT:int = 0

# Infinite loop for all operations!
print()
print("Now entering infinite operating loop!")
send_special("READY")
try:
    while True:

        # mark loop start time
        loop_begin_us:int = time.ticks_us() # ticks, in microseconds (us)

        # is it time to flicker the onboard LED?
        if time.ticks_diff(time.ticks_ms(), led_last_flickered_ticks_ms) >= 250: # every 250 ms (4 times per second)
            led.toggle()
            led_last_flickered_ticks_ms = time.ticks_ms()

        # is it time to send status (telemetry) over to the remote controller via the HC-12?
        # but ONLY send data if we are NOT armed. While throttle input > 0, we are armed and in flight mode, so more important to divert full HC-12 attention to receiving inputs
        # We do this because the HC-12 is half duplex, meaning it can only receive or send at one time
        # attempting to send while receiving means good chance a packet will be missed
        if input_throttle_uint16 == 0:
            if time.ticks_diff(time.ticks_ms(), status_last_sent_ticks_ms) >= 1000: # every 1000 ms (1 time per second)

                # first, get a ADC reading
                vbat_u16:int = vbat_adc.read_u16() # read the value on the ADC pin, as a uint16 (0-65535)

                # convert the battery ADC reading to a voltage reading
                # I know the function below looks weird! But let me explain it a bit.
                # This is a condensed calculation of a several small calculations.
                # The u16 reading from the ADC pin is basically 0-65535, with that value being mapped to a voltage 0-3.3v
                # We want to calculate what voltage it corresponds to, and then scale that back to the est. voltage of the BATTERY PACK via the inverse of the voltage divider
                # the voltage divider we use here is cutting the voltage down to 18.04% of the voltage, so we divide by 0.1804 (roughly) to get back to that voltage
                # however, that whole calculation above would involve floating point math, which we are trying to avoid for performance purposes.
                # So instead, we consolidate all multiplication and divison into a single line, like this. 
                # BUT, instead of multiplying by 3.3 (would be floating point math), I am bumpping it up to 33 to avoid integer math
                # so, that would mean the vbat calculated here is an integer, but is 10x more than it actually is
                # so, for example, a vbat here of 65 means the battery voltage is 6.5 volts. Or a vbat of 122 is a battery voltage of 12.2 volts.
                # And how did we get to the denominator, 11820? 
                # We wanted to divide by 65535 to turn the ADC reading into a % anyway
                # and then have to divide the whole thing again by 0.1804 to get back to a battery pack voltage
                # combining them both together and rounding to an integer, that is the same as just dividing by 11820!
                # note: we are not multiplying the denominator by 10 as well (like we did for the numerator) because we WANT the output result to be 10x higher, so that was it is like 65 and not 6.5.
                vbat = (vbat_u16 * 33) // 11820
                
                # pack and send
                tools.pack_telemetry(vbat, pitch_rate // 1000, roll_rate // 1000, yaw_rate // 1000, pitch_angle // 1000, roll_angle // 1000, telemetry_packet) # we divide by 1000 (integer division) to reduce back to a single unit (each is stored 1000x the actual to allow for integer math instead of floating point math)
                uart_hc12.write(telemetry_packet) # no need to append \r\n to it because the bytearray packet already has it at the end!
                status_last_sent_ticks_ms = time.ticks_ms() # update last sent time

        # check for received data (input data) from the HC-12
        # the data that we receive from the HC-12 could be:
        # 1 - control data
        # 2 - Settings update data (PID settings)
        # 3 - PING
        try:  

            # This uses a rather complicated "conveyer belt" approach
            # I know it is complex, but we do this to avoid constantly uart.read() which creates a new bytes. Slow and memory leak.
            # So we want to uart.readinto() which requires an rxBuffer, which requires all of this:

            # Step 1: Read Data
            BytesAvailable:int = uart_hc12.any()
            if BytesAvailable > 0:
                available_space:int = rxBufferLen - write_idx # calculate how many bytes we have remaining in the buffer
                BytesWeWillReadRightNow:int = min(BytesAvailable, available_space)
                if available_space > 0:
                    target_write_window = memoryview(rxBuffer)[write_idx:write_idx + BytesWeWillReadRightNow] # create a memoryview pointer target to the area of the rxBuffer we want to write to with these new bytes
                    bytes_read:int = uart_hc12.readinto(target_write_window, BytesWeWillReadRightNow) # read directly into that target window, but specify the number of bytes. Specifying exactly how many bytes to read into drastically improves performance. From like 3,000 microseconds to like 70 (unless the window you want to read into fits the bytes available, which we do here, but adding number of bytes just to be sure)
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
                # we must check if it is a TIMHPING first because the "T" byte has a 0 in bit 0, so it would think it is a control packet if we checked for that first!
                if ThisLine == TIMHPING: # PING: simple check of life
                    uart_hc12.write("TIMHPONG\r\n".encode()) # PONG back
                elif ThisLine[0] & 0b00000001 == 0: # if bit 0 is 0, it is a control packet
                    unpack_successful:bool = tools.unpack_control_packet(ThisLine, control_input)
                    if unpack_successful:
                        input_throttle_uint16 = control_input[0]
                        input_pitch_int16 = control_input[1]
                        input_roll_int16 = control_input[2]
                        input_yaw_int16 = control_input[3]
                        control_input_last_received_ticks_ms = time.ticks_ms() # mark that we just now got control input
                elif ThisLine[0] & 0b00000001 != 0: # if bit 0 is 1, it is a settings update
                    settings:dict = tools.unpack_settings_update(ThisLine)
                    if settings != None:
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
                        send_special("SETUPOK") # send special packet "SETUPOK", short for "Settings Update OK".
                    else:
                        print("It was settings but it failed.")
                else: # unknown packet
                    print("Unknown data received: " + str(ThisLine))
                    send_special("?") # respond with a simple question mark to indicate the message was not understood.

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
            input_throttle_uint16 = 0
            input_pitch_int16 = 0
            input_roll_int16 = 0
            input_yaw_int16 = 0
            send_special("CommsRx Err: " + str(ex))

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

        # Process & Transform raw accelerometer data
        accel_x = (accel_data[0] << 8) | accel_data[1]
        accel_y = (accel_data[2] << 8) | accel_data[3]
        accel_z = (accel_data[4] << 8) | accel_data[5]
        if accel_x >= 32768: accel_x = ((65535 - accel_x) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        if accel_y >= 32768: accel_y = ((65535 - accel_y) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        if accel_z >= 32768: accel_z = ((65535 - accel_z) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        accel_x = (accel_x * 1000) // 16384 # divide by scale factor for 2g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)
        accel_y = (accel_y * 1000) // 16384 # divide by scale factor for 2g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)
        accel_z = (accel_z * 1000) // 16384 # divide by scale factor for 2g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)

        # subtract out (account for) gyro bias that was calculated during calibration phase
        pitch_rate = pitch_rate - gyro_bias_y
        roll_rate = roll_rate - gyro_bias_x
        yaw_rate = yaw_rate - gyro_bias_z

        # Because of how I have my IMU mounted, invert necessary axes
        # I could in theory not need to do this if I mounted it flipped over, but preferring to leave it as is physically and just make the adjustment here!
        pitch_rate = pitch_rate * -1    # this ensures as the drone pitches down towards the ground, that is a NEGATIVE pitch rate. And a tile up would be positive
        yaw_rate = yaw_rate * -1        # this ensures the drone rotating towards the right is a POSITIVE yaw rate, with a left turn being negative

        # FOR DIAGNOSTICS / TESTING: 
        # You can manually hijack the pitch, roll, and yaw rate below.
        # uncomment these and set a value to observe the PID values / motor throttles adjust.
        # pitch_rate = 0
        # roll_rate = 0
        # yaw_rate = 0
        
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

        # convert the desired pitch, roll, and yaw from (-32,768 to 32,767) into (-90 to +90) degrees per second
        # Multiply by 90,000 because we will interpret each as -90 d/s to +90 d/s
        # We are multplying by 90,000 instead of 90,000 here so we can keep it in units of 1,000 and do integer math instead of floating point math
        desired_pitch_rate:int = (input_pitch_int16 * 90000) // 32767
        desired_roll_rate:int = (input_roll_int16 * 90000) // 32767
        desired_yaw_rate:int = (input_yaw_int16 * 90000) // 32767

        # now compare those ACTUAL rates with the DESIRED rates (calculate error)
        # error = desired - actual
        error_pitch_rate:int = desired_pitch_rate - pitch_rate
        error_roll_rate:int = desired_roll_rate - roll_rate
        error_yaw_rate:int = desired_yaw_rate - yaw_rate
        #print("ErrPitch: " + str(error_pitch_rate) + ", ErrRoll: " + str(error_roll_rate) + ", ErrYaw: " + str(error_yaw_rate))

        # Pitch PID calculation
        pitch_p:int = (error_pitch_rate * pitch_kp) // PID_SCALING_FACTOR
        pitch_i:int = pitch_last_i + ((error_pitch_rate * pitch_ki) // PID_SCALING_FACTOR)
        pitch_i = min(max(pitch_i, -i_limit), i_limit) # constrain within I limit
        pitch_d = (pitch_kd * (error_pitch_rate - pitch_last_error)) // PID_SCALING_FACTOR
        pitch_pid = pitch_p + pitch_i + pitch_d

        # Roll PID calculation
        roll_p:int = (error_roll_rate * roll_kp) // PID_SCALING_FACTOR
        roll_i:int = roll_last_i + ((error_roll_rate * roll_ki) // PID_SCALING_FACTOR)
        roll_i = min(max(roll_i, -i_limit), i_limit) # constrain within I limit
        roll_d = (roll_kd * (error_roll_rate - roll_last_error)) // PID_SCALING_FACTOR
        roll_pid = roll_p + roll_i + roll_d

        # Yaw PID calculation
        yaw_p:int = (error_yaw_rate * yaw_kp) // PID_SCALING_FACTOR
        yaw_i:int = yaw_last_i + ((error_yaw_rate * yaw_ki) // PID_SCALING_FACTOR)
        yaw_i = min(max(yaw_i, -i_limit), i_limit) # constrain within I limit
        yaw_d = (yaw_kd * (error_yaw_rate - yaw_last_error)) // PID_SCALING_FACTOR
        yaw_pid = yaw_p + yaw_i + yaw_d

        # save state values for next loop
        pitch_last_error = error_pitch_rate
        roll_last_error = error_roll_rate
        yaw_last_error = error_yaw_rate
        pitch_last_i = pitch_i
        roll_last_i = roll_i
        yaw_last_i = yaw_i

        # Calculate the mean pulse width the PWM signals will use
        # each motor will then offset this a bit based on the PID values for each axis
        # "pwm_pw" short for "Pulse Width Modulation Pulse Width"
        mean_pwm_pw:int = 1000000 + (input_throttle_uint16 * 1000000) // 65535

        # calculate throttle values for each motor using those PID influences
        #print("Pitch PID: " + str(pitch_pid) + ", Roll PID: " + str(roll_pid) + ", Yaw Pid: " + str(yaw_pid))
        m1_pwm_pw = mean_pwm_pw + pitch_pid + roll_pid - yaw_pid
        m2_pwm_pw = mean_pwm_pw + pitch_pid - roll_pid + yaw_pid
        m3_pwm_pw = mean_pwm_pw - pitch_pid + roll_pid + yaw_pid
        m4_pwm_pw = mean_pwm_pw - pitch_pid - roll_pid - yaw_pid

        # min/max those duty times
        # constrain to within 1 ms and 2 ms (1,000,000 nanoseconds and 2,000,000 nanoseconds), which is the min and max throttle duty cycles
        m1_pwm_pw = min(max(m1_pwm_pw, 1000000), 2000000)
        m2_pwm_pw = min(max(m2_pwm_pw, 1000000), 2000000)
        m3_pwm_pw = min(max(m3_pwm_pw, 1000000), 2000000)
        m4_pwm_pw = min(max(m4_pwm_pw, 1000000), 2000000)
        
        # MOTOR SHUTDOWN CONDITIONS (safety)
        # there are two conditions that would mean, no matter what happened above, ALL FOUR motors should be shut down (0% throttle)
        # scenario 1: desired throttle is 0%. This is obvious. If throttle is 0%, no motors should move. But, the PID loop is still running so it will still be trying to compensate for rate errors, meaning a motor could go OVER 0% throttle.
        # scenario 2: it has been a long time since we received a valid control data packet. This could be due to an error or something with the controller not sending data or the HL-MCU not sending data... but if this happens, as a failsafe, turn off all motors to prevent them from being stuck on.
        if input_throttle_uint16 == 0 or time.ticks_diff(time.ticks_ms(), control_input_last_received_ticks_ms) > 2000: # if we havne't received valid control input data in more than 2 seconds
            
            # shut off all motors
            # 1,000,000 nanoseconds = 1 ms, the minumum throttle for an ESC (0% throttle, so no rotation)
            m1_pwm_pw = 1000000
            m2_pwm_pw = 1000000
            m3_pwm_pw = 1000000
            m4_pwm_pw = 1000000

            # reset cumulative PID values (I and D related)
            pitch_last_i = 0
            roll_last_i = 0
            yaw_last_i = 0
            pitch_last_error = 0
            roll_last_error = 0
            yaw_last_error = 0

        # adjust throttles on PWMs
        #print("M1: " + str(m1_pwm_pw) + ", M2: " + str(m2_pwm_pw) + ", M3: " + str(m3_pwm_pw), "M4: " + str(m4_pwm_pw))
        M1.duty_ns(m1_pwm_pw)
        M2.duty_ns(m2_pwm_pw)
        M3.duty_ns(m3_pwm_pw)
        M4.duty_ns(m4_pwm_pw)

        # print?
        if time.ticks_diff(time.ticks_ms(), LAST_PRINT) > 500:
            print("--- AT " + str(time.ticks_ms()) + " ---")
            #print("M1: " + str(m1_pwm_pw))
            #print("M2: " + str(m2_pwm_pw))
            #print("M3: " + str(m3_pwm_pw))
            #print("M4: " + str(m4_pwm_pw))
            print("Pitch Rate: " + str(pitch_rate))
            print("Roll Rate: " + str(roll_rate))
            print("Yaw Rate: " + str(yaw_rate))
            print()
            LAST_PRINT = time.ticks_ms()

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
    FATAL_ERROR("UILE: " + str(ex)) # UILE = "Unhandled In-Loop Error"