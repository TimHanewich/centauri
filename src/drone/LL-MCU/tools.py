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
    
def shift_int8_to_uint8(val:int) -> int:
    """Does a simple 'shift' of a int8 (-128 to 127) to a uint8 (0 to 255) just by adding 128. It can later be shifted back by subtract 128. Super simple."""
    if val > 127: # 127 is upper limit of int8, beyond what we could represent with a uint8
        return 255
    elif val < -128: # -128 is lower limit of int8, beyond what we could represent with a uint8
        return 0
    else:
        return val + 128
    

##### UNPACKING DATA FROM HL-MCU #####

def unpack_settings_update(data:bytes) -> dict:

    # validate checksum
    checksum:int = data[21] # get checksum: should be the 22nd byte in (index of 21)
    selfchecksum:int = 0x00
    for byte in data[0:21]: 
        selfchecksum = selfchecksum ^ byte
    if selfchecksum != checksum: # if the checksum we calculated did not match the checksum in the data itself, must have been a transmission error. Return nothing, fail.
        return None
    
    # the first byte is a header byte, so ignore that. Assume the provided data was already validated to be a settings update packet.
    
    # unpack pitch values
    pitch_kp:float = struct.unpack("<H", data[1:3])[0] # "<H" = little-endian unsigned short
    pitch_ki:float = struct.unpack("<H", data[3:5])[0]
    pitch_kd:float = struct.unpack("<H", data[5:7])[0]

    # unpack roll values
    roll_kp:float = struct.unpack("<H", data[7:9])[0]
    roll_ki:float = struct.unpack("<H", data[9:11])[0]
    roll_kd:float = struct.unpack("<H", data[11:13])[0]

    # unpack yaw values
    yaw_kp:float = struct.unpack("<H", data[13:15])[0]
    yaw_ki:float = struct.unpack("<H", data[15:17])[0]
    yaw_kd:float = struct.unpack("<H", data[17:19])[0]

    # unpack i limit
    i_limit:float = struct.unpack("<H", data[19:21])[0]

    # return
    return {"pitch_kp": pitch_kp, "pitch_ki": pitch_ki, "pitch_kd": pitch_kd, "roll_kp": roll_kp, "roll_ki": roll_ki, "roll_kd": roll_kd, "yaw_kp": yaw_kp, "yaw_ki": yaw_ki, "yaw_kd": yaw_kd, "i_limit": i_limit}

def unpack_desired_rates(data:bytes, into:list[int]) -> bool:
    """Unpack desired rates packet into throttle, desired pitch rate, desired roll rate, and desired yaw rate, into a preexisting list. Returns True if the unpack was successful, False if it did nto unpack because of the checksum failing to verify."""

    # first, validate checksum
    selfchecksum:int = 0x00
    for i in range(9): # first 9 bytes
        selfchecksum = selfchecksum ^ data[i]
    if selfchecksum != data[9]: # the 10th byte (9th index position) is the checksum value. if the checksum we calculated did not match the checksum in the data itself, must have been a transmission error. Return nothing, fail.
        return False
    
    # unpack throttle, an unsigned short (uint16)
    into[0] = data[2] << 8 | data[1]

    # unpack pitch, roll, yaw: all signed shorts (int16)
    # we subtract 32,768 out of each one to shift it BACK to a int16 from a uint16
    # if you look at the desired rates pack function the HL-MCU has, it is shifting the int16 values into uint16 values before packing to keep it simple.
    # So we are undoing it here by shifting it back, so negatives can be preserved!
    into[1] = (data[4] << 8 | data[3]) - 32768
    into[2] = (data[6] << 8 | data[5]) - 32768
    into[3] = (data[8] << 8 | data[7]) - 32768

    # return true to indicate the unpack was successful
    return True



##### PACKING DATA TO BE SENT TO HL-MCU #####
def pack_status(m1_throttle:int, m2_throttle:int, m3_throttle:int, m4_throttle:int, pitch_rate:int, roll_rate:int, yaw_rate:int, pitch_angle:int, roll_angle:int, into:bytearray) -> None:
    """Packs status values in a preexisting bytearray, updating the first 10 bytes."""

    if len(into) < 10:
        raise Exception("Unable to pack status data into provided bytearray: it must be at least 10 bytes but the one provided is " + str(len(into)) + " in length!")

    # header byte
    into[0] = 0b00000000 # 0 in the Bit 0 position means it is a status packet

    # m1, m2, m3, m4 throttles
    # these convert from ranges of 1,000,000-2,000,00 to 0-255
    into[1] = ((m1_throttle - 1000000) * 255) // 1000000
    into[2] = ((m2_throttle - 1000000) * 255) // 1000000
    into[3] = ((m3_throttle - 1000000) * 255) // 1000000
    into[4] = ((m4_throttle - 1000000) * 255) // 1000000

    # pitch, roll, yaw rates
    into[5] = shift_int8_to_uint8(pitch_rate // 1000)
    into[6] = shift_int8_to_uint8(roll_rate // 1000)
    into[7] = shift_int8_to_uint8(yaw_rate // 1000)

    # pitch and roll angle
    into[8] = shift_int8_to_uint8(pitch_angle // 1000)
    into[9] = shift_int8_to_uint8(roll_angle // 1000)