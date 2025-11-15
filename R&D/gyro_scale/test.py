import machine
import math
import time
import gc

i2c = machine.I2C(0, sda=machine.Pin(16), scl=machine.Pin(17))
accel_data:bytearray = bytearray(6)
gyro_data:bytearray = bytearray(6)

while True:
    i2c.readfrom_mem_into(0x68, 0x43, gyro_data)
    i2c.readfrom_mem_into(0x68, 0x3B, accel_data)

    # gyro calc
    gyro_x = (gyro_data[0] << 8) | gyro_data[1]
    gyro_y = (gyro_data[2] << 8) | gyro_data[3]
    gyro_z = (gyro_data[4] << 8) | gyro_data[5]
    if gyro_x >= 32768: gyro_x = ((65535 - gyro_x) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    if gyro_y >= 32768: gyro_y = ((65535 - gyro_y) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    if gyro_z >= 32768: gyro_z = ((65535 - gyro_z) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    roll_rate = gyro_x * 1000 // 131 # now, divide by the scale factor to get the actual degrees per second. But multiply by 1,000 to work in larger units so we can do integer math.
    pitch_rate = gyro_y * 1000 // 131 # now, divide by the scale factor to get the actual degrees per second. But multiply by 1,000 to work in larger units so we can do integer math.
    yaw_rate = gyro_z * 1000 // 131 # now, divide by the scale factor to get the actual degrees per second. But multiply by 1,000 to work in larger units so we can do integer math.

    print("Roll Rate: " + str(roll_rate) + ", Pitch Rate: " + str(pitch_rate) + ", Yaw Rate: " + str(yaw_rate))

    # accel calc
    accel_x = (accel_data[0] << 8) | accel_data[1]
    accel_y = (accel_data[2] << 8) | accel_data[3]
    accel_z = (accel_data[4] << 8) | accel_data[5]
    if accel_x >= 32768: accel_x = ((65535 - accel_x) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    if accel_y >= 32768: accel_y = ((65535 - accel_y) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    if accel_z >= 32768: accel_z = ((65535 - accel_z) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    accel_x = (accel_x * 1000) // 16384 # divide by scale factor for 2g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)
    accel_y = (accel_y * 1000) // 16384 # divide by scale factor for 2g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)
    accel_z = (accel_z * 1000) // 16384 # divide by scale factor for 2g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)


    time.sleep(0.1)