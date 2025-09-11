##### UNPACKING DATA FROM THE CONTROLLER #####

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

    # return False right off the bat if the packet is not long enough
    if len(data) < 10:
        return False

    # first, validate checksum
    selfchecksum:int = 0x00
    for i in range(9): # first 9 bytes
        selfchecksum = selfchecksum ^ data[i]
    if selfchecksum != data[9]: # the 10th byte (9th index position) is the checksum value. if the checksum we calculated did not match the checksum in the data itself, must have been a transmission error. Return nothing, fail.
        return False
    
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

def unpack_settings_update(data:bytes) -> dict:
    """Unpack settings update into a pre-existing list. Returns a dict with settings values if unpack was successful, None if unsuccessful."""

    # Check if it is to short
    if len(data) < 22:
        return None
    
    # Check checksum
    selfchecksum:int = 0x00 # start at 0
    for i in range(21): # first 21 bytes (the 22nd byte is the checksum)
        selfchecksum = selfchecksum ^ data[i] # XOR operation
    if data[21] != selfchecksum: # if the 22nd byte (index location of 21), which is the checksum, is not equal to the checksum we just calculated, the checksum didn't validate. May be a transmission error.
        return None

    # Unpack all
    # they should be encoded in BIG endian formats
    pitch_kp:int = data[1] << 8 | data[2]
    pitch_ki:int = data[3] << 8 | data[4]
    pitch_kd:int = data[5] << 8 | data[6]
    roll_kp:int = data[7] << 8 | data[8]
    roll_ki:int = data[9] << 8 | data[10]
    roll_kd:int = data[11] << 8 | data[12]
    yaw_kp:int = data[13] << 8 | data[14]
    yaw_ki:int = data[15] << 8 | data[16]
    yaw_kd:int = data[17] << 8 | data[18]
    i_limit:int = data[19] << 8 | data[20]

    # return
    return {"pitch_kp": pitch_kp, "pitch_ki": pitch_ki, "pitch_kd": pitch_kd, "roll_kp": roll_kp, "roll_ki": roll_ki, "roll_kd": roll_kd, "yaw_kp": yaw_kp, "yaw_ki": yaw_ki, "yaw_kd": yaw_kd, "i_limit": i_limit}






##### PACKING DATA TO BE SENT TO THE CONTROLLER #####

def pack_telemetry(vbat:float, pitch_rate:int, roll_rate:int, yaw_rate:int, pitch_angle:int, roll_angle:int, into:bytearray) -> None:
    """
    Packs telemetry into an existing bytearray of length 7 bytes

    Expects:
    vbat between 6.0 and 16.8 (float)
    pitch_rate between -128 and 127 (signed byte)
    roll_rate between -128 and 127 (signed byte)
    yaw_rate between -128 and 127 (signed byte)
    pitch_angle between -128 and 127 (signed byte)
    roll_angle between -128 and 127 (signed byte)
    """

    # ensure the provided bytearray is big enough
    if len(into) < 7:
        raise Exception("Provided bytearray of length " + str(len(into)) + " is too small for packing telemetry into. Must be at least 7 bytes.")

    # header
    into[0] = 0b00000000 # bit 0 is 0 indicates it is a telemetry packet

    # battery voltage
    # this is the integer division equivalent of converting it to a percent of the 6.0 to 16.8 range and then seeign what byte value that comes out to
    aspor:float = (vbat - 6.0) / (16.8 - 6.0) # percent of range
    vbat_asbyte:int = int(round(aspor * 255, 0))
    vbat_asbyte = min(max(vbat_asbyte, 0), 255)
    into[1] = vbat_asbyte

    # rates
    # we add 128 to "shift" from a signed byte to an unsigned byte for the sake of storage
    # that means, when unpacking this (the PC unpacks it), 128 will be subtracted out to get the signed value
    into[2] = pitch_rate + 128
    into[3] = roll_rate + 128
    into[4] = yaw_rate + 128
    into[5] = pitch_angle + 128
    into[6] = roll_angle + 128

# don't need to write a function for packing special packet
# because main.py already makes that ("send_special()")