print("----- CENTAURI FLIGHT CONTROLLER -----")
print("gitub.com/TimHanewich/centauri")
print()

print("Importing libraries...")
import machine
import time
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

# establish failure pattern
def FATAL_ERROR(error_msg:str = None) -> None:
    print("FATAL ERROR ENCOUNTERED!")
    while True:
        if error_msg != None:
            print("FATAL ERROR: " + error_msg)
        led.toggle()
        time.sleep(1.0)

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
    #sendtimhmsg("IMU OK")
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
#sendtimhmsg("IMU SET")

# measure gyro to estimate bias
gxs:int = 0
gys:int = 0
gzs:int = 0
samples:int = 0
for i in range(3):
    print("Beginning gyro calibration in " + str(3 - i) + "... ")
    #endtimhmsg("GyroCal in " + str(3 - i))
    time.sleep(1.0)
#sendtimhmsg("CalibGyro...")
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
#sendtimhmsg("GyroCalib OK")

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