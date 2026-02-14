data = bytearray(b'\x00\xfdpW\n\x80\x00\x80\x00\xd0')
data.pop(len(data)-1) # remove the checksum byte

# dual checksum
checksum1:int = 0b00000000 # start with 0
checksum2:int = 0b00000000 # start with 0
for byte in data:
    checksum1 = checksum1 ^ byte
    checksum2 = checksum2 ^ checksum1
print("Checksum1: " + str(checksum1))
print("Checksum2: " + str(checksum2))