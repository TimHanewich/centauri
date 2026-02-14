import time

# construct "dummy" packet
data = bytearray()
data.append(0b00000000) # header byte
data.append(253) # throttle byte 1
data.append(112) # throttle byte 2
data.append(87) # pitch byte 1
data.append(10) # pitch byte 2
data.append(128) # roll byte 1
data.append(0) # roll byte 2
data.append(128) # yaw byte 1
data.append(0) # yaw byte 2


# dual checksum
for _ in range(10):
    t1 = time.ticks_us()
    checksum1:int = 0b00000000 # start with 0
    checksum2:int = 0b00000000 # start with 0
    for byte in data:
        checksum1 = checksum1 ^ byte
        checksum2 = checksum2 ^ checksum1
    t2 = time.ticks_us()
    print("Time, ticks us: " + str(t2 - t1))
    print("Checksum1: " + str(checksum1))
    print("Checksum2: " + str(checksum2))