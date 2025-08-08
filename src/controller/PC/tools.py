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
        checksum = checksum ^ byte
    ToReturn.append(checksum)
    print("Checksum: " + str(checksum))

    # append \r\n
    ToReturn.extend("\r\n".encode())

    # return it
    return bytes(ToReturn)