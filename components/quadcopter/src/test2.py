import time
import machine
import tools

i2c = machine.I2C(0, sda=machine.Pin(16), scl=machine.Pin(17))

print(str(i2c.scan()))

gyro_data:bytearray = bytearray(6)
accel_data:bytearray = bytearray(6)

hz:int = 10

pitch_angle:int = 0
roll_angle:int = 0



# Get baseline
gxs:int = 0          # gyro x samples (sum)
gys:int = 0          # gyro y samples (sum)
gzs:int = 0          # gyro z samples (sum)
samples:int = 0      # to count the number of samples we collect
started_at_ticks_ms:int = time.ticks_ms()
while time.ticks_diff(time.ticks_ms(), started_at_ticks_ms) < 3000: # 3 seconds

    # Read
    i2c.readfrom_mem_into(0x68, 0x43, gyro_data) # read 6 bytes, 2 for each axis, into the "gyro_data" bytearray (update values in that bytearray to have to avoid creating a new bytes object)
    i2c.readfrom_mem_into(0x68, 0x3B, accel_data) # read 6 bytes, two for each axis for accelerometer data, directly into the "accel_data" bytearray


    # Transform gyro data
    gyro_x = (gyro_data[0] << 8) | gyro_data[1]
    gyro_y = (gyro_data[2] << 8) | gyro_data[3]
    gyro_z = (gyro_data[4] << 8) | gyro_data[5]
    if gyro_x >= 32768: gyro_x = ((65535 - gyro_x) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    if gyro_y >= 32768: gyro_y = ((65535 - gyro_y) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    if gyro_z >= 32768: gyro_z = ((65535 - gyro_z) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    gyro_x = gyro_x * 10000 // 328      # now, divide by the scale factor to get the actual degrees per second. Multiply by 10,000 to both offset the divisor being 328 (not 32.8 as specified for this gyro scale) AND ensure the output is 1000x more so we can do integer math
    gyro_y = gyro_y * 10000 // 328      # now, divide by the scale factor to get the actual degrees per second. Multiply by 10,000 to both offset the divisor being 328 (not 32.8 as specified for this gyro scale) AND ensure the output is 1000x more so we can do integer math
    gyro_z = gyro_z * 10000 // 328      # now, divide by the scale factor to get the actual degrees per second. Multiply by 10,000 to both offset the divisor being 328 (not 32.8 as specified for this gyro scale) AND ensure the output is 1000x more so we can do integer math

    # increment
    gxs = gxs + gyro_x
    gys = gys + gyro_y
    gzs = gzs + gyro_z
    samples = samples + 1

    # wait
    time.sleep(0.01)


# Calc bias
gyro_bias_x:int = gxs // samples
gyro_bias_y:int = gys // samples
gyro_bias_z:int = gzs // samples
print("Gyro Bias: " + str(gyro_bias_x) + ", " + str(gyro_bias_y) + ", " + str(gyro_bias_z))

# Track real elapsed time between loop iterations rather than assuming
# time.sleep(1.0 / hz) gives us exactly 1/hz seconds (I2C reads + math take
# nonzero time too, so the true loop period drifts from the target period).
last_loop_ticks_us:int = time.ticks_us()

## TRACKING
last_accel_pitch:int = 0

while True:

    # Read
    i2c.readfrom_mem_into(0x68, 0x43, gyro_data) # read 6 bytes, 2 for each axis, into the "gyro_data" bytearray (update values in that bytearray to have to avoid creating a new bytes object)
    i2c.readfrom_mem_into(0x68, 0x3B, accel_data) # read 6 bytes, two for each axis for accelerometer data, directly into the "accel_data" bytearray

    # convert gyro
    gyro_x = (gyro_data[0] << 8) | gyro_data[1]
    gyro_y = (gyro_data[2] << 8) | gyro_data[3]
    gyro_z = (gyro_data[4] << 8) | gyro_data[5]
    if gyro_x >= 32768: gyro_x = ((65535 - gyro_x) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    if gyro_y >= 32768: gyro_y = ((65535 - gyro_y) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    if gyro_z >= 32768: gyro_z = ((65535 - gyro_z) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    roll_rate = gyro_x * 10000 // 328      # now, divide by the scale factor to get the actual degrees per second. Multiply by 10,000 to both offset the divisor being 328 (not 32.8 as specified for this gyro scale) AND ensure the output is 1000x more so we can do integer math
    pitch_rate = gyro_y * 10000 // 328     # now, divide by the scale factor to get the actual degrees per second. Multiply by 10,000 to both offset the divisor being 328 (not 32.8 as specified for this gyro scale) AND ensure the output is 1000x more so we can do integer math
    yaw_rate = gyro_z * 10000 // 328       # now, divide by the scale factor to get the actual degrees per second. Multiply by 10,000 to both offset the divisor being 328 (not 32.8 as specified for this gyro scale) AND ensure the output is 1000x more so we can do integer math

    # Process & Transform raw accelerometer data
    accel_x = (accel_data[0] << 8) | accel_data[1]
    accel_y = (accel_data[2] << 8) | accel_data[3]
    accel_z = (accel_data[4] << 8) | accel_data[5]
    if accel_x >= 32768: accel_x = ((65535 - accel_x) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    if accel_y >= 32768: accel_y = ((65535 - accel_y) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    if accel_z >= 32768: accel_z = ((65535 - accel_z) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    accel_x = (accel_x * 1000) // 4096 # divide by scale factor for 8g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)
    accel_y = (accel_y * 1000) // 4096 # divide by scale factor for 8g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)
    accel_z = (accel_z * 1000) // 4096 # divide by scale factor for 8g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)

    # subtract out bias
    pitch_rate = pitch_rate - gyro_bias_y
    roll_rate = roll_rate - gyro_bias_x
    yaw_rate = yaw_rate - gyro_bias_z

    # Inverse
    # I could in theory not need to do this if I mounted it flipped over, but preferring to leave it as is physically and just make the adjustment here!
    pitch_rate = pitch_rate * -1    # this ensures as the drone pitches down towards the ground, that is a NEGATIVE pitch rate. And a tile up would be positive
    yaw_rate = yaw_rate * -1        # this ensures the drone rotating towards the right is a POSITIVE yaw rate, with a left turn being negative


    # calculate angles: accel
    pitch_angle_accel:int = tools.iatan2(accel_x, tools.isqrt(accel_y * accel_y + accel_z * accel_z)) * 180_000 // 3142
    roll_angle_accel:int = tools.iatan2(accel_y, tools.isqrt(accel_x * accel_x + accel_z * accel_z)) * 180_000 // 3142

    # calc pitch angle to add for accel
    pitch_angle_accel_added = pitch_angle_accel - last_accel_pitch
    last_accel_pitch = pitch_angle_accel

    # calculate angles: gyro
    # Use the ACTUAL elapsed time (in microseconds) since the last iteration,
    # not an assumed period derived from hz, so drift from I2C/math overhead
    # doesn't silently bias the integration.
    now_ticks_us:int = time.ticks_us()
    us_elapsed:int = time.ticks_diff(now_ticks_us, last_loop_ticks_us)
    last_loop_ticks_us = now_ticks_us

    pitch_angle_gyro_to_add:int = ((pitch_rate * us_elapsed) // 1_000_000)
    pitch_angle_gyro:int = pitch_angle + pitch_angle_gyro_to_add
    roll_angle_gyro:int = roll_angle + ((roll_rate * us_elapsed) // 1_000_000)

    # complementary filter
    alpha:int = 9800
    alphai:int = 10_000 - alpha
    pitch_angle = ((pitch_angle_gyro * alpha) + (pitch_angle_accel * alphai)) // 10_000
    roll_angle = ((roll_angle_gyro * alpha) + (roll_angle_accel * alphai)) // 10_000


    # PRINT
    #print("Gyro X: " + str(gyro_x) + ", Gyro Y: " + str(gyro_y) + ", Gyro Z: " + str(gyro_z))
    #print(str("Pitch Rate: " + str(pitch_rate) + ", Roll Rate: " + str(roll_rate) + ", Yaw Rate: " + str(yaw_rate)))
    #print("Accel X: " + str(accel_x) + ", Accel Y: " + str(accel_y) + ", Accel Z: " + str(accel_z))
    #print("Pitch Angle (Accel): " + str(pitch_angle_accel) + ", Roll Angle (Accel): " + str(roll_angle_accel))
    ##print("Pitch Angle (Gyro): " + str(pitch_angle_gyro) + ", Pitch Angle (Accel): " + str(pitch_angle_accel) + ", Pitch Angle: " + str(pitch_angle))
    print("Adds: Accel = " + str(pitch_angle_accel_added) + ", Gyro = " + str(pitch_angle_gyro_to_add))


    # wait
    time.sleep(1.0 / hz)