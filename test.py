def pack_control_packet(throttle:float, pitch:float, roll:float, yaw:float) -> bytes:
    """
    Packs a control packet to be sent to the drone.
    
    Expects:
    throttle between 0.0 and 1.0
    pitch between -1.0 and 1.0
    roll between -1.0 and 1.0
    yaw between -1.0 and 1.0
    """

    ToReturn:bytearray = bytearray()

    # Add header byte (metadata byte)
    # bit 7, 6, 5, 4 are reserved (unused)
    header:int = 0b00000000 # start with 0. Bit 0 must be 0 to identify as a control packet, which it already is!s
    ToReturn.append(header)

    # Add throttle bytes
    asint16 = min(max(int(round(throttle * 65535, 0)), 0), 65535) # express as number between 0 and 65535
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add pitch bytes
    aspop:float = (pitch + 1) / 2 # as percent of the range -1.0 to 1.0
    asint16:int = min(max(int(round(aspop * 65535, 0)), 0), 65535) # convert the range from a number between 0 and 65535 (uint16)
    ToReturn.extend(asint16.to_bytes(2, "big")) # pack as 2-bytes using big endian

    # add roll bytes
    aspop:float = (roll + 1) / 2 # as percent of the range -1.0 to 1.0
    asint16:int = min(max(int(round(aspop * 65535, 0)), 0), 65535) # convert the range from a number between 0 and 65535 (uint16)
    ToReturn.extend(asint16.to_bytes(2, "big")) # pack as 2-bytes using big endian

    # add yaw bytes
    aspop:float = (yaw + 1) / 2 # as percent of the range -1.0 to 1.0
    asint16:int = min(max(int(round(aspop * 65535, 0)), 0), 65535) # convert the range from a number between 0 and 65535 (uint16)
    ToReturn.extend(asint16.to_bytes(2, "big")) # pack as 2-bytes using big endian

    # Add 2-byte XOR-chain-based checksum
    checksum1:int = 0x00 # start with 0
    checksum2:int = 0x00 # start with 0
    for byte in ToReturn: # for each byte added so far
        checksum1 = checksum1 ^ byte         # XOR operation on byte
        checksum2 = checksum2 ^ checksum1    # XOR operation on checksum1 itself
    ToReturn.append(checksum1)
    ToReturn.append(checksum2)

    # return it
    return bytes(ToReturn)


def unpack_control_packet(data:bytes, into:list[int]) -> bool:
    """
    Unpack desired rates packet into throttle input, pitch input, roll input, and yaw input, into a preexisting list. 

    The list it unpacks into must be 4 items long.
    Item 0 = throttle input, between 0 and 65535
    Item 1 = pitch input, between -32768 and 32767
    Item 2 = roll input, between -32768 and 32767
    Item 3 = yaw input, between -32768 and 32767
    
    Returns True if the unpack was successful, False if it did not unpack because of the checksum failing to verify or the data was just not long enough.
    """

    # We previously had in a check here that the provided bytearray is the minimum length needed to be a real packet
    # but I took that out for small performance gain
    # why dont we need that?
    # method I am using is providing an entire fixed-length "ProcessBuffer" to this (i.e. 256 bytes)
    # so the length of the buffer wil ALWAYS be large enough

    # first, validate checksums
    checksum1:int = 0x00 # start at 0
    checksum2:int = 0x00 # start at 0
    for i in range(9): # first 9 bytes (1 header byte, 2 throttle bytes, 2 pitch bytes, 2 roll bytes, 2 yaw bytes)
        checksum1 = checksum1 ^ data[i]
        checksum2 = checksum2 ^ checksum1
    if checksum1 != data[9] or checksum2 != data[10]: # if the checksum1 we calculated does NOT match the checksum1 in the data stream OR the checksum2 we calculated does NOT match the checksum2 in the data stream, it did NOT pass the checksum! Could be corrupted data!
        return False # return false to indicate it was not unpacked successfully
    
    # unpack throttle, an unsigned short (uint16)
    into[0] = data[1] << 8 | data[2]

    # unpack pitch, roll, yaw: all signed shorts (int16)
    # we subtract 32,768 out of each one to shift it BACK to a int16 from a uint16
    # if you look at the packing function, it is shifting the int16 values into uint16 values before packing to keep it simple.
    # So we are undoing it here by shifting it back, so negatives can be preserved!
    into[1] = (data[3] << 8 | data[4]) - 32768
    into[2] = (data[5] << 8 | data[6]) - 32768
    into[3] = (data[7] << 8 | data[8]) - 32768

    # return true to indicate the unpack was successful
    return True


data = pack_control_packet(0.6, 0.23, -0.3, -0.03)
unpack_to = [0,0,0,0]

successful = unpack_control_packet(data, unpack_to)
print(successful)
print(str(unpack_to))