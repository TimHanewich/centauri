### GENERAL HELPER FUNCTIONS

def shift_int16_to_uint16(val:int) -> int:
    """Does a simple 'shift' of an int16 (-32768 to 32767) to a uint16 (0 to 65535) by just adding 32768, shifting it upwards. Can later be shifted back down. Simple."""
    if val > 32767: # if exceeds bounds of upper limit of int16, return max of uint16
        return 65535
    elif val < -32768: # if lower than the lower limit of int16, return min value of uint16
        return 0
    else:
        return val + 32768

##### TO BE SENT TO REMOTE CONTROLLER

def pack_system_status(battery:float, tfluna_distance:int, tfluna_strength:int, altitude:float, heading:float) -> bytes:
    """Packs the second portion of the status packet, the portion that originates from the HL MCU, into bytes"""

    ToReturn:bytearray = bytearray()

    # header byte (metadata)
    ToReturn.append(0b00000001) # 01 for bits 0 and 1 is the packet identifier for system status

    # battery voltage
    # Fully charged 4S = 16.8v
    # Full discharged 2S = 6.0v
    # So a range of 10.8 volts, over 65,636 unique values (uint16) = ~6,068 per volt. High resolution!
    aspor:float = (battery - 6.0) / (16.8 - 6.0) # percent of range
    asint16:int = min(max(int(aspor * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # TF Luna Reading: Distance
    asint16:int = min(max(tfluna_distance, 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # TF Luna Reading: Strength
    asint16:int = min(max(tfluna_strength, 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # BMP180: Altitude, in meters
    # BMP180's min pressure reading: 300 hPa = 9,165.16 meters
    # BMP180's max pressure reading: 1,100 hPa = -698.42 meters
    # thus, the range in meters is 9,863.58
    # We are able to express that over 65,536 unique values (uint16)
    # Which would be 6.64 per meter
    aspor:float = (altitude + 698.42) / 9863.58 # percent of range
    asint16:int = min(max(int(aspor * 65535), 0), 65535)
    ToReturn.extend(asint16.to_bytes(2, "big"))

    # Heading
    # heading can be 0 to 360
    # however, since it isn't very sensitive, we will use a single byte here
    valb:int = int(round(heading * (255 / 360), 0))
    valb = min(max(valb, 0), 255)
    ToReturn.append(valb)

    return bytes(ToReturn)

def pack_special_packet(msg:str) -> bytes:
    """Packs special packet with a message to be sent to the remote controller (via HC-12). Does NOT append \r\n at the end"""

    ToReturn:bytearray = bytearray()

    # header byte
    ToReturn.append(0b00000010) # bit 0 = 0, bit 1 = 1 to declare it as a special packet

    # message
    ToUse:str = msg[0:50] # truncate to 50 characters
    ToReturn.extend(ToUse.encode())

    return bytes(ToReturn)




##### TO HELP UNPACKING DATA RECEIVED FROM CONTROLLER

def unpack_control_packet(data:bytes) -> dict:
    """Unpacks control packet data, like throttle, pitch input, and armed, angle mode, etc. Will return None if unpacked unsuccessfully (i.e. checksum failed)."""    

    # we will assume this packet is indeed a control packet
    # in other words, we will not check that the packet identifier bits of the first byte are correct
    # we will assume the code that uses this function has already verified that

    # first, validate checksum
    checksum:int = data[9] # should be last byte
    selfchecksum:int = 0b00000000 # start at 0
    for byte in data[0:9]:
        selfchecksum = selfchecksum ^ byte
    if selfchecksum != checksum: # if the checksum didn't validate, return None!
        return None

    # get armed (a single bit of the first byte)
    armed:bool = False
    if data[0] & 0b00000100 > 0: # if bit 2 is 1, that means it is armed!
        armed = True

    # get mode (a single bit of the first byte)
    # False = rate mode
    # True = angle mode
    mode:bool = False # default to rate mode
    if data[0] & 0b00001000 > 0: # if bit 3 is 1, that means it is in ANGLE mode. If not, it is in rate mode
        mode = True

    # get throttle
    as_uint16:int = int.from_bytes(data[1:3], "big")
    throttle:float = as_uint16 / 65535 # conver the throttle, stored as a uint16, into a percentage of total uint16 range

    # get pitch
    as_uint16 = int.from_bytes(data[3:5], "big")
    aspor:float = as_uint16 / 65535 # as percent of overall uint16 range (0-65535)
    pitch:float = (aspor * 2) - 1 # convert from 0.0-1.0 to -1.0 to 1.0

    # get roll
    as_uint16 = int.from_bytes(data[5:7], "big")
    aspor:float = as_uint16 / 65535 # as percent of overall uint16 range (0-65535)
    roll:float = (aspor * 2) - 1 # convert from 0.0-1.0 to -1.0 to 1.0

    # get yaw
    as_uint16 = int.from_bytes(data[7:9], "big")
    aspor:float = as_uint16 / 65535 # as percent of overall uint16 range (0-65535)
    yaw:float = (aspor * 2) - 1 # convert from 0.0-1.0 to -1.0 to 1.0

    # return
    return {"armed": armed, "mode": mode, "throttle": throttle, "pitch": pitch, "roll": roll, "yaw": yaw}


### TO BE SENT TO LL-MCU

def pack_settings_update(pitch_kp:int, pitch_ki:int, pitch_kd:int, roll_kp:int, roll_ki:int, roll_kd:int, yaw_kp:int, yaw_ki:int, yaw_kd:int, i_limit:int) -> bytes:
    """Packs settings for LL-MCU into bytes, ready to be delivered to LL-MCU via UART."""

    ToReturn:bytearray = bytearray()

    # header byte (metadata)
    ToReturn.append(0b00000000) # 0 in the Bit 0 position (farthest to right) as packet identifier

    # Pitch values
    ToReturn.extend(pitch_kp.to_bytes(2, "little"))
    ToReturn.extend(pitch_ki.to_bytes(2, "little"))
    ToReturn.extend(pitch_kd.to_bytes(2, "little"))

    # Roll values
    ToReturn.extend(roll_kp.to_bytes(2, "little"))
    ToReturn.extend(roll_ki.to_bytes(2, "little"))
    ToReturn.extend(roll_kd.to_bytes(2, "little"))

    # Yaw values
    ToReturn.extend(yaw_kp.to_bytes(2, "little"))
    ToReturn.extend(yaw_ki.to_bytes(2, "little"))
    ToReturn.extend(yaw_kd.to_bytes(2, "little"))

    # i limit
    ToReturn.extend(i_limit.to_bytes(2, "little"))

    # XOR-chain based checksum:
    checksum:int = 0x00 # start with 0
    for byte in ToReturn:
        checksum = checksum ^ byte # XOR operation
    ToReturn.append(checksum)

    return bytes(ToReturn)

def pack_desired_rates(throttle_uint16:int, pitch_int16:int, roll_int16:int, yaw_int16:int) -> bytes:

    ToReturn:bytearray = bytearray()

    # header byte
    ToReturn.append(0b00000001) # 1 is the packet identifier

    # pack throttle, pitch, roll, yaw
    ToReturn.extend(throttle_uint16.to_bytes(2, "little"))
    ToReturn.extend(shift_int16_to_uint16(pitch_int16).to_bytes(2, "little"))
    ToReturn.extend(shift_int16_to_uint16(roll_int16).to_bytes(2, "little"))
    ToReturn.extend(shift_int16_to_uint16(yaw_int16).to_bytes(2, "little"))
    
    # XOR-chain based checksum:
    checksum:int = 0x00 # start with 0
    for byte in ToReturn:
        checksum = checksum ^ byte # XOR operation
    ToReturn.append(checksum)

    return bytes(ToReturn)