import machine
import time
import math

### SETTINGS ###
gyro_x_bias:float = -0.7 # X degrees per second when resting (bias/error we will correct for)
gyro_y_bias:float = 1.2 # Y degrees per second when resting (bias/error we will correct for)
gyro_z_bias:float = -0.2 # Z degrees per second when resting (bias/error we will correct for)
################

# set up I2C
i2c = machine.I2C(0, sda=machine.Pin(16), scl=machine.Pin(17))
print(i2c.scan()) # 0x68 (104) should be in there, that is the address of the MPU-6050

# MPU-6050 configuration
i2c.writeto_mem(0x68, 0x6B, bytes([0])) # wake up
i2c.writeto_mem(0x68, 0x1A, bytes([0x05])) # set low pass filter for both gyro and accel to 10 hz (level 5 out of 6 in smoothing)
i2c.writeto_mem(0x68, 0x1B, bytes([0x00])) # set full scale range of gyro to 250 degrees per second
i2c.writeto_mem(0x68, 0x1C, bytes([0x00])) # set full scale range of accelerometer to 2g (lowest, most sensitive)

# Complementary Filter Variables
alpha:float = 0.98     # how much weight we give the gyro over the accel
pitch:float = 0.0      # pitch starting point
roll:float = 0.0       # roll starting point
last_time = time.ticks_ms()

while True:
    
    # read gyro data
    gyro:bytes = i2c.readfrom_mem(0x68, 0x43, 6) # read 6 bytes: gyro X high, gyro X low, gyro Y high, gyro Y low, gyro Z high, gyro Z low
    
    # convert bytes to 16-bit ints
    gyro_x = (gyro[0] << 8) | gyro[1]
    gyro_y = (gyro[2] << 8) | gyro[3]
    gyro_z = (gyro[4] << 8) | gyro[5]

    # convert unsigned ints to signed ints (so there can be negatives)
    if gyro_x >= 32768: gyro_x = ((65535 - gyro_x) + 1) * -1
    if gyro_y >= 32768: gyro_y = ((65535 - gyro_y) + 1) * -1
    if gyro_z >= 32768: gyro_z = ((65535 - gyro_z) + 1) * -1

    # now, divide by the scale factor to get the actual degrees per second
    # this is defined in a table in the register map PDF, shown here: https://i.imgur.com/hCh08VO.png
    # for scale factor of 250 degrees/second, divide by 131
    # for scale factor of 500 degrees/second, divide by 65.5
    # for scale factor of 1000 degrees/second, divide by 32.8
    # for scale factor of 2000 degrees/second, divide by 16.4
    gyro_x = gyro_x / 131
    gyro_y = gyro_y / 131
    gyro_z = gyro_z / 131

    # now subtract out the bias/error noted
    gyro_x = gyro_x - gyro_x_bias
    gyro_y = gyro_y - gyro_y_bias
    gyro_z = gyro_z - gyro_z_bias

    # now we will do accelerometer!
    # read acceleromete data
    accel:bytes = i2c.readfrom_mem(0x68, 0x3B, 6) # read 6 bytes for accelerometer data: Accel X High, Accel X Low, Accel Y High, Accel Y Low, Accel Z High, Accel Z Low

    # convert bytes to 16 bit ints
    accel_x = (accel[0] << 8) | accel[1]
    accel_y = (accel[2] << 8) | accel[3]
    accel_z = (accel[4] << 8) | accel[5]

    # convert unsigned ints to signed ints (so there can be negatives)
    if accel_x >= 32658: accel_x = ((65535 - accel_x) + 1) * -1
    if accel_y >= 32658: accel_y = ((65535 - accel_y) + 1) * -1
    if accel_z >= 32658: accel_z = ((65535 - accel_z) + 1) * -1

    # now divide by the scale factor to get the actual accelerometer values
    # this is defined in a table in the register map PDF, shown here: https://i.imgur.com/TR7OJiP.png
    # for scale range of 2g, divide by 16384
    # for scale range of 4g, divide by 8192
    # for scale range of 8g, divide by 4096
    # for scale range of 16g, divide by 2048
    accel_x = accel_x / 16384
    accel_y = accel_y / 16384
    accel_z = accel_z / 16384

    # print Gyro + Accel Data
    #print(f"Gyro X: {gyro_x:.2f}, Gyro Y: {gyro_y:.2f}, Gyro Z: {gyro_z:.2f}")
    #print(f"Accel X: {accel_x:.2f}, Accel Y: {accel_y:.2f}, Accel Z: {accel_z:.2f}")
    
    # use accel data to calculate pitch and roll
    # but note, because this is the accelerometer ONLY being used and it is very susceptible to vibrations, this will probably be rather inaccurate
    # hence, why we use a complementary filter below to fuse the gyro and accel together
    accel_pitch = math.atan2(accel_x, math.sqrt(accel_y ** 2 + accel_z ** 2)) * 180 / math.pi
    accel_roll = math.atan2(accel_y, math.sqrt(accel_x ** 2 + accel_z ** 2)) * 180 / math.pi
    #print("Accel Pitch: " + str(accel_pitch) + ", Accel Roll: " + str(accel_roll))

    # complementary filter to determine angle
    elapsed_seconds:float = (time.ticks_ms() - last_time) / 1000 # we must calculate how many seconds elapsed since the last read because remember, the gyro is a RATE. By multiplying the rate times the number of seconds that have passed, we can assume that is the number of degrees the IMU has rotated along that axis in that time period
    last_time = time.ticks_ms()
    pitch = alpha * (pitch - gyro_y * elapsed_seconds) + (1 - alpha) * accel_pitch    # see where I am subtracting out gyro_y? You may need to change that to a +. It is based on how you have the MPU-6050 mounted, direction it is facing in, etc.
    roll = alpha * (roll + gyro_x * elapsed_seconds) + (1 - alpha) * accel_roll

    # print
    print("Pitch: " + str(int(pitch)) + "°, Roll: " + str(int(roll)) + "°")

    # wait
    time.sleep(0.05)