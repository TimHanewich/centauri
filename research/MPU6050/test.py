# This test is designed to validate the MPU-6050 can be read from quickly by the LL MCU
# This is a direct follow up to EIO (Errno 5) I have been seeing at a high read rate
# Error on August 25, 2025: https://i.imgur.com/Dg6Go0I.png

import machine
import time

i2c = machine.I2C(0, sda=machine.Pin(16), scl=machine.Pin(17))
print("I2C scan: " + str(i2c.scan()))

hz_target:int = 250 # how many readings to take per second
delay_us:int = 1000000 // hz_target
print("Cycle time (us): " + str(delay_us))

gyro_data:bytearray = bytearray(6)
accel_data:bytearray = bytearray(6)

# go!
last_print_ticks_ms:int = 0
error_count:int = 0
immediate_error_recoveries:int = 0 # the number of times the read was successfull RIGHT after the error happened
just_encountered_error:bool = False
print("Entering infinite read loop now!")
while True:

    loop_begin_us:int = time.ticks_us()

    # read gyro data
    try:
        i2c.readfrom_mem_into(0x68, 0x43, gyro_data)
        if just_encountered_error:
            immediate_error_recoveries = immediate_error_recoveries + 1
        just_encountered_error = False
    except:
        error_count = error_count + 1
        just_encountered_error = True

    # read accel data
    try:   
        i2c.readfrom_mem_into(0x68, 0x3B, accel_data)
        if just_encountered_error:
            immediate_error_recoveries = immediate_error_recoveries + 1
        just_encountered_error = False
    except:
        error_count = error_count + 1
        just_encountered_error = True

    # print?
    if (time.ticks_ms() - last_print_ticks_ms) > 3000: # every 3 seconds
        print("----- " + str(time.ticks_ms()) + " ticks (ms) -----")
        print("Gyro: " + str(gyro_data))
        print("Accel: " + str(accel_data))
        print()
        last_print_ticks_ms = time.ticks_ms()

    # wait
    excess_us:int = delay_us - time.ticks_diff(time.ticks_us(), loop_begin_us)
    if excess_us > 0:
        time.sleep_us(excess_us)
