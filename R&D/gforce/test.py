import machine
import math
import time
import gc

i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15))
accel_data:bytearray = bytearray(6) # 6 bytes to reading the accelerometer reading directly from the MPU-6050 via I2C

# Set up MPU-6050
print("Waking up MPU-6050...")
i2c.writeto_mem(0x68, 0x6B, bytes([0])) # wake up 
print("Setting MPU-6050 gyro scale range to 1,000 d/s...")
i2c.writeto_mem(0x68, 0x1B, bytes([0x10])) # set full scale range of gyro to 1,000 degrees per second
print("Setting MPU-6050 accelerometer scale range to 8g...")
i2c.writeto_mem(0x68, 0x1C, bytes([0x10])) # set full scale range of accelerometer to 8g
print("Setting MPU-6050 LPF to 10 Hz...")
i2c.writeto_mem(0x68, 0x1A, bytes([0x05])) # set low pass filter for both gyro and accel to 10 hz (level 5 out of 6 in smoothing)

# Viper sqrt estimator (integer math)
@micropython.viper
def isqrt(x: int) -> int:
    # Integer square root using Newton's method
    if x <= 0:
        return 0
    r = x
    while True:
        new_r = (r + x // r) // 2
        if new_r >= r:
            return r
        r = new_r

# accel G-Force calibration (should be @ 1.0 when resting)
gforce_samples:int = 0
samples_collected:int = 0
started_at_ticks_ms:int = time.ticks_ms()
while time.ticks_diff(time.ticks_ms(), started_at_ticks_ms) < 3000: # 3 seconds
    
    # read from IMU
    i2c.readfrom_mem_into(0x68, 0x3B, accel_data) # read 6 bytes, two for each axis for accelerometer data, directly into the "accel_data" bytearray

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

    # calculate G force
    gforce:int = isqrt(accel_x*accel_x + accel_y*accel_y + accel_z*accel_z) # 1,000 would be 1g
    gforce_samples = gforce_samples + gforce
    samples_collected = samples_collected + 1

    time.sleep(0.1)

print(str(samples_collected) + " samples collected")
avg_gforce:int = gforce_samples // samples_collected
gforce_offset:int = 1000 - avg_gforce # the offset correction
print("Avg g-force: " + str(avg_gforce))

while True:

    # read from IMU
    i2c.readfrom_mem_into(0x68, 0x3B, accel_data) # read 6 bytes, two for each axis for accelerometer data, directly into the "accel_data" bytearray

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

    #print(accel_x, accel_y, accel_z)

    # calculate G force
    # 0 new bytes used
    # ~75 us
    gforce:int = isqrt(accel_x*accel_x + accel_y*accel_y + accel_z*accel_z)         # 1,000 would be 1g
    gforce = gforce + gforce_offset                                                 # adjust for offset, calculated earlier during calibration
    gforce_packable = (gforce + 50) // 100                                          # convert it to a two-digit, "packable" (single byte), value. "10" would be 1.0g, "23" would be 2.3g, 8 would be 0.8 g, etc.

    print("GForce: " + str(gforce) + ", packable: " + str(gforce_packable))

    time.sleep(0.05)