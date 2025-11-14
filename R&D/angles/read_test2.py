import machine
import math
import time
import gc

i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15))
accel_data:bytearray = bytearray(6) # 6 bytes to reading the accelerometer reading directly from the MPU-6050 via I2C

# Set up MPU-6050
print("Waking up MPU-6050...")
i2c.writeto_mem(0x68, 0x6B, bytes([0])) # wake up 
print("Setting MPU-6050 gyro scale range to 250 d/s...")
i2c.writeto_mem(0x68, 0x1B, bytes([0x00])) # set full scale range of gyro to 250 degrees per second
print("Setting MPU-6050 accelerometer scale range to 2g...")
i2c.writeto_mem(0x68, 0x1C, bytes([0x00])) # set full scale range of accelerometer to 2g (lowest, most sensitive)
print("Setting MPU-6050 LPF to 10 Hz...")
i2c.writeto_mem(0x68, 0x1A, bytes([0x05])) # set low pass filter for both gyro and accel to 10 hz (level 5 out of 6 in smoothing)

while True:

    # read from IMU
    i2c.readfrom_mem_into(0x68, 0x3B, accel_data) # read 6 bytes, two for each axis for accelerometer data, directly into the "accel_data" bytearray

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

    print("Accel data: " + str(accel_x) + ", " + str(accel_y) + ", " + str(accel_z))

    # calculate angle
    expected_pitch_angle_accel:int = int(math.atan2(accel_x, math.sqrt(accel_y*accel_y + accel_z*accel_z)) * 180000 / math.pi) # the accelerometers opinion of what the pitch angle is
    expected_roll_angle_accel:int = int(math.atan2(accel_y, math.sqrt(accel_x*accel_x + accel_z*accel_z)) * 180000 / math.pi) # the accelerometers opinion of what the roll angle is

    # print and wait
    print("Pitch Angle: " + str(expected_pitch_angle_accel) + ", Roll Angle: " + str(expected_roll_angle_accel))
    time.sleep(0.25)