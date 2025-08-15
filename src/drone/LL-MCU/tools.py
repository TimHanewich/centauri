import struct
import machine

### GENERAL TOOLS #####

def readuntil(uart:machine.UART, until:bytes = "\r\n".encode()) -> bytes:
    """Reads from a UART interface until a certain sequence is seen. I had to make this because the uart.readline() does not ONLY look for \r\n... \n on its own will do it too, which can occasionally show up in real data!"""
    ToReturn:bytearray = bytearray()
    while True:
        if uart.any():
            ToReturn = ToReturn.append(uart.read(1)[0])
            if ToReturn.endswith(until):
                return ToReturn
            
def signed_to_byte(val:int) -> int:
    """Converts an integer between -128 to 127 to a signed byte value (i.e. -4 would be 252)"""
    if val < 0:
        return 256 + val
    else:
        return val

##### UNPACKING DATA FROM HL-MCU #####

def unpack_settings_update(data:bytes) -> dict:

    # validate checksum
    checksum:int = data[41] # get checksum: should be the 42nd byte in, which would be index 41
    selfchecksum:int = 0x00
    for byte in data[0:41]: # first 41 bytes (not including checksum)
        selfchecksum = selfchecksum ^ byte
    if selfchecksum != checksum: # if the checksum we calculated did not match the checksum in the data itself, must have been a transmission error. Return nothing, fail.
        return None
    
    # the first byte is a header byte, so ignore that. Assume the provided data was already validated to be a settings update packet.
    
    # unpack pitch values
    pitch_kp:float = struct.unpack("f", data[1:5])[0]
    pitch_ki:float = struct.unpack("f", data[5:9])[0]
    pitch_kd:float = struct.unpack("f", data[9:13])[0]

    # unpack roll values
    roll_kp:float = struct.unpack("f", data[13:17])[0]
    roll_ki:float = struct.unpack("f", data[17:21])[0]
    roll_kd:float = struct.unpack("f", data[21:25])[0]

    # unpack yaw values
    yaw_kp:float = struct.unpack("f", data[25:29])[0]
    yaw_ki:float = struct.unpack("f", data[29:33])[0]
    yaw_kd:float = struct.unpack("f", data[33:37])[0]

    # unpack i limit
    i_limit:float = struct.unpack("f", data[37:41])[0]

    # return
    return {"pitch_kp": pitch_kp, "pitch_ki": pitch_ki, "pitch_kd": pitch_kd, "roll_kp": roll_kp, "roll_ki": roll_ki, "roll_kd": roll_kd, "yaw_kp": yaw_kp, "yaw_ki": yaw_ki, "yaw_kd": yaw_kd, "i_limit": i_limit}

def unpack_desired_rates(data:bytes, into:list[int, int, int, int]) -> bool:
    """Unpack desired rates packet into throttle, desired pitch rate, desired roll rate, and desired yaw rate, into a preexisting list. Returns True if the unpack was successful, False if it did nto unpack because of the checksum failing to verify."""

    # first, validate checksum
    checksum:int = data[9] # it will be the 10th byte, so 9th index position
    selfchecksum:int = 0x00
    for byte in data[0:9]: # first 9 bytes, excluding the checksum
        selfchecksum = selfchecksum ^ byte
    if selfchecksum != checksum: # if the checksum we calculated did not match the checksum in the data itself, must have been a transmission error. Return nothing, fail.
        return False

    # unpack throttle, an unsigned short (2-byte int)
    into[0] = struct.unpack("<H", data[1:3])[0]

    # unpack pitch, roll, yaw: all signed shorts (2-byte int)
    into[1] = struct.unpack("<h", data[3:5])[0] # pitch_int16
    into[2] = struct.unpack("<h", data[5:7])[0] # roll_int16
    into[3] = struct.unpack("<h", data[7:9])[0] # yaw_int16

    # return True to indicate the unpack was successful
    return True



##### PACKING DATA TO BE SENT TO HL-MCU #####
def pack_status(m1_throttle:float, m2_throttle:float, m3_throttle:float, m4_throttle:float, pitch_rate:float, roll_rate:float, yaw_rate:float, pitch_angle:float, roll_angle:float, into:bytearray) -> None:
    """Packs status values in a preexisting bytearray, updating the first 10 bytes."""

    if len(into) < 10:
        raise Exception("Unable to pack status data into provided bytearray: it must be 10 bytes but the one provided is " + str(len(into)) + " in length!")

    # header byte
    into[0] = 0b00000000 # 0 in the Bit 0 position means it is a status packet

    # m1, m2, m3, m4 throttles
    into[1] = int(m1_throttle * 255)
    into[2] = int(m2_throttle * 255)
    into[3] = int(m3_throttle * 255)
    into[4] = int(m4_throttle * 255)

    # pitch, roll, yaw rates
    into[5] = signed_to_byte(min(max(int(pitch_rate), -128), 127))
    into[6] = signed_to_byte(min(max(int(roll_rate), -128), 127))
    into[7] = signed_to_byte(min(max(int(yaw_rate), -128), 127))

    # pitch and roll angle
    into[8] = signed_to_byte(min(max(int(pitch_angle), -128), 127))
    into[9] = signed_to_byte(min(max(int(roll_angle), -128), 127))