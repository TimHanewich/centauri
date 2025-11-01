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

    # multiply i_limit by 1,000 because it is expressed in units of 1,000
    # we do this to give it a higher upper end (an i_limit of 65,535 is not nearly enough)
    # doing this gives it a total upper limit of 65,535,000
    i_limit = i_limit * 1000

    # return
    return {"pitch_kp": pitch_kp, "pitch_ki": pitch_ki, "pitch_kd": pitch_kd, "roll_kp": roll_kp, "roll_ki": roll_ki, "roll_kd": roll_kd, "yaw_kp": yaw_kp, "yaw_ki": yaw_ki, "yaw_kd": yaw_kd, "i_limit": i_limit}






##### PACKING DATA TO BE SENT TO THE CONTROLLER #####

def pack_telemetry(ticks_ms:int, vbat:int, pitch_rate:int, roll_rate:int, yaw_rate:int, input_throttle:int, input_pitch:int, input_roll:int, input_yaw:int, m1_throttle:int, m2_throttle:int, m3_throttle:int, m4_throttle:int, into:bytearray) -> None:
    """
    Packs telemetry into an existing bytearray.

    Expects:
    ticks_ms between 0 and 16,777,215 (3 bytes)
    vbat between 60 and 168 (10x higher than 6.0 and 16.8 respectively, to avoid floating point math)
    pitch_rate between -128 and 127 (signed byte)
    roll_rate between -128 and 127 (signed byte)
    yaw_rate between -128 and 127 (signed byte)
    input_throtle between 0 and 100
    input_pitch between -100 and 100
    input_roll between -100 and 100
    input_yaw between -100 and 100
    m1_throttle between 0 and 100
    m2_throttle between 0 and 100
    m3_throttle between 0 and 100
    m4_throttle between 0 and 100
    """

    # ensure the provided bytearray is big enough
    if len(into) < 15:
        raise Exception("Provided bytearray of length " + str(len(into)) + " is too small for packing telemetry into. Must be at least 15 bytes.")

    # First, prep values

    # ticks, ms
    # we do this manually by shifting the bits to the right (demoting them)
    # and then chopping off whatever is remaining beyond the 8th bit position (exceeding a byte) by doing an AND operation on 0xFF, which is 0b11111111
    # that and operation basically is our way of cutting out anything beyond 8 bits - isolating only the single byte!s
    ticks_ms_byte1:int = (ticks_ms >> 16) & 0xFF     # Most significant byte
    ticks_ms_byte2:int = (ticks_ms >> 8) & 0xFF      # middle byte
    ticks_ms_byte3:int = ticks_ms & 0xFF             # Least significant byte
    
    # battery voltage
    # first subtract 60 out of it (60 is the floor for a valid reading, 6.0 volts)
    # Plan if we were using floating point math:
    # 1. divide by the possible voltage range (16.8 - 6.0 = 10.8 volts) to get a % of total range
    # 2. then multiply by 255 to turn that to a byte, between 0-255 to express the percentage
    # Since we are using integer math, we combine both into one:
    # 1. multiply first by 255
    # 2. divide by the voltage range of 10.8, but expressed as 108 since we are using 10x units here (i.e. voltage of 6.5 is expressed as 65 in vbat)
    vbat = vbat - 60
    vbat_asbyte:int = (vbat * 255) // 108
    vbat_asbyte = min(max(vbat_asbyte, 0), 255)

    # rates
    # we add 128 to "shift" from a signed byte to an unsigned byte for the sake of storage
    # that means, when unpacking this (the PC unpacks it), 128 will be subtracted out to get the signed value
    pitch_rate_unsigned = pitch_rate + 128
    roll_rate_unsigned = roll_rate + 128
    yaw_rate_unsigned = yaw_rate + 128

    # input values
    # no need to do input throtte - it is good as is! (between 0 and 100)
    input_pitch_unsigned:int = input_pitch + 100
    input_roll_unsigned:int = input_roll + 100
    input_yaw_unsigned:int = input_yaw + 100

    # Motor throttle values
    # no need to do anything with these - they are unsigned as is!

    # now, assign values to their positions

    # ticks
    into[0] = ticks_ms_byte1
    into[1] = ticks_ms_byte2
    into[2] = ticks_ms_byte3

    # vbat
    into[3] = vbat

    # rates
    into[4] = pitch_rate_unsigned
    into[5] = roll_rate_unsigned
    into[6] = yaw_rate_unsigned

    # inputs
    into[7] = input_throttle
    into[8] = input_pitch_unsigned
    into[9] = input_roll_unsigned
    into[10] = input_yaw_unsigned

    # motor throttles
    into[11] = m1_throttle
    into[12] = m2_throttle
    into[13] = m3_throttle
    into[14] = m4_throttle

    # no need to do \r\n at the end as we assume that is already set as the last two bytes of the into byte array



        

# don't need to write a function for packing special packet
# because main.py already makes that ("send_special()")