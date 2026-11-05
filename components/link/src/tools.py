

###### DIRECTLY COPY + PASTE THIS OUT OF tools.py OF THE FLIGHT CONTROLLER REPO

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
    # This is based on the Fletcher16 checksum, shown here: https://en.wikipedia.org/wiki/Fletcher%27s_checksum
    # takes ~249 us
    checksum1:int = 0x00 # start at 0
    checksum2:int = 0x00 # start at 0
    for i in range(9): # first 9 bytes (1 header byte, 2 throttle bytes, 2 pitch bytes, 2 roll bytes, 2 yaw bytes)
        checksum1 = (checksum1 + data[i]) % 255
        checksum2 = (checksum2 + checksum1) % 255
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


