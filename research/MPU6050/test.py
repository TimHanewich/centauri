# This test is designed to validate the MPU-6050 can be read from quickly by the LL MCU
# This is a direct follow up to EIO (Errno 5) I have been seeing at a high read rate
# Error on August 25, 2025: https://i.imgur.com/Dg6Go0I.png
# It sometimes fails and recovers right away, sometimes not: https://i.imgur.com/4fQlNw0.png

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
delays_after_fails_ms:list[int] = [] # list of how long it took to get a good read right after getting a BAD read (EIO)
print("Entering infinite read loop now!")
while True:

    loop_begin_us:int = time.ticks_us()

    # try read
    ReadGood:bool = False
    ErrorEncountered:bool = True # if at least one EIO was encountered during this read attempt
    ReadAttemptBegan_ticks_ms:int = time.ticks_ms()
    while ReadGood == False:
        try:
            i2c.readfrom_mem_into(0x68, 0x43, gyro_data) # read gyro data
            i2c.readfrom_mem_into(0x68, 0x3B, accel_data) # read accel data
            ReadGood = True

            # if we already had an errro this loop, append it
            if ErrorEncountered:
                delays_after_fails_ms.append(time.ticks_diff(time.ticks_ms(), ReadAttemptBegan_ticks_ms))
        except:
            ReadGood = False
            ErrorEncountered = True

    # print?
    if (time.ticks_ms() - last_print_ticks_ms) > 3000: # every 3 seconds
        print("----- " + str(time.ticks_ms()) + " ticks (ms) -----")
        print("Gyro: " + str(gyro_data))
        print("Accel: " + str(accel_data))
        print("Delays after errors: " + str(delays_after_fails_ms))
        print()
        last_print_ticks_ms = time.ticks_ms()

    # wait
    excess_us:int = delay_us - time.ticks_diff(time.ticks_us(), loop_begin_us)
    if excess_us > 0:
        time.sleep_us(excess_us)
