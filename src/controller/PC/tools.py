### PACKING DATA TO SEND TO DRONE (through transceiver)

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

    # Add XOR-chain-based checksum
    checksum:int = 0x00 # start with 0
    for byte in ToReturn: # for each byte added so far
        checksum = checksum ^ byte # XOR operation
    ToReturn.append(checksum)

    # return it
    return bytes(ToReturn)



######### UNPACKING DATA FROM THE DRONE ########

def unpack_telemetry(data:bytes) -> dict:
    """Unpacks telemetry packet coming from the drone"""

    # the first byte is a header (metadata) byte

    # battery voltage
    vbat:float = 6.0 + ((16.8 - 6.0) * (data[1] / 255))

    # others
    # we subtract 128 here to "shift back" to a signed byte from an unsigned byte (128 is added before packing it)
    pitch_rate:int = data[2] - 128
    roll_rate:int = data[3] - 128
    yaw_rate:int = data[4] - 128
    pitch_angle:int = data[5] - 128
    roll_angle:int = data[6] - 128

    # return
    ToReturn:dict = {"vbat": vbat, "pitch_rate": pitch_rate, "roll_rate": roll_rate, "yaw_rate": yaw_rate, "pitch_angle": pitch_angle, "roll_angle": roll_angle}
    return ToReturn

def unpack_special_packet(data:bytes) -> str:
    """Unpacks a special packet, containing free text"""

    # the first byte is a header, so we can ignore

    # determine how far to go in
    EndOn:int = len(data)
    if data.endswith("\r\n".encode()):
        EndOn = EndOn - 2
    
    trb:bytes = data[1:EndOn]
    ToReturn:str = trb.decode(errors="replace") # transmission errors will be replaced with "�"
    return ToReturn