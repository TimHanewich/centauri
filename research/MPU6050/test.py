# This test is designed to validate the MPU-6050 can be read from quickly by the LL MCU
# This is a direct follow up to EIO (Errno 5) I have been seeing at a high read rate

import machine
import time

i2c = machine.I2C(0, sda=machine.Pin(16), scl=machine.Pin(17))
print("I2C scan: " + str(i2c.scan()))

hz_target:int = 250 # how many readings to take per second
delay_us:int = 1000000 // hz_target
print("Cycle time (us): " + str(delay_us))

gyro_data:bytearray = bytearray(6)
accel_data:bytearray = bytearray(6)

while True:

    loop_begin_us:int = time.ticks_us()

    # read gyro data
    i2c.readfrom_mem_into(0x68, 0x43, gyro_data)

    # read accel data
    i2c.readfrom_mem_into(0x68, 0x3B, accel_data)

    # wait
    excess_us:int = delay_us - time.ticks_diff(time.ticks_us(), loop_begin_us)
    print("Excess us: " + str(excess_us))
    if excess_us > 0:
        time.sleep_us(excess_us)
