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

def pack_telemetry(ticks_ms:int, vbat:int, pitch_rate:int, roll_rate:int, yaw_rate:int, pitch_angle:int, roll_angle:int, gforce:int, input_throttle:int, input_pitch:int, input_roll:int, input_yaw:int, m1_throttle:int, m2_throttle:int, m3_throttle:int, m4_throttle:int, lrecv_ago_ms:int, into:bytearray) -> None:
    """
    Packs telemetry into an existing bytearray.

    Expects:
    ticks_ms between 0 and 16,777,215 (3 bytes)

    VALUES THAT WILL ALSO BE SENT OVER HC-12
    vbat between 60 and 168 (10x higher than 6.0 and 16.8 respectively, to avoid floating point math)
    pitch_rate between -128 and 127 (signed byte)
    roll_rate between -128 and 127 (signed byte)
    yaw_rate between -128 and 127 (signed byte)
    pitch_angle between -128 and 127 (signed byte)... though anything beyond -90 to 90 should be impossible
    roll_angle between -128 and 127 (signed byte)... though anything beyond -90 to 90 should be impossible

    VALUES COLLECTED ONLY FOR ON-MCU TELEMETRY LOGGING
    gforce between 0 and 255 - i.e. 10 would be 1.0g, 14 would be 1.4g, 8 would be 0.8g, etc.
    input_throttle between 0 and 100
    input_pitch between -100 and 100
    input_roll between -100 and 100
    input_yaw between -100 and 100
    m1_throttle between 0 and 100
    m2_throttle between 0 and 100
    m3_throttle between 0 and 100
    m4_throttle between 0 and 100
    lrecv_ago_ms between 0 and 2,550 (max is 2,550 ms) - this is meant to track how long ago, in ms, a command packet was recevied
    """

    # ensure the provided bytearray is big enough
    if len(into) < 19:
        raise Exception("Provided bytearray of length " + str(len(into)) + " is too small for packing telemetry into. Must be at least 19 bytes.")

    # First, prep values

    # ticks, ms
    # we do this manually by shifting the bits to the right (demoting them)
    # and then chopping off whatever is remaining beyond the 8th bit position (exceeding a byte) by doing an AND operation on 0xFF, which is 0b11111111
    # that and operation basically is our way of cutting out anything beyond 8 bits - isolating only the single byte!s
    ticks_ms_byte1:int = (ticks_ms >> 16) & 0xFF     # Most significant byte
    ticks_ms_byte2:int = (ticks_ms >> 8) & 0xFF      # middle byte
    ticks_ms_byte3:int = ticks_ms & 0xFF             # Least significant byte
    
    # battery voltage
    # we just supply this directly as the byte it came in as
    # i.e. 60 would be 6.0 volts and 168 would be 16.8 volts - just supply it as is!
    # however, let's min/max it within byte constraints to be safe
    if vbat < 0:
        vbat = 0
    elif vbat > 255:
        vbat = 255

    # rates
    # we add 128 to "shift" from a signed byte to an unsigned byte for the sake of storage
    # that means, when unpacking this (the PC unpacks it), 128 will be subtracted out to get the signed value
    pitch_rate_unsigned = pitch_rate + 128
    roll_rate_unsigned = roll_rate + 128
    yaw_rate_unsigned = yaw_rate + 128

    # angles
    # we add 128 to "shift" from a signed byte to an unsigned byte for the sake of storage
    # that means, when unpacking this (the PC unpacks it), 128 will be subtracted out to get the signed value
    pitch_angle_unsigned = pitch_angle + 128
    roll_angle_unsigned = roll_angle + 128

    # input values
    # no need to do input throtte - it is good as is! (between 0 and 100)
    input_pitch_unsigned:int = input_pitch + 100
    input_roll_unsigned:int = input_roll + 100
    input_yaw_unsigned:int = input_yaw + 100

    # Motor throttle values
    # no need to do anything with these - they are unsigned as is!

    # last recv, in ms
    # but we will "encode" it as ms, in units of 10. 
    # so a value of 1 would be 10 ms, a value of 8 would be 80 ms, a value of 123 would be 1,230 ms, etc.
    # by doing this, this enables us to express 2,550 ms (over two seconds)
    if lrecv_ago_ms < 0:
        lrecv_ago_ms = 0
    elif lrecv_ago_ms > 2550:
        lrecv_ago_ms = 2550
    lrecv_ago_byte:int = (lrecv_ago_ms + 5) // 10       # add 5 so the integer divison will round up if needed

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

    # angles
    into[7] = pitch_angle_unsigned
    into[8] = roll_angle_unsigned

    # gforce
    into[9] = gforce

    # inputs
    into[10] = input_throttle
    into[11] = input_pitch_unsigned
    into[12] = input_roll_unsigned
    into[13] = input_yaw_unsigned

    # motor throttles
    into[14] = m1_throttle
    into[15] = m2_throttle
    into[16] = m3_throttle
    into[17] = m4_throttle

    # last recv
    into[18] = lrecv_ago_byte

    # no need to do \r\n at the end as we assume that is already set as the last two bytes of the into byte array

# don't need to write a function for packing special packet
# because main.py already makes that ("send_special()")





##### TRIGONOMETRY APPROXIMATION FUNCTIONS #####
# We use this instead of using the "math" module because:
# A) the math module uses floating point math
# B) the math module always allocates memory using math.atan2 and math.sqrt, which we want to avoid (to avoid garbage collection)
# I'll be honest - I did NOT write these. These were written by GPT-5 via Copilot and I understand little about them... trig is complicated.
# The viper emitters speed it up significantly

# Integer-based Square Root Estimator
# uses Neton's method
@micropython.viper
def isqrt(x: int) -> int:
    if x <= 0:
        return 0
    r = x
    while True:
        new_r = (r + x // r) // 2
        if new_r >= r:
            return r
        r = new_r

# atan2 estimator (integer math)
@micropython.viper
def iatan2(y:int, x:int) -> int:
    # constants scaled by 1000
    PI     = 3141   # ~π * 1000
    PI_2   = 1571   # ~π/2 * 1000
    PI_4   = 785    # ~π/4 * 1000

    if x == 0:
        return PI_2 if y > 0 else -PI_2 if y < 0 else 0

    # calculate abs y
    abs_y = y
    if abs_y < 0:
        abs_y = abs_y * -1

    # calculate abs x
    abs_x = x
    if abs_x < 0:
        abs_x = abs_x * -1

    angle = 0

    if abs_x >= abs_y:
        # slope = y/x
        slope = (abs_y * 1000) // abs_x
        # polynomial approx of atan(slope)
        angle = (PI_4 * slope) // 1000
    else:
        # slope = x/y
        slope = (abs_x * 1000) // abs_y
        angle = (PI_2 - (PI_4 * slope) // 1000)

    # adjust quadrant
    if x < 0:
        if y >= 0:
            angle = PI - angle
        else:
            angle = -PI + angle
    else:
        if y < 0:
            angle = -angle

    return angle