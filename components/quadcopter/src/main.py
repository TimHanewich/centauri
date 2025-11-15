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
import tools
import os

####################
##### SETTINGS #####
####################

alpha:int = 98                 # complementary filter alpha value for pitch/roll angle estimation. A value closer to 100 (MAX 100!) favor's gyroscope's opinion, lower (MIN 0!) favors accelerometer (noisy)
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
print("Setting MPU-6050 gyro scale range to 1,000 d/s...")
i2c.writeto_mem(0x68, 0x1B, bytes([0x10])) # set full scale range of gyro to 1,000 degrees per second
print("Setting MPU-6050 accelerometer scale range to 8g...")
i2c.writeto_mem(0x68, 0x1C, bytes([0x10])) # set full scale range of accelerometer to 8g
print("Setting MPU-6050 LPF to 10 Hz...")
i2c.writeto_mem(0x68, 0x1A, bytes([0x05])) # set low pass filter for both gyro and accel to 10 hz (level 5 out of 6 in smoothing)

# wait a moment, then validate MPU-6050 settings have taken place
time.sleep(0.25)
if i2c.readfrom_mem(0x68, 0x1B, 1)[0] == 0x10:
    print("MPU-6050 Gyro full scale range confirmed to be set at 1,000 d/s")
else:
    print("MPU-6050 Gyro full scale range set failed!")
    FATAL_ERROR("MPU6050 gyro range set failed.")
if i2c.readfrom_mem(0x68, 0x1C, 1)[0] == 0x10:
    print("MPU-6050 accelerometer full scale range confirmed to be set at 8g")
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

# determine how much space we have in storage to store telemetry
print()
print("CHECKING STORAGE SPACE")
stats:tuple = os.statvfs('/')
block_size:int = stats[0]
free_blocks:int = stats[3]
free_bytes:int = block_size * free_blocks # how much free space is on the device, in bytes. This will be decremented as we add to it.
print(str(free_bytes) + " bytes free for telemetry storage")

# declare variables: desired rate inputs
# these will later be updated via incoming desired rate packets (over UART from HL-MCU)
input_throttle_uint16:int = 0        # from 0 to 65535, representing 0-100%
input_pitch_int16:int = 0            # from -32768 to 32767, later interpreted to -90.0 to 90.0 degrees/second
input_roll_int16:int = 0             # from -32768 to 32767, later interpreted to -90.0 to 90.0 degrees/second
input_yaw_int16:int = 0              # from -32768 to 32767, later interpreted to -90.0 to 90.0 degrees/second

# set up ADC for reading the battery voltage
vbat_adc = machine.ADC(machine.Pin(26))

# Set up telemetry variables
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
telemetry_packet_stream:bytearray = bytearray(7) # array that we will repopulate with updated telemetry data (i.e. battery level, pitch rate, etc.).
telemetry_packet_store:bytearray = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n') # array that we will repopulate with telemetry data intended to be stored to local flash storage
TIMHPING:bytes = "TIMHPING\r\n".encode() # example TIMHPING\r\n for comparison sake later (so we don't have to keep encoding it and making a new bytes object later)
TIMHPONG:bytes = "TIMHPONG\r\n".encode() # example TIMHPONG\r\n that we will send back out later on. Making it here to avoid re-making it in the loop

# declare objects that will be used for reading incoming data from the HC-12 (conveyer approach)
terminator:bytes = "\r\n".encode()        # example \r\n for comparison sake later on (13, 10 in bytes)
rxBuffer:bytearray = bytearray(128)       # buffer we st up only to append new incoming data received over the HC-12 (via UART)
ProcessBuffer:bytearray = bytearray(256)  # buffer we immediately append newly received bytes to and then process the lines out of
ProcessBufferMV:memoryview = memoryview(ProcessBuffer)
ProcessBufferOccupied:int = 0             # simple counter of how many bytes of the process buffer are occupied (starting from position 0)

# declare PID state variables
# declaring them here because their "previous state" (value from previous loop) must be referenced in each loop
pitch_last_i:int = 0
pitch_last_error:int = 0
roll_last_i:int = 0
roll_last_error:int = 0
yaw_last_i:int = 0
yaw_last_error:int = 0

