import machine
import time

### SETTINGS ###
gyro_x_bias:float = -0.7 # X degrees per second when resting (bias/error we will correct for)
gyro_y_bias:float = 1.2 # Y degrees per second when resting (bias/error we will correct for)
gyro_z_bias:float = -0.2 # Z degrees per second when resting (bias/error we will correct for)
################


i2c = machine.I2C(0, sda=machine.Pin(16), scl=machine.Pin(17))
print(i2c.scan())

i2c.writeto_mem(0x68, 0x6B, bytes([0])) # wake up
i2c.writeto_mem(0x68, 0x1A, bytes([0x05])) # set low pass filter for both gyro and accel to 10 hz (level 5 out of 6 in smoothing)
i2c.writeto_mem(0x68, 0x1B, bytes([0x00])) # set full scale range to 250 degrees per second

while True:
    
    # read data
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
    
    print(f"X: {gyro_x:.2f}, Y: {gyro_y:.2f}, Z: {gyro_z:.2f}")
    time.sleep(0.05)