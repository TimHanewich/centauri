data = bytearray(b'\x00\xfdpW\n\x80\x00\x80\x00\xd0')
data.pop(len(data)-1) # remove the checksum byte


# checksum 1
checksum1:int = 0x00 # start with 0
for byte in data: # for each byte added so far
    checksum1 = checksum1 ^ byte # XOR operation

# checksum2
checksum2:int = 0x00 # start with 0
for i in range(len(data)):
    checksum2 = checksum2 ^ data[len(data)-1-i]

print("Checksum1: " + str(checksum1))
print("Checksum2: " + str(checksum2))