# declare variables that serve for storing telemetry
temp_telemetry_storage_len:int = 25000                                       # declare length of the temporary storage
temp_telemetry_storage:bytearray = bytearray(temp_telemetry_storage_len)     # create the fixed-length bytearray for storing telemetry while in flight (fast)
temp_telemetry_storage_mv:memoryview = memoryview(temp_telemetry_storage)    # create a memoryview of that temp storage array for faster copying into later on
temp_telemetry_storage_used:int = 0                                          # for tracking how many bytes of the temp storage have been used so far

# timestamps for tracking other processes that need to be done on a schedule
# originally was using asyncio for this but now resorting to timestamp-based
led_last_flickered_ticks_ms:int = 0 # the last time the onboard (pico) LED was swapped, in ms ticks
telemetry_last_recorded_ticks_ms:int = 0 # the most recent time the telemetry was last recorded
status_last_sent_ticks_ms:int = 0 # the most recent time the telemetry status was sent to the remote controller via HC-12
control_input_last_received_ticks_ms:int = 0 # timestamp (in ms) of the last time a valid control packet was received. This is used to check and shut down motors if it has been too long (failsafe)
last_gyro_dead_reckoning_ticks_us:int = 0 # timestamp (in us) of when we did the last dead reckoning via the gyroscope to estimate the pitch and roll angle. Important for the calculation

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
         
        # check for received data (input data) from the HC-12
        # ~250 us when there is data coming in rapidly, ~650 us when there is not data coming in. The reason it takes longer when there is NOT new data is because the ProcessBuffer.find() spends more time searching through the entire bytearray... just to find nothing. Versus when it has data, it finds something quickly shallow in the ProcessBuffer
        # ~16 bytes of memory used, but only when it has a full new line and thus has to use the memoryview slice to move the conveyer belt back
        # the data that we receive from the HC-12 could be:
        # 1 - control data
        # 2 - Settings update data (PID settings)
        # 3 - PING
        try:  

            # Step 1: If bytes received and available via HC-12, collect them
            # ~250-330 us
            # 0 bytes of new memory used
            bytesavailable:int = uart_hc12.any()
            if bytesavailable > 0: # there are bytes available

                # read into the rxBuffer (just a place to read them into)
                bytesread:int = uart_hc12.readinto(rxBuffer, bytesavailable)

                # Now copy them into the ProcessBuffer, but only ifwe have room for the entirety of it
                # if we don't have room for all of it, ignore it
                if bytesread <= len(ProcessBuffer) - ProcessBufferOccupied: # if we have room left in the process buffer that will fit all the bytes we just received

                    # copy the bytes we just received in the rxBuffer into the ProcessBuffer, byte by byte (one by one)
                    for i in range(0, bytesread):
                        ProcessBuffer[ProcessBufferOccupied + i] = rxBuffer[i]

                    # increment how much of the ProcessBuffer is now occupied
                    ProcessBufferOccupied = ProcessBufferOccupied + bytesread

            # Step 2: Do we have a complete line to work with (a "\r\n" terminator is there)
            # if we do, isolate it, process it
            # takes ~480 us
            while True: # continuously search until there are no more left
                TerminatorLoc:int = ProcessBuffer.find(terminator, 0, ProcessBufferOccupied)
                if TerminatorLoc == -1: # if a terminator (\r\n) was not found...
                    break # break out of the while loop
                else:

                    # At this point, we can assume the ProcessBuffer's NEXT LINE (that we have yet to process) is between position 0 and "TerminatorLoc"
                    # example below (commented out) of what we could do if I was not worried about memory management
                    #ThisLine:bytes = ProcessBuffer[0:LineEndLoc]
                    # we will not do that because any slicing (using "[]") uses NEW memory... even if you slice via a memoryview!!!!!

                    # Process the line 
                    t1 = time.ticks_us()
                    if ProcessBuffer.startswith(TIMHPING): # PING: simple check of life. Checking "startswith" is quick, only ~70 us
                        uart_hc12.write(TIMHPONG) # PONG back
                    elif ProcessBuffer[0] & 0b00000001 == 0: # if bit 0 is 0, it is a control packet
                        unpack_successful:bool = tools.unpack_control_packet(ProcessBuffer, control_input) # takes ~350 us, uses 0 bytes of new memory
                        if unpack_successful:
                            input_throttle_uint16 = control_input[0]
                            input_pitch_int16 = control_input[1]
                            input_roll_int16 = control_input[2]
                            input_yaw_int16 = control_input[3]
                            control_input_last_received_ticks_ms = time.ticks_ms() # mark that we just now got control input
                    elif ProcessBuffer[0] & 0b00000001 != 0: # if bit 0 is 1, it is a settings update
                        settings:dict = tools.unpack_settings_update(ProcessBuffer)
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
                        print("Unknown data received via HC-12")
                        send_special("?") # respond with a simple question mark to indicate the message was not understood.

                    # Move the conveyer belt back so the new unprocessed data is right at the beginning
                    # ~180 us
                    # 16 bytes of new memory used each time... unavoidable due to memoryview slicer
                    NewDataStarts:int = TerminatorLoc + 2                                                                           # Where the "next line" (new, unprocessed data) begins, skipping past the \r\n terminator
                    NumberOfBytesToMove:int = ProcessBufferOccupied - NewDataStarts                                                 # how many bytes in the ProcessBuffer we need to move back (left)... basically how big that entire chunk is
                    ProcessBufferMV[0:NumberOfBytesToMove] = ProcessBufferMV[NewDataStarts:NewDataStarts + NumberOfBytesToMove]     # take that entire unprocessed chunk and shift it to the beginning
                    ProcessBufferOccupied = ProcessBufferOccupied - NewDataStarts                                                   # decrement how much of the ProcessBuffer is now occupied since we just "extracted" (processed) a line and then moved everything backward like a conveyer belt
        except Exception as ex:
            print("RX FAIL: " + str(ex))
            input_throttle_uint16 = 0
            input_pitch_int16 = 0
            input_roll_int16 = 0
            input_yaw_int16 = 0
            send_special("CommsRx Err: " + str(ex))

        # Capture RAW IMU data: both gyroscope and accelerometer
        # Goal here is ONLY to capture the data, not to transform it
        # ~700 us
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
        # ~100 us
        gyro_x = (gyro_data[0] << 8) | gyro_data[1]
        gyro_y = (gyro_data[2] << 8) | gyro_data[3]
        gyro_z = (gyro_data[4] << 8) | gyro_data[5]
        if gyro_x >= 32768: gyro_x = ((65535 - gyro_x) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        if gyro_y >= 32768: gyro_y = ((65535 - gyro_y) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        if gyro_z >= 32768: gyro_z = ((65535 - gyro_z) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        roll_rate = gyro_x * 10000 // 655 # now, divide by the scale factor to get the actual degrees per second. Multiply by 10,000 to both offset the divisor being 655 (not 65.5 as specified for this gyro scale) AND ensure the output is 1000x more so we can do integer math
        pitch_rate = gyro_y * 10000 // 655 # now, divide by the scale factor to get the actual degrees per second. Multiply by 10,000 to both offset the divisor being 655 (not 65.5 as specified for this gyro scale) AND ensure the output is 1000x more so we can do integer math
        yaw_rate = gyro_z * 10000 // 655 # now, divide by the scale factor to get the actual degrees per second. Multiply by 10,000 to both offset the divisor being 655 (not 65.5 as specified for this gyro scale) AND ensure the output is 1000x more so we can do integer math

        # Process & Transform raw accelerometer data
        # ~100 us
        accel_x = (accel_data[0] << 8) | accel_data[1]
        accel_y = (accel_data[2] << 8) | accel_data[3]
        accel_z = (accel_data[4] << 8) | accel_data[5]
        if accel_x >= 32768: accel_x = ((65535 - accel_x) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        if accel_y >= 32768: accel_y = ((65535 - accel_y) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        if accel_z >= 32768: accel_z = ((65535 - accel_z) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
        accel_x = (accel_x * 1000) // 4096 # divide by scale factor for 8g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)
        accel_y = (accel_y * 1000) // 4096 # divide by scale factor for 8g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)
        accel_z = (accel_z * 1000) // 4096 # divide by scale factor for 8g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)

        # subtract out (account for) gyro bias that was calculated during calibration phase
        pitch_rate = pitch_rate - gyro_bias_y
        roll_rate = roll_rate - gyro_bias_x
        yaw_rate = yaw_rate - gyro_bias_z

        # Because of how I have my IMU mounted, invert necessary axes
        # I could in theory not need to do this if I mounted it flipped over, but preferring to leave it as is physically and just make the adjustment here!
        pitch_rate = pitch_rate * -1    # this ensures as the drone pitches down towards the ground, that is a NEGATIVE pitch rate. And a tile up would be positive
        yaw_rate = yaw_rate * -1        # this ensures the drone rotating towards the right is a POSITIVE yaw rate, with a left turn being negative

        # calculate the "accelerometers opinion" of the pitch and roll angles
        # these will later be "fused" with the gyro's opinion via a complementary filter
        # This will output the pitch and roll angle as 1000x what it is (so like 5493 is 5.493 degrees)
        pitch_angle_accel:int = tools.iatan2(accel_x, tools.isqrt(accel_y * accel_y + accel_z * accel_z)) * 180_000 // 3142
        roll_angle_accel:int = tools.iatan2(accel_y, tools.isqrt(accel_x * accel_x + accel_z * accel_z)) * 180_000 // 3142

        # Now calculate how much time has elapsed since the last time we were here, about to use dead reckoning with the gyro's data to estimate the angles
        elapsed_since_ldr_ticks_us:int = time.ticks_diff(time.ticks_us(), last_gyro_dead_reckoning_ticks_us) # how many ticks have elapsed sine the last dead reckoning
        last_gyro_dead_reckoning_ticks_us = time.ticks_us() # update the time, just as a flag. This will establish a baseline for how long since we were last here on the next loop. And that timespan is very important to perform dead reckoning with the gyro data.

        # if the elapsed time since the last dead reckoning is less than 250 ms, we should use fusion
        # otherwise, we should just accept whatever the accelerometer is telling us (that will prob be more reliable than combining w/ the gyro's dead reckoning)
        # I learned the "dead reckoning" used by the gyro is really only reliable in very tight read loops
        # This also avoids the problem of the angles shooting up massively when first starting up because the time elapsed would have been so high
        if elapsed_since_ldr_ticks_us < 250_000: 
            
            # calculate the "gyro's opinion" using dead reckoning
            # why do we divide by 1,000,000?
            # Because the pitch rate is in degrees per second... and we measured it as us, of which there are 1,000,000 us in one second.
            # so we have to divide by 1,000,000 to calculate how far, in degrees, it drifted in that time at that degrees/second rate
            pitch_angle_gyro:int = pitch_angle + (pitch_rate * elapsed_since_ldr_ticks_us // 1_000_000)
            roll_angle_gyro:int = roll_angle + (roll_rate * elapsed_since_ldr_ticks_us // 1_000_000)

            # Now use a complementary filter to determine angle (fuse accelerometer and gyro data)
            pitch_angle = ((pitch_angle_gyro * alpha) + (pitch_angle_accel * (100 - alpha))) // 100
            roll_angle = ((roll_angle_gyro * alpha) + (roll_angle_accel * (100 - alpha))) // 100
        else:
            pitch_angle = pitch_angle_accel
            roll_angle = roll_angle_accel

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

        # Pitch PID calculation
        pitch_p:int = (error_pitch_rate * pitch_kp) // PID_SCALING_FACTOR
        pitch_i:int = pitch_last_i + ((error_pitch_rate * pitch_ki) // PID_SCALING_FACTOR)
        if pitch_i < -i_limit: # constrain within I limit. I originally was using min(max()) here but that takes 210 us. Way too slow. Doing it this way uses only 40 us.
            pitch_i = -i_limit
        elif pitch_i > i_limit:
            pitch_i = i_limit
        pitch_d = (pitch_kd * (error_pitch_rate - pitch_last_error)) // PID_SCALING_FACTOR
        pitch_pid = pitch_p + pitch_i + pitch_d

        # Roll PID calculation
        roll_p:int = (error_roll_rate * roll_kp) // PID_SCALING_FACTOR
        roll_i:int = roll_last_i + ((error_roll_rate * roll_ki) // PID_SCALING_FACTOR)
        if roll_i < -i_limit: # constrain within I limit
            roll_i = -i_limit
        elif roll_i > i_limit:
            roll_i = i_limit
        roll_d = (roll_kd * (error_roll_rate - roll_last_error)) // PID_SCALING_FACTOR
        roll_pid = roll_p + roll_i + roll_d

        # Yaw PID calculation
        yaw_p:int = (error_yaw_rate * yaw_kp) // PID_SCALING_FACTOR
        yaw_i:int = yaw_last_i + ((error_yaw_rate * yaw_ki) // PID_SCALING_FACTOR)
        if yaw_i < -i_limit: # constrain within I limit
            yaw_i = -i_limit
        elif yaw_i > i_limit:
            yaw_i = i_limit
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
        # I originally had this: mean_pwm_pw:int = 1000000 + (input_throttle_uint16 * 1000000) // 65535
        # however, that was causing a big memory usage as new memory had to be allocated to store the result of input_throttle_uint16 * 1,000,000 (it is in the billions)
        # to avoid that multiplication blowing up, I first multiply by 10,000 (keep the number small), AND THEN multiply by 100 afterwards
        # this saves memory by not allowing it to blow up into a big int, but also takes a small amount of accuracy off
        # for example, 1,078,340 will now be 1,078,300... but that is so small, it is negligible
        mean_pwm_pw:int = 1_000_000 + ((input_throttle_uint16 * 10_000) // 65535) * 100

        # calculate throttle values for each motor using those PID influences
        m1_pwm_pw = mean_pwm_pw + pitch_pid + roll_pid - yaw_pid
        m2_pwm_pw = mean_pwm_pw + pitch_pid - roll_pid + yaw_pid
        m3_pwm_pw = mean_pwm_pw - pitch_pid + roll_pid + yaw_pid
        m4_pwm_pw = mean_pwm_pw - pitch_pid - roll_pid - yaw_pid

        # min/max those duty times
        # constrain to within 1 ms and 2 ms (1,000,000 nanoseconds and 2,000,000 nanoseconds), which is the min and max throttle duty cycles
        # takes ~60 us
        # you may think why not just use the min/max functions here - I originally was! But those are very slow, taking ~440 us to min/max all four. Saving a lot of time doing it manually like this.
        if m1_pwm_pw < 1000000:
            m1_pwm_pw = 1000000
        elif m1_pwm_pw > 2000000:
            m1_pwm_pw = 2000000
        if m2_pwm_pw < 1000000:
            m2_pwm_pw = 1000000
        elif m2_pwm_pw > 2000000:
            m2_pwm_pw = 2000000
        if m3_pwm_pw < 1000000:
            m3_pwm_pw = 1000000
        elif m3_pwm_pw > 2000000:
            m3_pwm_pw = 2000000
        if m4_pwm_pw < 1000000:
            m4_pwm_pw = 1000000
        elif m4_pwm_pw > 2000000:
            m4_pwm_pw = 2000000
        
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
        M1.duty_ns(m1_pwm_pw)
        M2.duty_ns(m2_pwm_pw)
        M3.duty_ns(m3_pwm_pw)
        M4.duty_ns(m4_pwm_pw)

        # if we need to stream/record telemetry, pack telemetry
        # uses 0 bytes of new memory
        # ~1,000 us while armed, ~1,200 us when unarmed (it may send if unarmed)
        t1 = time.ticks_us()
        if time.ticks_diff(time.ticks_ms(), telemetry_last_recorded_ticks_ms) >= 250: # every 250 ms, telemetry will be recorded

            # first, get a ADC reading
            vbat_u16:int = vbat_adc.read_u16() # read the value on the ADC pin, as a uint16 (0-65535)

            # Using the ADC reading, estimate the actual supply voltage
            # I can do this because I have sampled what the ADC reading is at several KNOWN voltage supplies in tests previously (see R&D notes in this project)
            # Explanation of the values below:
            # -248,065 = "B" value in the equation y = mx + b. But B is multiplied by 1,000,000 for scaling purposes to avoid floating point math
            # 297 = "M" value in the equation y = mx + b. But M is multiplied by 1,000,000 for scaling purposes to avoid floating point math
            # 50,000 = half of the divisor. Adding this to the numerator is a trick to ensure that the resulting value is "rounded up". Integer division just truncates the remainder, which I don't want to happen, I want it to round up if it should round up. (i.e. 16.77 should be 16.8, not 16.7)
            # 100,000 = 10x less than the total scaler of 1,000,000 (used to scale M and B). We divide by 100,000 and not 1,000,000 so that way the resulting value is NOT a floating point number but instead an integer
            vbat:int = ((-248_065 + (vbat_u16 * 297)) + 50_000) // 100_000 # results in a value between 60 and 168 (6.0 and 16.8 volts respectively)

            # Prepare input values to packet as expected: rates
            packable_pitch_rate:int = pitch_rate // 1000                              # express as whole number  
            packable_roll_rate:int = roll_rate // 1000                                # express as whole number
            packable_yaw_rate:int = yaw_rate // 1000                                  # express as whole number

            # prepare input values as expected: input values
            # we need to convert the pitch, roll, and yaw input (expressed as int16 between -32,768 and 32,767) to a percentage from -100 to 100
            # I have found the most efficient way of doing this is to:
            # 1. convert it back to a uint16 (0 to 65,535) by adding 32,768 back to it (shift it up)
            # 2. the multiply by 100 and divide by 65,535 gets it into a percentage from 0 to 100 (percent of the 65,535 range)
            # 3. and then multiply by 2 and subtract by 100 to get it to the -100 to 100 range
            # originally I was dividing by 32,767 but that caused a -101 percent due to the asymetrical signs of an int16
            # Performance: takes ~127 us, uses 0 bytes of new memory
            packable_input_throttle:int = (input_throttle_uint16 * 100) // 65535                      # express between 0 and 100
            packable_input_pitch:int = ((((input_pitch_int16 + 32768) * 100) // 65535) * 2) - 100     # express between -100 and 100
            packable_input_roll:int = ((((input_roll_int16 + 32768) * 100) // 65535) * 2) - 100       # express between -100 and 100
            packable_input_yaw:int = ((((input_yaw_int16 + 32768) * 100) // 65535) * 2) - 100         # express between -100 and 100

            # Prepare input valuesas expected: motor throttles
            packable_m1_throttle:int = (m1_pwm_pw - 1000000) // 10000                 # express between 0 and 100
            packable_m2_throttle:int = (m2_pwm_pw - 1000000) // 10000                 # express between 0 and 100
            packable_m3_throttle:int = (m3_pwm_pw - 1000000) // 10000                 # express between 0 and 100
            packable_m4_throttle:int = (m4_pwm_pw - 1000000) // 10000                 # express between 0 and 100

            # pack it
            # takes ~460 us, uses 0 bytes of new memory
            # note: while calling this function below takes > 400 us, it takes only around 200 within the function. Maybe 200 us wasted by calling a function. Can save time running it inline below.
            tools.pack_telemetry(time.ticks_ms(), vbat, packable_pitch_rate, packable_roll_rate, packable_yaw_rate, packable_input_throttle, packable_input_pitch, packable_input_roll, packable_input_yaw, packable_m1_throttle, packable_m2_throttle, packable_m3_throttle, packable_m4_throttle, telemetry_packet_store)

            # Record it by adding it to the temporary memory buffer we have going while in flight
            # takes ~490 us, uses 0 bytes of new memory. I tried slicing via memoryview and array itself and that takes much longer - like 2,000 us! I also tried storing the len(telemetry_packet_store) and reusing it... doesnt do anything.
            if (temp_telemetry_storage_len - temp_telemetry_storage_used) > len(telemetry_packet_store): # if we have enough room for another telemetry packet store. Takes about 85 us
                for i in range(len(telemetry_packet_store)): # manually copy telemetry packet via loop. Takes about 450 us to complete
                    temp_telemetry_storage[temp_telemetry_storage_used + i] = telemetry_packet_store[i]
                temp_telemetry_storage_used = temp_telemetry_storage_used + len(telemetry_packet_store) # increment how many bytes are now used. Takes about 80 us

            # mark last recorded time
            telemetry_last_recorded_ticks_ms = time.ticks_ms() # update last time recorded

            # if we also have the opportunity to send telemetry right now, send it
            # We only send under 2 conditions:
            # 1. We are unarmed (throttle = 0)
            # 2. It is due time!
            if input_throttle_uint16 == 0: # if we are unarmed (throttle is 0%), we will consider streaming some telemetry periodically to the controller. It is important to only send data via HC-12 while unarmed because the HC-12 is half duplex, meaning it can't send and receive at the same time. Full focus should be put into receiving input commands while armed.
                if time.ticks_diff(time.ticks_ms(), status_last_sent_ticks_ms) >= 1000: # every 1000 ms (1 time per second)
                    
                    # construct stream packet
                    # we just packed all the data into the record buffer
                    # so pull out the telemetry we will send from there directly
                    telemetry_packet_stream[0] = 0b00000000                     # header byte. Bit 0 = 0 means it is a status packet.
                    telemetry_packet_stream[1] = telemetry_packet_store[3]      # vbat
                    telemetry_packet_stream[2] = telemetry_packet_store[4]      # pitch rate
                    telemetry_packet_stream[3] = telemetry_packet_store[5]      # roll rate
                    telemetry_packet_stream[4] = telemetry_packet_store[6]      # yaw rate
                    telemetry_packet_stream[5] = 13                             # \r
                    telemetry_packet_stream[6] = 10                             # \n

                    # send
                    uart_hc12.write(telemetry_packet_stream) # no need to append \r\n to it because the bytearray packet already has it at the end!
                    status_last_sent_ticks_ms = time.ticks_ms() # update last sent time

        # Do we have an opportunity to flush the telemetry? (we do if we are unarmed)
        # In this scenario, "flushing" means saving the telemetry that has built up in the temporary in-memory buffer and saving it file storage
        # We will ONLY do this if unarmed because it takes a significant amount of time (garbage collection). And when unarmed is when the tight time loop is not necessary
        # ~305,000 us - note, this takes TONS of time. But we only do it when unarmed (not in the tight PID loop)... so it is okay
        if input_throttle_uint16 == 0: # if we are unarmed
            if temp_telemetry_storage_used > 0: # if we have some telemetry to write

                # flush to flash storage
                log = open("log", "ab")
                for i in range(temp_telemetry_storage_used):
                    if free_bytes > 0: # if we have free bytes in capacity
                        log.write(bytes([temp_telemetry_storage[i]]))
                        free_bytes = free_bytes - 1 # decrement the number of bytes that are now free
                log.close()

                # clear out the temporary storage bytearray
                for i in range(temp_telemetry_storage_len):
                    temp_telemetry_storage[i] = 0
                temp_telemetry_storage_used = 0 # reset used counter

        # Wait if there is excess time
        # note: because of how telemetry is logged to temp buffer every 250 ms and then it is later to local storage immediately after if unarmed, on the loops when it is unarmed, it will be significantly behind
        # In testing, for each unarmed loop that performed a flush, it is slow by like > 300,000 us (300 ms)
        # This is because the process of opening the log file, appending to it, closing it, clearing the temp storage, etc. is SLOW!
        # It doesn't really matter when unarmed because that is not when the ultra tight PID loop is super important. But worth noting in case you see that and get concerned
        excess_us:int = cycle_time_us - time.ticks_diff(time.ticks_us(), loop_begin_us) # calculate how much excess time we have to kill until it is time for the next loop
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