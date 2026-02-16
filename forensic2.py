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

REAL_THROTTE_MAX:float = 0.39
REAL_THROTTLE_MIN:float = 0.29
input_throttle_max:float = 1.00
input_throttle_min:float = 0.98
input_pitch_max:float = -0.31
input_pitch_min:float = -0.33

percent_step:float = 0.0000001
steps_REAL_THROTTLE:int = int((REAL_THROTTE_MAX - REAL_THROTTLE_MIN) / percent_step)
steps_throttle:int = int((input_throttle_max - input_throttle_min) / percent_step)
steps_pitch:int = int(abs(input_pitch_max - input_pitch_min) / percent_step)

# collect
successes:list[tuple[int, int, int, int]] = [] # [throttle1, throttle2, pitch1, pitch2]
for i_REAL in range(steps_REAL_THROTTLE):
    for i_throttle in range(steps_throttle):
        for i_pitch in range(steps_pitch):

            # get values
            REAL_THROTTLE:float = REAL_THROTTLE_MIN + (percent_step * i_REAL)
            throttle:float = input_throttle_min + (percent_step * i_throttle)
            pitch:float = input_pitch_min + (percent_step * i_pitch)

            # construct a realist "REAL" paket of what it probably actually was
            REAL:bytearray = bytearray(pack_control_packet(REAL_THROTTLE, 0.0, 0.0, 0.0))

            # pack the "bad one"
            data = pack_control_packet(throttle, pitch, 0.0, 0.0)

            # put the "bad one" bytes into the "real" one in the corrupted positions
            REAL[1] = data[1]
            REAL[2] = data[2]
            REAL[3] = data[3]
            REAL[4] = data[4]

            # does it unpack?
            REAL = bytes(REAL)
            unpack_into:list = [0, 0, 0, 0]
            successful:bool = unpack_control_packet(REAL, unpack_into)
            if successful:

                # this tuplie
                thistuple = (REAL[1], REAL[2], REAL[3], REAL[4])

                if thistuple not in successes:
                    print("Found one that would match " + str(round(REAL_THROTTLE * 100, 1)) + "% ACTUAL throttle, all else 0%: " + str(thistuple) + " (" + str(round(throttle * 100, 1)) + "% throttle, " + str(round(pitch * 100, 1)) + " % pitch)")
                    successes.append(thistuple)
