data = bytearray(b'\x00\xfdpW\n\x80\x00\x80\x00\xd0')
data.pop(len(data)-1) # remove the checksum byte

throttle_uint16_min:int = 64_224
throttle_uint16_max:int = 65_535

pitch_int16_min:int = -10_814
pitch_int16_max:int = -10_158

PossibleCheckSums:list[int] = []

for throttle in range (throttle_uint16_min, throttle_uint16_max):
    for pitch in range(pitch_int16_min, pitch_int16_max):

        # plug in throttle
        throttle_bytes:bytes = throttle.to_bytes(2, "big")
        data[1] = throttle_bytes[0]
        data[2] = throttle_bytes[1]

        # plug in pitch
        pitch_bytes:bytes = (pitch + 32_767).to_bytes(2, "big")
        data[3] = pitch_bytes[0]
        data[4] = pitch_bytes[1]

        # calculate the checksum
        checksum:int = 0x00 # start with 0
        for byte in data: # for each byte in the data
            checksum = checksum ^ byte # XOR operation
        
        # do we have it?
        if checksum not in PossibleCheckSums:
            PossibleCheckSums.append(checksum)

# print all possible checksums
print(str(len(PossibleCheckSums)) + " possible checksums")

