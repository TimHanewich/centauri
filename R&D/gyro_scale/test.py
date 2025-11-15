import machine
import math
import time
import gc

i2c = machine.I2C(0, sda=machine.Pin(16), scl=machine.Pin(17))

# Set up MPU-6050
print("Waking up MPU-6050...")
i2c.writeto_mem(0x68, 0x6B, bytes([0])) # wake up 
print("Setting MPU-6050 gyro scale range to 1,000 d/s...")
i2c.writeto_mem(0x68, 0x1B, bytes([0x10])) # set full scale range of gyro to 1,000 degrees per second
print("Setting MPU-6050 accelerometer scale range to 8g...")
i2c.writeto_mem(0x68, 0x1C, bytes([0x10])) # set full scale range of accelerometer to 8g
print("Setting MPU-6050 LPF to 10 Hz...")
i2c.writeto_mem(0x68, 0x1A, bytes([0x05])) # set low pass filter for both gyro and accel to 10 hz (level 5 out of 6 in smoothing)

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
    roll_rate = gyro_x * 10000 // 655 # now, divide by the scale factor to get the actual degrees per second. Multiply by 10,000 to both offset the divisor being 655 (not 65.5 as specified for this gyro scale) AND ensure the output is 1000x more so we can do integer math
    pitch_rate = gyro_y * 10000 // 655 # now, divide by the scale factor to get the actual degrees per second. Multiply by 10,000 to both offset the divisor being 655 (not 65.5 as specified for this gyro scale) AND ensure the output is 1000x more so we can do integer math
    yaw_rate = gyro_z * 10000 // 655 # now, divide by the scale factor to get the actual degrees per second. Multiply by 10,000 to both offset the divisor being 655 (not 65.5 as specified for this gyro scale) AND ensure the output is 1000x more so we can do integer math

    #print("Roll Rate: " + str(roll_rate) + ", Pitch Rate: " + str(pitch_rate) + ", Yaw Rate: " + str(yaw_rate))

    # accel calc
    accel_x = (accel_data[0] << 8) | accel_data[1]
    accel_y = (accel_data[2] << 8) | accel_data[3]
    accel_z = (accel_data[4] << 8) | accel_data[5]
    if accel_x >= 32768: accel_x = ((65535 - accel_x) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    if accel_y >= 32768: accel_y = ((65535 - accel_y) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    if accel_z >= 32768: accel_z = ((65535 - accel_z) + 1) * -1 # convert unsigned ints to signed ints (so there can be negatives)
    accel_x = (accel_x * 1000) // 4096 # divide by scale factor for 8g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)
    accel_y = (accel_y * 1000) // 4096 # divide by scale factor for 8g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)
    accel_z = (accel_z * 1000) // 4096 # divide by scale factor for 8g range to get value. But before doing so, multiply by 1,000 because we will work with larger number to do integer math (faster) instead of floating point math (slow and memory leak)

    print(accel_x, accel_y, accel_z)

    time.sleep(0.1)