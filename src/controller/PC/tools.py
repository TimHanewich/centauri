def shift_uint8_to_int8(byte:int) -> int:
    """Shifts a value that was stored as a uint8 (0-255) to a int8 (-128 to 127)."""
    return byte - 128

def pack_control_packet(armed:bool, mode:bool, throttle:float, pitch:float, roll:float, yaw:float) -> bytes:
    """Packs a control packet, including the '\r\n' at the end"""

    ToReturn:bytearray = bytearray()

    # Add header byte (metadata byte)
    # bit 7, 6, 5, 4 are reserved (unused)
    header:int = 0b00000000 # start with 0
    header = header | 0b00000001 # set up pack identifier to 1, a control packet
    if armed: header = header | 0b00000100 # if armed, make the 3rd bit 1. Otherwise, if unarmed, leave it as 0
    if mode: header = header | 0b00001000 # if in angle mode, set the 4th bit to 1. Othewise, if in rate mode, leave it as 0
    ToReturn.append(header)

    # Add throttle bytes
    asint16:int = min(max(int(throttle * 65535), 0), 65535) # express as number between 0 and 65535
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add pitch bytes
    aspop:float = (pitch + 1) / 2 # as percent of range
    asint16:int = min(max(int(aspop * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add roll bytes
    aspop:float = (roll + 1) / 2 # as percent of range
    asint16:int = min(max(int(aspop * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # add yaw bytes
    aspop:float = (yaw + 1) / 2 # as percent of range
    asint16:int = min(max(int(aspop * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # Add XOR-chain-based checksum
    checksum:int = 0x00 # start with 0
    for byte in ToReturn: # for each byte added so far
        checksum = checksum ^ byte # XOR operation
    ToReturn.append(checksum)
    print("Checksum: " + str(checksum))

    # append \r\n
    ToReturn.extend("\r\n".encode())

    # return it
    return bytes(ToReturn)

def unpack_control_status(data:bytes) -> dict:
    """Unpack status packet received from LL-MCU."""

    # ensure it is long enough. And if it isn't, return None
    if len(data) < 10:
        return None

    # we will skip the first byte, the header byte, for now, and assume this is indeed a status packet (that should be checked before this function is used)

    # throttles, as float
    # throttles are expressed as a single byte, from 0-255, with that range representing throttle range 0-100%
    m1_throttle:float = data[1] / 255
    m2_throttle:float = data[2] / 255
    m3_throttle:float = data[3] / 255
    m4_throttle:float = data[4] / 255

    # pitch, roll, yaw rates
    # they are stored as a uint8 that will be shifted to a int8
    # and that int8 value can be interpreted literally... i.e. a value of -6 would mean -6 degrees per second
    # (yes that loses some fidelity of decimal points)
    pitch_rate:int = shift_uint8_to_int8(data[5])
    roll_rate:int = shift_uint8_to_int8(data[6])
    yaw_rate:int = shift_uint8_to_int8(data[7])

    # pitch and roll angle
    # they are stored as a uint8 that will be shifted to a int8
    # and that int8 value can be interpreted literally... i.e. a value of -6 would mean -6 degrees
    # (yes that loses some fidelity of decimal points)
    pitch_angle:int = shift_uint8_to_int8(data[8])
    roll_angle:int = shift_uint8_to_int8(data[9])

    # return dict
    return {"m1_throttle": m1_throttle, "m2_throttle": m2_throttle, "m3_throttle": m3_throttle, "m4_throttle": m4_throttle, "pitch_rate": pitch_rate, "roll_rate": roll_rate, "yaw_rate": yaw_rate, "pitch_angle": pitch_angle, "roll_angle": roll_angle}

